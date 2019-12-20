from utils import read_data
import matplotlib.pyplot as plt
from analysis import aggregate_times_by_carraige_flow
import numpy as np
import math

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10


df = read_data("m1", "M1 northbound between J47 and J48 (116024401)")

for col in df.columns: 
    print(col) 

dates = aggregate_times_by_carraige_flow(df)

plt.bar(range(len(dates)), list(dates.values()), align='center')
plt.xticks(range(len(dates)), list(dates.keys()))

plt.show()

