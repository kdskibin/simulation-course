import math
import random
import collections
import numpy as np
from server import Server
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        # Чтение параметров
        lambda_val = float(request.form.get('lambda', 0))
        mu_val = float(request.form.get('mu', 0))
        N = int(request.form.get('N', 0))
        c = int(request.form.get('c', 1))
        p_impatient = float(request.form.get('p_impatient', 0))

        # Валидация
        if (lambda_val <= 0) or (mu_val <= 0) or (N <= 0) or (c <= 0):
            return jsonify({'error': 'lambda, mu, N должны быть > 0, c >= 1'}), 400
        if not (0 <= p_impatient <= 1):
            return jsonify({'error': 'Вероятность нетерпеливости должна быть от 0 до 1'}), 400

        rho = lambda_val / (c * mu_val)

        # Инициализация
        current_time = 0.0
        last_event_time = 0.0
        arrivals_generated = 0
        next_arrival_time = -math.log(max(random.random(), 1e-10)) / lambda_val

        # Список каналов: время освобождения, изначально все свободны (0.0)
        servers = [Server(0.0, mu_val) for _ in range(c)]
        # servers = [0.0] * c
        queue = collections.deque() # хранит времена прибытия ожидающих заявок

        accepted = 0
        refused = 0

        # Статистика: время, проведённое в каждом состоянии
        busy_time = [0.0] * (c + 1)
        queue_length_time = [0.0] # индекс = длина очереди

        waiting_times = [] # времена ожидания всех обслуженных заявок (включая 0)

        def get_busy_count(t):
            """Возвращает число занятых каналов на момент времени t"""
            return sum(1 for s in servers if s.free_at > t)

        # Основной цикл
        while (arrivals_generated < N) or queue or any(s > current_time for s in servers):
            # Определяем следующее событие
            if arrivals_generated < N:
                next_arr = next_arrival_time
            else:
                next_arr = float('inf')

            # Ближайшее освобождение
            min_dep = min((s.free_at for s in servers if s.free_at > current_time), default=float('inf'))

            next_event_time = min(next_arr, min_dep)
            if next_event_time == float('inf'):
                break

            # Накапливаем статистику за интервал [last_event_time, next_event_time)
            delta = next_event_time - last_event_time
            if delta > 0:
                bc = get_busy_count(last_event_time)
                ql = len(queue)
                busy_time[bc] += delta
                while len(queue_length_time) <= ql:
                    queue_length_time.append(0.0)
                queue_length_time[ql] += delta

            current_time = next_event_time
            last_event_time = current_time

            # Обработка события
            if next_arr <= min_dep:
                # Прибытие заявки
                arrivals_generated += 1
                if arrivals_generated < N:
                    inter = -math.log(max(random.random(), 1e-10)) / lambda_val
                    next_arrival_time = current_time + inter

                # Поиск свободного канала
                free = [i for i, end_t in enumerate(servers) if end_t <= current_time]
                if free:
                    idx = free[0]
                    service = -math.log(max(random.random(), 1e-10)) / mu_val
                    servers[idx] = current_time + service
                    accepted += 1
                    waiting_times.append(0.0)
                else:
                    # Все каналы заняты
                    if random.random() < p_impatient:
                        refused += 1
                    else:
                        queue.append(current_time)
            else:
                # Освобождение канала (может быть несколько одновременно, обрабатываем первое)
                for i, end_t in enumerate(servers):
                    if end_t == min_dep:
                        if queue:
                            arrival = queue.popleft()
                            wait = current_time - arrival
                            waiting_times.append(wait)
                            service = -math.log(max(random.random(), 1e-10)) / mu_val
                            servers[i] = current_time + service
                            accepted += 1
                        else:
                            servers[i] = 0.0  # освобождаем
                        break

        total_time = current_time

        # Расчёт эмпирических вероятностей
        busy_dist = [t / total_time for t in busy_time]
        queue_dist = [t / total_time for t in queue_length_time]

        # Гистограмма времени ожидания (только для обслуженных заявок)
        wait_hist = {"labels": [], "counts": []}
        if waiting_times:
            # Определяем число бинов по правилу Стёрджеса
            n_wait = len(waiting_times)
            if n_wait > 1:
                bins = int(1 + 3.322 * math.log10(n_wait))
            else:
                bins = 1
            max_w = max(waiting_times)
            if max_w == 0:
                bins = 1
                width = 1  # не имеет значения
            else:
                width = max_w / bins
            # Инициализация бинов
            counts = [0] * bins
            for w in waiting_times:
                idx = min(int(w // width), bins - 1)
                counts[idx] += 1
            # Генерация меток (интервалов)
            for i in range(bins):
                low = i * width
                high = (i + 1) * width if i < bins - 1 else max_w
                wait_hist["labels"].append(f"{low:.3f}-{high:.3f}")
            wait_hist["counts"] = counts

        # Пропускная способность
        throughput = accepted / total_time if total_time > 0 else 0

        results = {
            'lambda': lambda_val,
            'mu': mu_val,
            'N': N,
            'c': c,
            'p_impatient': p_impatient,
            'rho': round(rho, 4),
            'empirical': {
                'busy_distribution': [round(p, 6) for p in busy_dist],
                'mean_busy': np.mean([round(p, 6) for p in busy_dist]),
                'queue_length_distribution': [round(p, 6) for p in queue_dist],
                'mean_queue': np.mean([round(p, 6) for p in queue_dist]),
                'waiting_histogram': wait_hist,
                'mean_waits': np.mean([round(p, 6) for p in waiting_times])
            },
            'counts': {
                'accepted': accepted,
                'refused': refused
            },
            'total_time': round(total_time, 4),
            'throughput': round(throughput, 4)
        }

        return jsonify({'status': 'ok', 'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)