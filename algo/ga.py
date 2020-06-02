from itertools import chain
from random import randrange, random
from typing import List, Tuple

from .agent import Agent


class GA:
    def __init__(self, matrix: List[List[float]], population_size: int, generations: int, mutation_probability: float):
        self.population_size = population_size  # размер популяции (количество особей популяции)
        self.matrix = matrix  # матрица смежности графа
        self.generations = generations
        self.mutation_probability = mutation_probability
        self.size = len(matrix)  # количество городов

        self.population = None  # популяция особей
        self.population_fitness = None  # приспособленность особей

        self.g_best_solution = None
        self.g_best_length = None

    def generate_init_population(self):
        self.population = [Agent(self.size) for _ in range(self.population_size)]

    def crossover(self, parent1: Agent, parent2: Agent) -> Tuple[Agent, Agent]:
        n = self.size
        start = randrange(0, self.size)
        end = randrange(0, self.size)

        if end >= start:
            end += 1
        else:
            start, end = end, start

        solution1 = parent1.genotype
        solution2 = parent2.genotype

        new_solution1 = [0] * n
        new_solution2 = [0] * n
        for i in range(start, end):
            new_solution1[i] = solution1[i]
            new_solution2[i] = solution2[i]

        if end != n:
            cur = end
        else:
            cur = 0
        for value in chain(solution2[end:], solution2[:end]):
            if cur != start and value not in new_solution1:
                new_solution1[cur] = value
                if cur == n - 1:
                    cur = 0
                else:
                    cur += 1

        if end != n:
            cur = end
        else:
            cur = 0
        for value in chain(solution1[end:], solution1[:end]):
            if cur != start and value not in new_solution2:
                new_solution2[cur] = value
                if cur == n - 1:
                    cur = 0
                else:
                    cur += 1

        return Agent(n, tuple(new_solution1)), Agent(n, tuple(new_solution2))

    def selection(self):
        # отбор особей для скрещивания
        mating_pool = []
        for _ in range(self.population_size):
            indices = [randrange(0, self.population_size) for _ in range(3)]
            agents = {index: self.population_fitness[index] for index in indices}

            index = max(agents, key=agents.get)  # выбор победителя
            agent = self.population[index]

            mating_pool.append(agent)

        new_population = []
        # лучшая особь прошлой популяции добавляется в новую
        index, fitness = max(enumerate(self.population_fitness), key=lambda a: a[1])
        best_agent = self.population[index]
        new_population.append(best_agent)

        # скрещивание особей. добавление новых особей в новое поколение
        it = iter(mating_pool)
        pairs = zip(it, it)
        for parent1, parent2 in pairs:
            child1, child2 = self.crossover(parent1, parent2)
            new_population.append(child1)
            new_population.append(child2)

        self.population = new_population[:self.population_size]

    def mutate_population(self):
        for agent in self.population:
            if random() < self.mutation_probability:
                g = list(agent.genotype)
                i1, i2 = randrange(0, self.size), randrange(0, self.size)
                g[i1], g[i2] = g[i2], g[i1]
                agent.genotype = tuple(g)

    def calculate_solution_length(self, agent: Agent) -> float:
        n = self.size
        solution = agent.genotype
        length = 0

        for i in range(0, n - 1):
            length += self.matrix[solution[i]][solution[i + 1]]
        length += self.matrix[0][-1]

        return length

    def calculate_fitness(self, agent: Agent) -> float:
        return 1 / self.calculate_solution_length(agent)

    def calculate_population_fitness(self):
        self.population_fitness = []
        for agent in self.population:
            fitness = self.calculate_fitness(agent)
            self.population_fitness.append(fitness)

        # номер особи с наибольшим значением ЦФ
        index = self.population_fitness.index(max(self.population_fitness))
        best_agent = self.population[index]

        self.update_stats(best_agent)

    def update_stats(self, best_agent: Agent):
        l_best_length = self.calculate_solution_length(best_agent)
        l_best_solution = best_agent.genotype

        if self.g_best_solution is None:
            self.g_best_solution = l_best_solution
            self.g_best_length = l_best_length

        elif self.g_best_length > l_best_length:
            self.g_best_solution = l_best_solution
            self.g_best_length = l_best_length

    def shake(self):
        u = len(set(self.population_fitness)) / self.population_size * 100
        if u < 70:
            size = int(self.population_size * 2 / 3)
            for _ in range(size):
                agent = self.population[randrange(0, self.population_size)]
                agent.create_genotype(self.size)

            self.calculate_population_fitness()

    def run(self):
        for generation in range(1, self.generations + 1):
            if generation == 1:
                self.generate_init_population()
                self.calculate_population_fitness()

            yield generation, self.g_best_solution, self.g_best_length
            self.selection()
            self.mutate_population()
            generation += 1
            self.calculate_population_fitness()
            self.shake()
