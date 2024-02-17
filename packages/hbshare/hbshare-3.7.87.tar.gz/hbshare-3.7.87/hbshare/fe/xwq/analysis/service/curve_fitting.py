# import numpy as np
# from scipy.optimize import curve_fit
#
# def f(x, y, a, b, c, d, e, f):
#     return a*x**2 + b*y**2 + c*x*y + d*x + e*y + f
# len = 150
# x = np.array([-1.2, -1.0, 0.6, -0.8, 0.8, -0.8, 0.0, 0.2, -1.2, 0.0, 0.2, 1.4, 1.6, 1.2, 1.4, 1.6, 1.8, 1.2, 1.4, 1.6, 1.8, 2.0, 1.4, 1.6, 1.8, 1.6, 1.8, 1.4, 1.6, 1.8, 1.4, 1.6, 1.8])
# y = np.array([81, 81, 81, 83, 83, 91, 91, 91, 93, 93, 93, 99, 99, 101, 101, 101, 101, 103, 103, 103, 103, 103, 105, 105, 105, 107, 109, 111, 111, 111, 113, 113, 113])
# z = np.array([2659, 2604, 2300, 2461, 2083, 2028, 2244-len, 2229-len, 2216, 2211-len, 2196-len, 1978, 1968, 2029, 1996, 1962, 1938, 2005, 1958, 1925, 1922, 1901, 1910, 1877, 1882, 1819, 1750, 1768, 1736, 1726, 1719, 1731, 1706])
# popt, _ = curve_fit(f, (x, y), z)
# print(popt)


from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def f(x, y, a, b, c, d, e, f):
    return a*x**2 + b*x*y + c*y**2 + d*x + e*y + f

len = 150
x = np.array([-1.2, -1.0, 0.6, -0.8, 0.8, -0.8, 0.0, 0.2, -1.2, 0.0, 0.2, 1.4, 1.6, 1.2, 1.4, 1.6, 1.8, 1.2, 1.4, 1.6, 1.8, 2.0, 1.4, 1.8, 1.6, 1.8, 1.4, 1.6, 1.8, 1.4, 1.8, 2.2, 2.4, 2.2, 2.4, -1.2, -1.0, -1.2, -1.0])
y = np.array([81, 81, 81, 83, 83, 91, 91, 91, 93, 93, 93, 99, 99, 101, 101, 101, 101, 103, 103, 103, 103, 103, 105, 105, 107, 109, 111, 111, 111, 113, 113, 81, 81, 83, 83, 111, 111, 113, 113])
z = np.array([2659, 2604, 2300, 2461, 2083, 2028, 2244-len, 2229-len, 2216, 2211-len, 2196-len, 1978, 1968, 2029, 1996, 1962, 1938, 2005, 1958, 1925, 1922, 1901, 1910, 1882, 1819, 1750, 1768, 1736, 1726, 1719, 1706, 2148, 2133, 2134, 2099, 2000, 1985, 1967, 1952])

data = pd.concat([pd.DataFrame(z, columns=['z']), pd.DataFrame(x, columns=['x']), pd.DataFrame(y, columns=['y'])], axis=1)
data['x^2'] = data['x'] ** 2
data['x*y'] = data['x'] * data['y']
data['y^2'] = data['y'] ** 2
data = data[['z', 'x^2', 'x*y', 'y^2', 'x', 'y']]

model = LinearRegression(fit_intercept=True)
res = model.fit(data.iloc[:, 1:].values, data.iloc[:, :1].values)

x = np.arange(-1.3, 2.5, 0.01)
y = np.arange(114, 80, -0.5)
x, y = np.meshgrid(x, y)
z = res.coef_[0][0] * x ** 2 + res.coef_[0][1] * x * y + res.coef_[0][2] * y ** 2 + res.coef_[0][3] * x + res.coef_[0][4] * y + res.intercept_
fig = plt.figure(figsize = (5,5))
ax = Axes3D(fig)
ax.plot_wireframe(x, y, z)
plt.show()