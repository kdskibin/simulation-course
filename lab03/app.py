import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
from flask import Flask, request, render_template, url_for

app = Flask(__name__)

# Папка для сохранения GIF
STATIC_FOLDER = 'static'
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# Значения по умолчанию
DEFAULT_PARAMS = {
    'NEW_TREE_PROBA': 0.01,
    'START_FIRE_PROBA': 0.0001,
    'DIAGONAL_FIRE_START_PROBA': 0.5,
    'TEMPERATURE_COEFF': 1.1,
    'WIND_AFFLICTION': 0.9,
    'WIND_DIRECTION': 'sw',
    'FOREST_FRACTION': 0.2,
    'NX': 200,
    'NY': 200,
    'FRAMES': 200  # можно регулировать длительность анимации
}

def run_simulation(params):
    # Извлекаем параметры
    NEW_TREE_PROBA = params['NEW_TREE_PROBA']
    START_FIRE_PROBA = params['START_FIRE_PROBA']
    DIAGONAL_FIRE_START_PROBA = params['DIAGONAL_FIRE_START_PROBA']
    TEMPERATURE_COEFF = params['TEMPERATURE_COEFF']
    WIND_AFFLICTION = params['WIND_AFFLICTION']
    WIND_DIRECTION = params['WIND_DIRECTION']
    FOREST_FRACTION = params['FOREST_FRACTION']
    NX = params['NX']
    NY = params['NY']
    FRAMES = params.get('FRAMES', 200)

    # Константы состояний клеток
    EMPTY, TREE, FIRE, WATER = 0, 1, 2, 3

    # Направления ветра (клетки, на которые влияет ветер при пожаре)
    available_wind_directions = {
        'n':  {'x': [-1, 0, 1], 'y': [1, 1, 1]},
        's':  {'x': [-1, 0, 1], 'y': [-1, -1, -1]},
        'w':  {'x': [1, 1, 1], 'y': [-1, 0, 1]},
        'e':  {'x': [-1, -1, -1], 'y': [1, 0, -1]},
        'nw': {'x': [1, 0], 'y': [1, 0]},
        'ne': {'x': [-1, 0], 'y': [1, 0]},
        'sw': {'x': [1, 0], 'y': [-1, 0]},
        'se': {'x': [-1, 0], 'y': [-1, 0]}
    }

    # Окрестность Мура
    neighbourhood = ((-1, -1), (-1, 0), (-1, 1),(0, -1), (0, 1), (1, -1),  (1, 0),  (1, 1))

    # Инициализация возраста деревьев. Каждое дерево может быть возрастом от 1 до n лет
    FOREST_AGE = np.zeros((NY, NX))

    def compute_age_coeff(x, y):
        '''Рассчет коэффициента возгорания дерева в зависисмости от времени жизни.
        Значения будут менять от 1 до 2 в соответствии с графиком функции из класса сигмоидальных'''
        return 2 / (1 + np.exp(-FOREST_AGE[x, y]/10))

    # Функция одного шага эволюции
    def iterate(X):
        updated_X = np.zeros((NY, NX))
        for ix in range(1, NX-1):
            for iy in range(1, NY-1):
                if X[iy, ix] == WATER:
                    updated_X[iy, ix] = WATER
                    continue

                # Появление нового дерева
                if X[iy, ix] == EMPTY and np.random.random() <= NEW_TREE_PROBA:
                    updated_X[iy, ix] = TREE

                # Проверка на возгорание
                if X[iy, ix] == TREE:
                    updated_X[iy, ix] = TREE
                    FOREST_AGE[iy, ix] += 1
                    for dx, dy in neighbourhood:
                        # Диагональные соседи загораются с меньшей вероятностью
                        if abs(dx) == abs(dy) and (np.random.random() < DIAGONAL_FIRE_START_PROBA * TEMPERATURE_COEFF * compute_age_coeff(dx, dy)):
                            continue
                        if X[iy+dy, ix+dx] == FIRE:
                            updated_X[iy, ix] = FIRE if X[iy+dy, ix+dx] != WATER else FIRE
                            # Распространение ветром
                            for wx, wy in zip(available_wind_directions[WIND_DIRECTION]['x'], available_wind_directions[WIND_DIRECTION]['y']):
                                wy_clipped = np.clip(iy + wy, 1, NY-2)
                                wx_clipped = np.clip(ix + wx, 1, NX-2)
                                if (np.random.random() < DIAGONAL_FIRE_START_PROBA * TEMPERATURE_COEFF * WIND_AFFLICTION * compute_age_coeff(wx_clipped, wy_clipped)) and (X[wy_clipped, wx_clipped] != WATER):
                                    updated_X[wy_clipped, wx_clipped] = FIRE
                            break
                    else:
                        # Самовозгорание
                        if np.random.random() <= START_FIRE_PROBA * compute_age_coeff(dx, dy):
                            updated_X[iy, ix] = FIRE
        return updated_X

    # Инициализация леса
    X = np.zeros((NY, NX))
    # Внутренняя область заполняется деревьями случайно
    X[1:NY-1, 1:NX-1] = (np.random.random(size=(NY-2, NX-2)) < FOREST_FRACTION).astype(int)
    # Добавляем речку

    # Настройка цветов для визуализации
    colors_list = [(0.2, 0, 0), (0, 0.5, 0), (1, 0, 0), 'orange', 'blue']
    cmap = colors.ListedColormap(colors_list)
    bounds = [0, 1, 2, 3, 4]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    im = ax.imshow(X, cmap=cmap, norm=norm)

    def animate_func(i):
        nonlocal X
        im.set_data(X)
        X = iterate(X)

    anim = animation.FuncAnimation(fig, animate_func, frames=FRAMES, interval=100, repeat=False)

    # Уникальное имя файла
    filename = f"fire_in_the_forest_{WIND_DIRECTION}.gif"
    filepath = os.path.join(STATIC_FOLDER, filename)
    anim.save(filepath, writer='pillow')

    return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    gif_filename = None
    error = None

    if request.method == 'POST':
        try:
            # Собираем параметры из формы с преобразованием типов
            params = {}
            params['NEW_TREE_PROBA'] = float(request.form.get('NEW_TREE_PROBA', DEFAULT_PARAMS['NEW_TREE_PROBA']))
            params['START_FIRE_PROBA'] = float(request.form.get('START_FIRE_PROBA', DEFAULT_PARAMS['START_FIRE_PROBA']))
            params['DIAGONAL_FIRE_START_PROBA'] = float(request.form.get('DIAGONAL_FIRE_START_PROBA', DEFAULT_PARAMS['DIAGONAL_FIRE_START_PROBA']))
            params['TEMPERATURE_COEFF'] = float(request.form.get('TEMPERATURE_COEFF', DEFAULT_PARAMS['TEMPERATURE_COEFF']))
            params['WIND_AFFLICTION'] = float(request.form.get('WIND_AFFLICTION', DEFAULT_PARAMS['WIND_AFFLICTION']))
            params['WIND_DIRECTION'] = request.form.get('WIND_DIRECTION', DEFAULT_PARAMS['WIND_DIRECTION'])
            params['FOREST_FRACTION'] = float(request.form.get('FOREST_FRACTION', DEFAULT_PARAMS['FOREST_FRACTION']))
            params['NX'] = int(request.form.get('NX', DEFAULT_PARAMS['NX']))
            params['NY'] = int(request.form.get('NY', DEFAULT_PARAMS['NY']))
            params['FRAMES'] = int(request.form.get('FRAMES', DEFAULT_PARAMS['FRAMES']))

            # Простейшая валидация
            if not (0 <= params['NEW_TREE_PROBA'] <= 1):
                raise ValueError("NEW_TREE_PROBA должна быть в [0,1]")
            if not (0 <= params['START_FIRE_PROBA'] <= 1):
                raise ValueError("START_FIRE_PROBA должна быть в [0,1]")
            if not (0 <= params['DIAGONAL_FIRE_START_PROBA'] <= 1):
                raise ValueError("DIAGONAL_FIRE_START_PROBA должна быть в [0,1]")
            if params['TEMPERATURE_COEFF'] <= 0:
                raise ValueError("TEMPERATURE_COEFF должна быть положительной")
            if params['WIND_AFFLICTION'] < 0:
                raise ValueError("WIND_AFFLICTION не может быть отрицательной")
            if not (0 <= params['FOREST_FRACTION'] <= 1):
                raise ValueError("FOREST_FRACTION должна быть в [0,1]")
            if params['NX'] < 10 or params['NY'] < 10:
                raise ValueError("Размеры сетки должны быть не менее 10")
            if params['FRAMES'] < 1:
                raise ValueError("Количество кадров должно быть >= 1")

            # Запуск симуляции
            gif_filename = run_simulation(params)
        except Exception as e:
            error = str(e)

    return render_template('index.html', default=DEFAULT_PARAMS, gif_filename=gif_filename, error=error)

if __name__ == '__main__':
    app.run(debug=False)