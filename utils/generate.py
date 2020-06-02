from math import sqrt
from random import randrange


def generate_coordinates(n, x_min=0, x_max=500, y_min=0, y_max=500):
    x = [randrange(x_min, x_max) for _ in range(n)]
    y = [randrange(y_min, y_max) for _ in range(n)]
    return [(xi, yi) for xi, yi in zip(x, y)]


def generate_matrix(xy):
    n = len(xy)
    matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0
            else:
                x1, y1 = xy[i]
                x2, y2 = xy[j]
                matrix[i][j] = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return matrix
