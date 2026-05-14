import eventlet
eventlet.monkey_patch()

import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import os

np.random.seed(1984)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

sim_sessions = {}

STATE_LABELS = {1: 'Ясно', 2: 'Облачно', 3: 'Пасмурно'}

def compute_stationary(Q):
    """Вычисление стационарного распределения из матрицы интенсивностей Q."""
    n = Q.shape[0]
    A = np.vstack([Q.T, np.ones(n)])
    b = np.zeros(n + 1)
    b[-1] = 1
    pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    return pi

def run_simulation(session_id, Q, n_days, speed, initial_state):
    """Имитационное моделирование непрерывной цепи Маркова. Генерирует последовательность состояний по дням."""
    n_states = Q.shape[0]
    diag = -np.diag(Q)
    theoretical_mean_times = np.where(diag > 0, 1.0 / diag, np.inf)
    if np.any(diag < 0):
        emit('error', {'message': 'Диагональные элементы должны быть неположительными, проверьте матрицу.'})
        return

    current_state = initial_state
    visit_counts = np.zeros(n_states)
    visit_counts[current_state - 1] = 1
    t = 0.0
    next_time = t + np.random.exponential(scale=1.0/diag[current_state-1]) if diag[current_state-1] > 0 else np.inf

    state_history = []
    times_history = []
    day = 0
    total_time_in_state = np.zeros(n_states)

    day_step = 1

    socketio.emit('state_change', {
    'time': 0.0,
    'state': int(current_state),
    'label': STATE_LABELS[int(current_state)]}, room=session_id)

    while day < n_days:
        while t < day + day_step:
            if next_time > day + day_step:
                time_in_day = (day + 1) - t
                total_time_in_state[current_state-1] += time_in_day
                t = day + day_step
                break
            else:
                delta = next_time - t
                total_time_in_state[current_state-1] += delta
                t = next_time
                # Выбор следующего состояния
                if diag[current_state-1] == 0: # поглощающее состояние
                    next_time = np.inf
                    continue
                probs = Q[current_state-1, :] / diag[current_state-1]
                probs[current_state-1] = 0
                probs /= probs.sum()
                current_state = int(np.random.choice(range(1, n_states+1), p=probs))
                socketio.emit('state_change', {
                'time': float(t),
                'state': int(current_state),
                'label': STATE_LABELS[int(current_state)]}, room=session_id)
                visit_counts[current_state - 1] += 1
                # Генерация времени до следующего перехода
                next_time = t + np.random.exponential(scale=1.0/diag[current_state-1]) if diag[current_state-1] > 0 else np.inf

                state_history.append(current_state)
                times_history.append(next_time)
        # Отправка на клиент для визуализации
        # socketio.emit('new_day', {'day': float(day + day_step),
        #                           'state': int(current_state),
        #                           'label': STATE_LABELS[int(current_state)]}, room=session_id)

        day += day_step
        socketio.sleep(speed)

        mean_times = total_time_in_state / np.maximum(visit_counts, 1)

    # Эмпирическое распределение по времени
    empirical_pi = total_time_in_state / total_time_in_state.sum()
    theoretical_pi = compute_stationary(Q)

    # Формирование DataFrame для сохранения
    df_log = pd.DataFrame({'День': times_history,
                           'Состояние': state_history})
    df_log['Погода'] = df_log['Состояние'].map(STATE_LABELS)
    filename = f'weather_simulation.csv'
    filepath = os.path.join('downloads', filename)
    os.makedirs('downloads', exist_ok=True)
    df_log.to_csv(filepath, index=False)

    socketio.emit('state_change', {
        'time': float(n_days),
        'state': int(current_state),
        'label': STATE_LABELS[int(current_state)]
    }, room=session_id)

    # Отправка итогов
    socketio.emit('simulation_done', {'empirical': empirical_pi.tolist(),
                                      'theoretical': theoretical_pi.tolist(),
                                      'mean_times': mean_times.tolist(),
                                      'theoretical_mean_times': theoretical_mean_times.tolist(),
                                      'file': filename}, room=session_id)

    sim_sessions[session_id]['finished'] = True
    sim_sessions[session_id]['empirical'] = empirical_pi.tolist()
    sim_sessions[session_id]['theoretical'] = theoretical_pi.tolist()
    sim_sessions[session_id]['file'] = filename

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    session_id = str(uuid.uuid4())
    sim_sessions[session_id] = {'finished': False}
    join_room(session_id)
    emit('session_id', {'session_id': session_id})

@socketio.on('start_simulation')
def handle_start(data):
    session_id = data.get('session_id')
    if not session_id or session_id not in sim_sessions:
        emit('error', {'message': 'Недействительная сессия, обновите страницу.'})
        return

    # Извлечение параметров
    try:
        n_days = int(data.get('n_days', 100))
        speed = float(data.get('speed', 0.2))
        # Матрица интенсивностей
        Q_list = data.get('Q')
        if Q_list is None or len(Q_list) != 3:
            raise ValueError('Матрица не 3x3')
        Q = np.array(Q_list, dtype=float)
        # Проверка корректности: строки должны суммироваться в 0 (с допустимой погрешностью)
        row_sums = Q.sum(axis=1)
        if not np.allclose(row_sums, np.zeros(3), atol=1e-6):
            emit('error', {'message': 'Сумма элементов в каждой строке должна быть равна 0. Проверьте матрицу.'})
            return
        # Дополнительно: Q_ij >= 0 для i!=j
        for i in range(3):
            for j in range(3):
                if i != j and Q[i, j] < 0:
                    emit('error', {'message': 'Внедиагональные элементы должны быть неотрицательными.'})
                    return
        if np.any(np.diag(Q) > 0):
            emit('error', {'message': 'Диагональные элементы должны быть <= 0.'})
            return

        # Теоретическое стационарное распределение
        pi_theor = compute_stationary(Q)
        init_state = int(np.argmax(pi_theor) + 1) # состояние с наибольшей вероятностью

        socketio.start_background_task(run_simulation, session_id, Q, n_days, speed, init_state)
        emit('simulation_started', {'initial_state': init_state,
                                    'state_label': STATE_LABELS[init_state],
                                    'stationary': pi_theor.tolist()})
    except Exception as e:
        emit('error', {'message': f'Ошибка: {str(e)}'})

@socketio.on('disconnect')
def handle_disconnect():
    pass

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)