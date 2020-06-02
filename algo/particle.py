from random import random
from typing import List


class Particle:
    def __init__(self, solution: List, length: float):
        self.solution = solution  # текущее решение(позиция) частицы
        self.length = length  # длина текущего решения

        self.p_best_solution = solution  # лучшее найденное точкой решение
        self.p_best_length = length  # длина лучшего решения

        self.velocity = []  # скорость точки

    def update_solution_using_velocity(self):
        for swap_operator in self.velocity:
            i, j, probability = swap_operator
            if random() <= probability:
                self.solution[i], self.solution[j] = self.solution[j], self.solution[i]
