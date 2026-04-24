import io
import base64
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import chi2, norm
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'some_qunique_secret_key'


# Парсер распределения из строки формата "x1,p1;x2,p2;..."
def parse_distribution(text):
    pairs = text.strip().split(';')
    x_th = []
    p_th = []
    for pair in pairs:
        if ',' not in pair:
            continue
        parts = pair.split(',')
        if len(parts) >= 2:
            x_th.append(float(parts[0].strip()))
            p_th.append(float(parts[1].strip()))

    if not x_th:
        raise ValueError("Empty distribution")

    total = sum(p_th)
    if total == 0:
        raise ValueError("Sum of probabilities is zero")
    p_th = [p / total for p in p_th]
    return x_th, p_th


# Моделирование дискретной случайной величины
def simulate_discrete(x_th, p_th, N):
    cdf = np.cumsum(p_th)
    samples = []
    for _ in range(N):
        u = random.random()
        idx = next(i for i, c in enumerate(cdf) if u <= c)
        samples.append(x_th[idx])
    samples = np.array(samples)

    # Теоретические моменты
    m_th = sum(x * p for x, p in zip(x_th, p_th))
    var_th = sum((x**2) * p for x, p in zip(x_th, p_th)) - m_th**2
    s_th = np.sqrt(var_th)

    # Эмпирические моменты
    m_emp = np.mean(samples)
    s_emp = np.std(samples) # по генеральной совокупности (ddof=0)

    # Относительные погрешности
    err_m = abs(m_th - m_emp) / (abs(m_th) if m_th != 0 else 1)
    err_s = abs(s_th - s_emp) / (s_th if s_th != 0 else 1)

    # Хи-квадрат
    chi_val = 0
    for i in range(len(x_th)):
        expected = N * p_th[i]
        observed = np.sum(samples == x_th[i])
        if expected > 0:
            chi_val += (observed - expected)**2 / expected

    df = len(x_th) - 1
    critical = chi2.ppf(0.95, df)
    passed = chi_val < critical

    return {'N': N,
            'emp_mean': m_emp,
            'emp_std': s_emp,
            'rel_err_mean': err_m,
            'rel_err_std': err_s,
            'chi2': chi_val,
            'critical': critical,
            'passed': passed,
            'samples': samples}


def run_all_discrete(x_th, p_th):
    sizes = [10, 100, 1000, 10000]
    results = []
    for N in sizes:
        res = simulate_discrete(x_th, p_th, N)
        results.append(res)
    return results


# Генерация нормальной случайной величины при помощи преобразования Бокса-Мюллера
def simulate_normal(N, bins):
    samples = []
    for _ in range(N // 2):
        u1, u2 = random.random(), random.random()
        z0 = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
        z1 = np.sqrt(-2 * np.log(u1)) * np.sin(2 * np.pi * u2)
        samples.extend([z0, z1])
    if N % 2:
        u1, u2 = random.random(), random.random()
        samples.append(np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2))
    samples = np.array(samples)

    m_emp = np.mean(samples)
    s_emp = np.std(samples)
    err_m = abs(0 - m_emp)
    err_s = abs(1 - s_emp)

    observed, bin_edges = np.histogram(samples, bins=bins)
    chi_val = 0
    for i in range(bins):
        expected = N * (norm.cdf(bin_edges[i+1]) - norm.cdf(bin_edges[i]))
        if expected > 0:
            chi_val += (observed[i] - expected)**2 / expected

    df = bins - 1
    critical = chi2.ppf(0.95, df)
    passed = chi_val < critical

    return {
        'N': N,
        'mean_err': err_m,
        'std_err': err_s,
        'chi2': chi_val,
        'critical': critical,
        'passed': passed,
        'samples': samples,
        'bin_edges': bin_edges
    }


