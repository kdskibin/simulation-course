import math
import random
import numpy as np
import logging
from flask import Flask, render_template, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

app = Flask(__name__)

def simulate_poisson(lambda_, T, N):
    """
    Моделирование пуассоновского потока: N экспериментов.
    Возвращает словарь с результатами и данными для графика.
    """
    counts = {}
    all_counts = []
    for _ in range(N):
        count = 0
        time = 0.0
        while time < T:
            u = max(random.random(), 1e-10)
            inter_arrival = -math.log(u) / lambda_
            time += inter_arrival
            if time <= T:
                count += 1
        all_counts.append(count)
        counts[count] = counts.get(count, 0) + 1

    # Эмпирические характеристики
    emp_mean = np.mean(all_counts)
    emp_var = np.var(all_counts)

    # Теоретические характеристики
    theo_lambda_T = lambda_ * T
    theo_mean = theo_lambda_T
    theo_var = theo_lambda_T

    # Теоретическое распределение Пуассона
    max_k = max(counts.keys()) if counts else 0
    logging.info(f"max_k: {max_k}")
    # max_theoretical_k = max(max_k + 10, int(np.sqrt(theo_lambda_T) * 3))
    # logging.info(f"max_theoretical_k: {max_theoretical_k}")
    # theo_dist = {}
    # pk = math.exp(-theo_lambda_T)
    # theo_dist[0] = pk
    # for k in range(1, max_theoretical_k + 1):
    #     pk *= theo_lambda_T / k
    #     theo_dist[k] = pk
    # logging.info(f"len(theo_dist.keys()): {len(theo_dist.keys())}")
    # logging.info(f"len(theo_dist.keys()): {len(theo_dist.keys())}")

    max_theoretical_k = max(max_k + 10, int(theo_lambda_T * 3))

    theo_dist = {}
    if theo_lambda_T == 0:
        theo_dist[0] = 1.0
    else:
        # Мода распределения Пуассона
        mode = int(theo_lambda_T)  # можно также округлить
        # ln(P(mode)) = mode*ln(λT) - λT - ln(mode!)
        log_p_mode = mode * math.log(theo_lambda_T) - theo_lambda_T - math.lgamma(mode + 1)
        p_mode = math.exp(log_p_mode)
        
        # Правая часть (k = mode, mode+1, ...)
        pk = p_mode
        for k in range(mode, max_theoretical_k + 1):
            theo_dist[k] = pk
            pk *= theo_lambda_T / (k + 1)   # P(k+1) = P(k) * λT/(k+1)
        
        # Левая часть (k = mode-1, mode-2, ..., 0)
        pk = p_mode
        for k in range(mode - 1, -1, -1):
            pk = pk * (k + 1) / theo_lambda_T   # P(k) = P(k+1) * (k+1)/λT
            theo_dist[k] = pk

    # Относительные ошибки
    mean_error = abs(emp_mean - theo_mean) / theo_mean * 100 if theo_mean != 0 else 0
    var_error = abs(emp_var - theo_var) / theo_var * 100 if theo_var != 0 else 0
    conclusion = (
        f"Эмпирическое среднее ({emp_mean:.4f}) отличается от теоретического ({theo_mean:.4f}) на {mean_error:.2f}%.\n"
        f"Эмпирическая дисперсия ({emp_var:.4f}) отличается от теоретической ({theo_var:.4f}) на {var_error:.2f}%.\n\n"
    )

    # Топ-20 частот для таблицы
    top_freq = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:20]
    freq_table = []
    for k, cnt in top_freq:
        emp_p = cnt / N
        theo_p = theo_dist.get(k, 0.0)
        freq_table.append({
            'k': k,
            'empirical': f"{emp_p:.4f}",
            'theoretical': f"{theo_p:.4f}"
        })

    # Данные для гистограммы (бины, адаптивно)
    num_bins = 20
    center_k = int(round(theo_lambda_T))
    sigma = int(math.ceil(math.sqrt(theo_lambda_T))) if theo_lambda_T > 0 else 1
    if center_k <= 100:
        end_k = max(center_k + 4 * sigma, 20)
        start_k = 0
    else:
        end_k = center_k + 3 * sigma
        start_k = max(0, center_k - 3 * sigma)
    bin_width = (end_k - start_k) / num_bins

    emp_values = []
    theo_values = []
    labels = []
    for b in range(num_bins):
        b_start = start_k + b * bin_width
        b_end = start_k + (b + 1) * bin_width
        k_min = int(math.ceil(b_start))
        k_max = int(math.floor(b_end - 1e-12))
        if k_max < k_min:
            k_max = k_min
        emp_sum = sum(counts.get(k, 0) / N for k in range(k_min, k_max + 1))
        theo_sum = sum(theo_dist.get(k, 0) for k in range(k_min, k_max + 1))
        emp_values.append(round(emp_sum, 6))
        theo_values.append(round(theo_sum, 6))
        labels.append(f"{b_start:.1f}–{b_end:.1f}")

    return {
        'emp_mean': round(emp_mean, 4),
        'emp_var': round(emp_var, 4),
        'theo_mean': round(theo_mean, 4),
        'theo_var': round(theo_var, 4),
        'conclusion': conclusion,
        'freq_table': freq_table,
        'chart_labels': labels,
        'empirical_series': emp_values,
        'theoretical_series': theo_values,
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        lambda_ = float(request.form['lambda'])
        T = float(request.form['T'])
        N = int(request.form['N'])
        if lambda_ <= 0 or T <= 0 or N <= 0:
            return jsonify({'error': 'Все параметры должны быть положительными'}), 400
    except (ValueError, KeyError):
        return jsonify({'error': 'Некорректные параметры'}), 400

    result = simulate_poisson(lambda_, T, N)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)