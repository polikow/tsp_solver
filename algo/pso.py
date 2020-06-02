from random import shuffle
from typing import List, Tuple

from .particle import Particle


class PSO:
    def __init__(self, matrix: List[List[float]], population_size: int, iterations: int, alpha: float, beta: float):
        self.matrix = matrix
        self.population_size = population_size
        self.iterations = iterations
        self.beta = beta
        self.alpha = alpha
        self.particles = None
        self.g_best_particle = None
        self.best_solution = None
        self.best_length = None

    def generate_particles(self):
        self.particles = []
        n = len(self.matrix)

        for i in range(self.population_size):
            solution = list(range(n))
            shuffle(solution)
            length = self.calculate_solution_length(solution)
            particle = Particle(solution, length)
            self.particles.append(particle)

    def update_stats(self):
        self.g_best_particle = min(self.particles, key=lambda particle: particle.p_best_length)

        if self.best_solution is None:
            self.best_solution = self.g_best_particle.p_best_solution
            self.best_length = self.g_best_particle.p_best_length
        elif self.g_best_particle.p_best_length < self.best_length:
            self.best_solution = self.g_best_particle.p_best_solution
            self.best_length = self.g_best_particle.p_best_length

    def calculate_solution_length(self, solution: List[int]) -> float:
        length = 0
        n = len(self.matrix)

        for i in range(n - 1):
            a = solution[i]
            b = solution[i + 1]
            length += self.matrix[a][b]
        length += self.matrix[0][-1]
        return length

    def calc_velocity(self, particle_solution: List[int], solution: List[int]) -> List[Tuple[int, int, float]]:
        velocity = []
        for i in range(len(self.matrix)):
            if particle_solution[i] != solution[i]:
                swap_operator = (i, solution.index(particle_solution[i]), self.alpha)

                velocity.append(swap_operator)
                t = solution[swap_operator[0]]
                solution[swap_operator[0]] = solution[swap_operator[1]]
                solution[swap_operator[1]] = t

        return velocity

    def update_velocity_and_position_of_particles(self):
        for particle in self.particles:
            g_best_solution = self.g_best_particle.p_best_solution[:]  #
            p_best_solution = particle.p_best_solution[:]
            particle_solution = particle.solution[:]

            alpha_velocity = self.calc_velocity(particle_solution, p_best_solution)
            beta_velocity = self.calc_velocity(particle_solution, g_best_solution)

            particle.velocity = alpha_velocity + beta_velocity

            # новое решение для частицы
            particle.update_solution_using_velocity()

            cur_solution_length = self.calculate_solution_length(particle_solution)
            particle.length = cur_solution_length
            if cur_solution_length < particle.p_best_length:
                particle.p_best_solution = particle_solution
                particle.p_best_length = cur_solution_length

    def solve(self):
        self.generate_particles()

        for iteration in range(1, self.iterations + 1):
            self.update_stats()
            # print(f'Итерация: {iteration}, лучшая длина: {self.best_length}')
            self.update_velocity_and_position_of_particles()

        all_solutions = [p.p_best_solution for p in self.particles]
        best_solution = self.g_best_particle.p_best_solution
        best_length = self.g_best_particle.length

        return all_solutions, best_solution, best_length

    def run(self):
        for iteration in range(1, self.iterations + 1):
            if iteration == 1:
                self.generate_particles()

            self.update_stats()
            print(f'Итерация: {iteration}, лучшая длина: {self.best_length}')
            yield iteration, self.best_solution, self.best_length
            self.update_velocity_and_position_of_particles()