# Построение графиков
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def generate_discrete_plot(x_th, p_th, sample_10000):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0b0e14')

    ax1.bar(x_th, p_th, color='#3498db', alpha=0.7)
    ax1.set_title('Теоретическое', color='#3498db')
    ax1.set_facecolor('#151921')
    ax1.tick_params(colors='#7f8c8d')

    ax2.hist(sample_10000, bins=np.arange(min(x_th)-0.5, max(x_th)+1.5, 1),
             density=True, color='#3498db', alpha=0.7, rwidth=0.8)
    ax2.set_title('Эмперическое (N=10000)', color='#3498db')
    ax2.set_facecolor('#151921')
    ax2.tick_params(colors='#7f8c8d')

    return fig_to_base64(fig)


def generate_normal_plot(normal_results, bins):
    n = len(normal_results)
    fig, axes = plt.subplots(1, n, figsize=(5*n, 5))
    if n == 1:
        axes = [axes]
    fig.patch.set_facecolor('#0b0e14')

    for ax, res in zip(axes, normal_results):
        ax.hist(res['samples'], bins=res['bin_edges'], density=True,
                color='#e74c3c', alpha=0.6)
        x_vals = np.linspace(min(res['bin_edges']), max(res['bin_edges']), 200)
        ax.plot(x_vals, norm.pdf(x_vals), '--', color='white', linewidth=2)
        ax.set_title(f'N={res["N"]}', color='#e74c3c')
        ax.set_facecolor('#151921')
        ax.tick_params(colors='#7f8c8d')

    return fig_to_base64(fig)


# Маршруты
@app.route('/', methods=['GET', 'POST'])
def index():
    # Параметры для нормальной симуляции по умолчанию
    default_normal_n = ['100', '1000', '10000']
    default_bins = 20

    if request.method == 'POST':
        # Загрузка пресета дискретного распределения
        if 'preset_load' in request.form:
            preset = request.form.get('preset', 'uniform')
            if preset == 'uniform':
                session['dist_text'] = '1,0.2;2,0.2;3,0.2;4,0.2;5,0.2'
            elif preset == 'bernoulli':
                session['dist_text'] = '0,0.4;1,0.6'
            else:
                session['dist_text'] = '1,0.2;2,0.2;3,0.2;4,0.2;5,0.2'
            session['last_preset'] = preset
            return redirect(url_for('index'))

        # Запуск дискретной симуляции
        if 'run_discrete' in request.form:
            dist_text = request.form.get('dist_text', '')
            session['dist_text'] = dist_text
            try:
                x_th, p_th = parse_distribution(dist_text)
            except Exception as e:
                flash(f'Error parsing distribution: {e}')
                return redirect(url_for('index'))

            results = run_all_discrete(x_th, p_th)
            # Для графика используем выборку с N=10000 (последний элемент)
            plot = generate_discrete_plot(x_th, p_th, results[-1]['samples'])
            return render_template('index.html',
                                   discrete_results=results,
                                   discrete_plot=plot,
                                   selected_normal_n=default_normal_n,
                                   bins=default_bins)

        # Запуск нормальной симуляции
        if 'run_normal' in request.form:
            raw_sizes = request.form.getlist('sample_sizes')
            try:
                bins = int(request.form.get('bins', default_bins))
            except ValueError:
                bins = default_bins

            Ns = []
            for val in raw_sizes:
                try:
                    Ns.append(int(val))
                except ValueError:
                    pass
            if not Ns:
                flash('Select at least one sample size.')
                return redirect(url_for('index'))

            normal_results = []
            for N in Ns:
                res = simulate_normal(N, bins)
                normal_results.append(res)

            normal_plot = generate_normal_plot(normal_results, bins)

            # Сохраним последние выбранные опции для формы
            selected = [str(n) for n in Ns]
            return render_template('index.html',
                                   normal_results=normal_results,
                                   normal_plot=normal_plot,
                                   selected_normal_n=selected,
                                   bins=bins)

    return render_template('index.html',
                           selected_normal_n=default_normal_n,
                           bins=default_bins)


if __name__ == '__main__':
    app.run(debug=True)