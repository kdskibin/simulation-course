class MLCG:

    def _set_seed(self, new_seed):
        self.Xn = new_seed

    def __init__(self, X0: int = 1, beta: int = 2**32+3, M: int = 2**63):
        self.Xn = X0
        self.beta = beta
        self.M = M
        self.seed = self._set_seed
        self._already_generated = 0
        # прогрев генератора
        for _, _ in zip(range(10), self):
            continue

    def random(self):
        return next(self)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self._already_generated >= self.M:
            raise StopIteration("Достигнут предел непериодичесой генерации чисел")
        self.Xn = (self.beta*self.Xn) % self.M
        return self.Xn / self.M