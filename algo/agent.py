from random import shuffle
from typing import Tuple


class Agent:

    def __init__(self, size: int, genotype: Tuple[int] = None):
        # генотип особи
        # генотип состоит из 1 хромосомы с length числом генов
        if genotype is None:
            self.create_genotype(size)
        else:
            self.genotype = genotype

    def create_genotype(self, size: int):
        tmp = list(range(size))
        shuffle(tmp)
        self.genotype = tuple(tmp)
