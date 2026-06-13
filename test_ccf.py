import numpy as np
from statsmodels.tsa.stattools import ccf
x = np.random.randn(153)
y = np.random.randn(153)
result = ccf(x, y, nlags=12, alpha=None)
print(len(result), result.shape)