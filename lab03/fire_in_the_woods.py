from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors

def iterate(X):
    updated_X = np.zeros((NY, NX))
    # Граница леса всегда пуста
    for ix in range(1,NX-1):
        for iy in range(1,NY-1):
            if X[iy,ix] == WATER:
                updated_X[iy,ix] = WATER
                continue
            if (X[iy,ix] == EMPTY) and (np.random.random() <= NEW_TREE_PROBA):
                updated_X[iy,ix] = TREE
            if X[iy,ix] == TREE:
                updated_X[iy,ix] = TREE
                for dx,dy in neighbourhood:
                    # Соседние по диагонали деревья находятся дальше, поэтому загораются с меньшей вероятностью:
                    if (abs(dx) == abs(dy)) and np.random.random() < DIAGONAL_FIRE_START_PROBA*TEMPERATURE_COEFF:
                        continue
                    if X[iy+dy,ix+dx] == FIRE:
                        updated_X[iy,ix] = FIRE
                        for wx, wy in zip(available_wind_directions[WIND_DIRECTION]['x'], available_wind_directions[WIND_DIRECTION]['y']):
                            winded_y = np.clip(iy+wy, 1, NY-2)
                            winded_x = np.clip(ix+wx, 1, NX-2)
                            updated_X[winded_y, winded_x] = FIRE if np.random.random() < DIAGONAL_FIRE_START_PROBA*TEMPERATURE_COEFF*WIND_AFFLICTION else updated_X[winded_y, winded_x]
                        break
                else:
                    if np.random.random() <= START_FIRE_PROBA:
                        updated_X[iy,ix] = FIRE
    return updated_X

available_wind_directions = defaultdict()
available_wind_directions['n'] = {'x' : [-1, 0, 1], 'y' : [1, 1, 1]}
available_wind_directions['s'] = {'x' : [-1, 0, 1], 'y' : [-1, -1, -1]}
available_wind_directions['w'] = {'x' : [1, 1, 1], 'y' : [-1, 0, 1]}
available_wind_directions['e'] = {'x' : [-1, -1, -1], 'y' : [1, 0, -1]}
available_wind_directions['nw'] = {'x' : [1, 0], 'y' : [1, 0]}
available_wind_directions['ne'] = {'x' : [-1, 0], 'y' : [1, 0]}
available_wind_directions['sw'] = {'x' : [1, 0], 'y' : [-1, 0]}
available_wind_directions['se'] = {'x' : [-1, 0], 'y' : [-1, 0]}
available_wind_directions.default_factory = available_wind_directions['n']

# Окрестность Мура для восьми соседних клеток от рассматриваемой
neighbourhood = ((-1,-1), (-1,0), (-1,1), (0,-1), (0, 1), (1,-1), (1,0), (1,1))
EMPTY, TREE, FIRE, WATER = (0, 1, 2, 3)

NEW_TREE_PROBA = 1e-2
START_FIRE_PROBA = 1e-3
DIAGONAL_FIRE_START_PROBA = 0.8
TEMPERATURE_COEFF = 1.1
WIND_AFFLICTION = 0.8
WIND_DIRECTION = 'sw'
# Начальная доля леса, занятая деревьями.
FOREST_FRACTION = 0.2
# Размер леса
NX, NY = (200, 200)

# Цвета для визуализации: коричневый - пустая клетка, тёмно-зелёный - дерево, оранжевый - огонь
colors_list = [(0.2,0,0), (0,0.5,0), (1,0,0), 'orange', 'blue']
cmap = colors.ListedColormap(colors_list)
bounds = [0,1,2,3,4]
norm = colors.BoundaryNorm(bounds, cmap.N)

# Инициализируем сетку леса
X  = np.zeros((NY, NX))
X[1:NY-1, 1:NX-1] = np.random.randint(0, 2, size=(NY-2, NX-2))
X[1:NY-1, 1:NX-1] = np.random.random(size=(NY-2, NX-2)) < FOREST_FRACTION
X[10:NY-10, NX//2-7:NX//2+7] = WATER

fig = plt.figure(figsize=(25/3, 6.25))
ax = fig.add_subplot(111)
ax.set_axis_off()
im = ax.imshow(X, cmap=cmap, norm=norm)

# Функция анимации: вызывается для создания кадра для каждого поколения
def animate(i):
    im.set_data(animate.X)
    animate.X = iterate(animate.X)
# Привяжем нашу сетку к идентификатору X в пространстве имен функции animate
animate.X = X

# Интервал между кадрами (мс)
interval = 100
anim = animation.FuncAnimation(fig, animate, interval=interval, frames=500)
anim.save(f"static/fire_in_the_forest_{WIND_DIRECTION}.mp4", writer="ffmpeg")