from math import sqrt
import random as r
from time import sleep

AVAILABLE_WAIT_FUNCTIONS = {
    "normal": lambda m,s: r.gauss(m,s),
    "uniform": lambda m,s: r.uniform(m-sqrt(12)*s, m+sqrt(12)*s),
    "exp": lambda m, s: r.expovariate(1/m)
}


class Throttler:

    def __init__(
            self, 
            iterable, 
            mean: float = 3, 
            sd: float = 0.2, 
            distro: str="normal", 
            min_sleep: float = 1.0
    ) -> None:
        self.iterable = iterable
        self.wait_f = AVAILABLE_WAIT_FUNCTIONS[distro]
        self.mu = mean
        self.sigma = sd
        self.min_sleep = min_sleep

    def sleep(self):
        sleep(max(self.min_sleep, self.wait_f(self.mu, self.sigma)))

    def __iter__(self):
        for element in self.iterable:
            yield element
            self.sleep()