import math
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        # Получение и валидация параметров
        lambda_val = float(request.form.get('lambda', 0))
        mu_val = float(request.form.get('mu', 0))
        N = int(request.form.get('N', 0))

        if lambda_val <= 0 or mu_val <= 0 or N <= 0:
            return jsonify({'error': 'Все параметры должны быть положительными.'}), 400

        rho = lambda_val / mu_val

        # Теоретические вероятности для M/M/1/0 (формула Эрланга B, n=1)
        theo_p0 = 1.0 / (1.0 + rho) # вероятность, что сервер свободен
        theo_p1 = rho / (1.0 + rho) # сервер занят
        theo_refusal = theo_p1
        theo_throughput = lambda_val * theo_p0

        accepted = 0
        refused = 0
        arrivals = []
        current_time = 0.0
        server_free_at = 0.0
        for _ in range(N):
            req_arrival = -math.log(max(random.random(), 1e-10)) / lambda_val
            current_time += req_arrival
            if current_time >= server_free_at:
                accepted += 1
                service_time = -math.log(max(random.random(), 1e-10)) / mu_val
                server_free_at = current_time + service_time
            else:
                refused += 1
            arrivals.append(current_time)

        total_time = current_time # время прихода последней заявки

        # Эмпирические вероятности
        emp_p0 = accepted / N
        emp_p1 = refused / N
        emp_refusal = emp_p1
        emp_throughput = accepted / total_time if total_time > 0 else 0

        # Формирование ответа
        results = {
            'lambda': lambda_val,
            'mu': mu_val,
            'N': N,
            'rho': round(rho, 4),
            'theoretical': {
                'p0': round(theo_p0, 4),
                'p1': round(theo_p1, 4),
                'refusal': round(theo_refusal, 4),
                'throughput': round(theo_throughput, 4)
            },
            'empirical': {
                'p0': round(emp_p0, 4),
                'p1': round(emp_p1, 4),
                'refusal': round(emp_refusal, 4),
                'throughput': round(emp_throughput, 4)
            },
            'counts': {
                'accepted': accepted,
                'refused': refused
            }
        }

        return jsonify({'status': 'ok', 'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)