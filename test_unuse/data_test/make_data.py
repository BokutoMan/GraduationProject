import numpy as np
from collections import Counter

class DataSet:
    def __init__(self, mean=100, size=1_000_000) -> None:
        self.data = np.random.poisson(mean, size)
        self.frequency = Counter(self.data)
        self.dfh = Counter(self.frequency.values())
        self.dfh = sorted(self.dfh.items())
import math

begin = 1
n = 100
x = 1
data = []
for j in range(100):
    var = (- math.log(x))**2
    print(f"log({x})^2 = ", var)
    x *= 1/2
    data.append((100-j, int(var)))

print(data)
dfh = data
dataset = []
num = 0
for frequence, count in data:
    for _ in range(count):
        for _ in range(frequence):
            dataset.append(num)
        num += 1
print(len(dataset))
print(sum([i*j for i,j in data]))
    