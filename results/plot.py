import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.use('TkAgg')
log = pd.read_json('log')
print(log)
#log.plot()
log.plot(y=['main/loss', 'validation/main/loss'],
        figsize=(15,10),
        grid=True)
plt.show()
#log.show()
