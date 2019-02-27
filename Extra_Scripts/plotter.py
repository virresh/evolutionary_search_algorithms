import pandas as pd
import matplotlib.pyplot as plt
ga = pd.read_csv('ga_points.csv', header=None)
ma = pd.read_csv('ma_points.csv', header=None)
ax0 = ga[0].plot.line()
ma[0].plot.line(ax=ax0)
ax0.legend(['GA', 'MA'])
ax0.set_title('Cost Plot')
plt.show()

ax1 = ga[1].plot.line()
ma[1].plot.line(ax=ax1)
ax1.legend(['GA', 'MA'])
ax1.set_title('Clash Plot')
plt.show()
