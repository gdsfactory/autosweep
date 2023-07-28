import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ta.sweep.sweep_parser import Sweep
from ta.utils.logger import init_logger

v = np.linspace(-1, 1, 11)
i0 = v/10
i1 = v/20

init_logger()

attrs = {'v': ("Voltage", "V"), 'i0': ("Current", "A"), 'i1': ("Current", "A")}

s = Sweep(traces={'v': list(v), 'i0': tuple(i0), 'i1': i1}, attrs=attrs)
s.change_unit(col='i1', coeff=1000, unit='mA')
s.change_unit(col='i1', coeff=1e-3, unit='A')
f = plt.figure(1)
ax = f.subplots(1, 1)
ax.plot(s['v'], s['i0'])
ax.plot(s['x'], s['y1'])
print(attrs)

x = np.linspace(0, 5, 64)
y = np.sin(2*np.pi*x)

s = Sweep(traces={'x': x, 'y': y}, attrs={'x': 'X', 'y': 'Y'})
ss = s.filter_range(x_min=0.2, x_max=0.8)

f = plt.figure(2)
ax = f.subplots(1, 1)
ax.plot(s['x'], s['y'], 'x-')
ax.plot(ss['x'], ss['y'], '.-')
print(s._aliases)
print(s.attrs)
ax.grid()
labels = s.get_axis_labels()
ax.set_xlabel(labels['x'])
ax.set_ylabel(labels['y'])
plt.show()
