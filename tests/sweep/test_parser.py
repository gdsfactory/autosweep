import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ta.sweep.sweep_parser import Sweep
from ta.base.logger import init_logger

v = np.linspace(-1, 1, 11)
i = v/10

init_logger()

s = Sweep(traces={'v': v, 'i': i})
print(s._aliases)

f = plt.figure(1)
ax = f.subplots(1, 1)
ax.plot(s['v'], s['i'])
ax.plot(s['x'], s['y'])
plt.show()