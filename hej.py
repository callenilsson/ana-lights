import numpy as np
import time
from sklearn.linear_model import LinearRegression

times = []
for i in range(5):
    input('Press enter to start: ' + str(5-i))
    times.append(time.time())
times = np.array(times)
model = LinearRegression().fit(np.arange(5).reshape(-1,1), times)
start_time = model.predict(5)[0]