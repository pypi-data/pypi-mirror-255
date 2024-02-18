import matplotlib.pyplot as plt
import numpy as np


def f(x):
    if x >= 0.20:
        return 0.0984
    elif x >= 0.15:
        return 0.0959 + x/60
    elif x >= 0.10:
        return 0.0984
    elif x >= 0:
        return 0.0736 + x*5/12
    else:
        return 0.0148 + x/3

def f1(x):
    if x > 0:
        pass
    else:
        return 0.0526

k = np.linspace(-0.3, 0.3, 1000)
y = []
y1 = []
for i in k:
    y_1 = f(i)
    y.append(y_1)
    if i > -0.2:
        y1.append(f1(i))
plt.plot(k, y)
plt.plot(k[167:], y1)
plt.grid()
plt.show()

