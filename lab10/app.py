from flask import Flask, render_template, request, jsonify, send_file
import io
import agents

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        arrival_rate = float(data.get('lambda', 0))
        service_rate = float(data.get('mu', 0))
        num_servers = int(data.get('n', 0))
        max_queue_size = int(data.get('queue_size', 0))
        max_patience = float(data.get('patience', 0))
        duration = float(data.get('t', 0))
        vip_prob = float(data.get('vip_prob', 0))

        if arrival_rate <= 0 or service_rate <= 0 or num_servers <= 0 or max_queue_size < 0 or max_patience <= 0 or duration <= 0:
            return jsonify({'error': 'Все параметры должны быть положительными.'}), 400
        if not (0 <= vip_prob <= 1):
            return jsonify({'error': 'Вероятность VIP должна быть в диапазоне [0, 1].'}), 400

        system = agents.QueueingSystem(
            num_servers=num_servers, max_queue_size=max_queue_size,
            arrival_rate=arrival_rate, service_rate=service_rate,
            max_patience=max_patience, duration=duration, vip_prob=vip_prob
        )
        system.run()

        total_arrivals = system.stats['total_arrivals'] if system.stats['total_arrivals'] > 0 else 1
        
        results = {
            'time_points': system.time_points,
            'busy_servers': system.busy_servers_series,
            'queue_length': system.queue_length_series,
            'stats': {
                'total_arrivals': system.stats['total_arrivals'],
                'total_served': system.stats['total_served'],
                'total_refused': system.stats['total_refused'],
                'total_impatient': system.stats['total_impatient'],
                'avg_wait_time': system.stats['total_wait_time'] / system.stats['total_served'] if system.stats['total_served'] > 0 else 0,
                'avg_service_time': system.stats['total_service_time'] / system.stats['total_served'] if system.stats['total_served'] > 0 else 0,
                'prop_served': system.stats['total_served'] / total_arrivals,
                'prop_refused': system.stats['total_refused'] / total_arrivals,
                'prop_impatient': system.stats['total_impatient'] / total_arrivals,
            },
            'log': system.log_entries
        }
        return jsonify({'status': 'ok', 'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export', methods=['POST'])
def export():
    try:
        data = request.json
        output = io.StringIO()
        output.write("=== Лабораторная работа 10: СМО M/M/n с усложнениями ===\n\n")
        output.write("Параметры:\n")
        output.write(f"  λ (прибытие) = {data.get('lambda')}\n")
        output.write(f"  μ (обслуживание) = {data.get('mu')}\n")
        output.write(f"  n (серверы) = {data.get('n')}\n")
        output.write(f"  Макс. размер очереди = {data.get('queue_size')}\n")
        output.write(f"  Макс. терпение = {data.get('patience')}\n")
        output.write(f"  Вероятность VIP = {data.get('vip_prob')}\n")
        output.write(f"  Длительность T = {data.get('t')}\n\n")
        
        stats = data.get('stats', {})
        output.write("Результаты:\n")
        output.write(f"  Всего заявок: {stats.get('total_arrivals')}\n")
        output.write(f"  Обслужено: {stats.get('total_served')}\n")
        output.write(f"  Отказы (очередь полна): {stats.get('total_refused')}\n")
        output.write(f"  Нетерпеливые: {stats.get('total_impatient')}\n")
        output.write(f"  Ср. время ожидания: {stats.get('avg_wait_time', 0):.4f}\n")
        output.write(f"  Ср. время обслуживания: {stats.get('avg_service_time', 0):.4f}\n\n")
        
        output.write("Доли:\n")
        output.write(f"  Обслужено: {stats.get('prop_served', 0):.4f}\n")
        output.write(f"  Отказы: {stats.get('prop_refused', 0):.4f}\n")
        output.write(f"  Нетерпеливые: {stats.get('prop_impatient', 0):.4f}\n\n")
        
        output.write("Лог событий:\n")
        for entry in data.get('log', []):
            output.write(f"{entry}\n")
            
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        
        return send_file(
            mem, mimetype='text/plain', as_attachment=True,
            download_name=f"lab10_report_n{data.get('n')}_vip{data.get('vip_prob')}_T{data.get('t')}.txt"
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)