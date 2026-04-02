from flask import Flask, render_template, request
from random_impl import get_binary_answer, MagicBall

from congen import MLCG

app = Flask(__name__)

magic_ball = MagicBall()
generator = MLCG(89)

@app.route('/')
def index():
    """Главная страница с ссылками на другие разделы."""
    return render_template('index.html')

@app.route('/binary', methods=['GET', 'POST'])
def binary():
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "Введите вопрос"
            return render_template('binary.html', error=error)
        answer = get_binary_answer(generator)
        return render_template('binary.html', question=question, answer=answer)
    return render_template('binary.html')

@app.route('/magicball', methods=['GET', 'POST'])
def magicball():
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "Введите вопрос"
            return render_template('magicball.html', error=error)
        answer = magic_ball.get_answer()
        return render_template('magicball.html', question=question, answer=answer)
    return render_template('magicball.html')

if __name__ == '__main__':
    app.run(debug=True)