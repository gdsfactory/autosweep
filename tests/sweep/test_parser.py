import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ta.sweep.sweep_parser import Sweep
from ta.base.logger import init_logger

v = np.linspace(-1, 1, 11)
i0 = v/10
i1 = v/20

init_logger()

attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

s = Sweep(traces={'v': list(v), 'i0': tuple(i0), 'i1': i1}, attrs=attrs)
s.change_unit(col='i1', coeff=1000, unit='mA')
s.change_unit(col='i1', coeff=1e-3, unit='A')
print(s._aliases)
print(s.ranges)
print(s.x_col)
print(s.y_cols)
print(s.attrs)

print(s['x'])

f = plt.figure(1)
ax = f.subplots(1, 1)
ax.plot(s['v'], s['i0'])
ax.plot(s['x'], s['y1'])
plt.show()