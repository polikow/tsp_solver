from typing import List

from .ga import GA
from .pso import PSO
from .agent import Agent


class HybridGA(GA):
    def __init__(self, matrix: List[List[float]],
                 population_size: int, generations: int, mutation_probability: float,
                 pso_iterations: int, pso_alpha: float, pso_beta: float):
        super().__init__(matrix, population_size, generations, mutation_probability)

        self.pso_iterations = pso_iterations
        self.pso_alpha = pso_alpha
        self.pso_beta = pso_beta

    def generate_init_population(self):
        pso = PSO(self.matrix, self.population_size, self.pso_iterations, self.pso_alpha, self.pso_beta)
        all_solutions, best_solution, best_length = pso.solve()

        length = len(self.matrix)
        self.population = [Agent(length, solution) for solution in all_solutions]
