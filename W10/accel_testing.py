from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Data interface
path = r"C:\Users\jmpop\Downloads\no_offsets_Stop_Straight_Stop_Back_Middle_Left_Right_260cm.xlsx"
print(path)
excel_data = pd.read_excel(path)
print(excel_data)
data = pd.DataFrame(excel_data, columns=['Time (sec)', "Alpha", "Beta", "Gamma", 'AxT', 'AyT', 'AzT', 'Anchor1_dis', 'Anchor2_dis'])
print(data)
t0 = list(data['Time (sec)']).index(0)
time = np.array(list(data['Time (sec)'][t0:]))
axt = np.array(list(data['AyT'][t0:]))
print(len(time), len(axt))

sos = signal.butter(5, 5, 'hp', fs=20, output='sos')
filtered = signal.sosfilt(sos, axt)
print(len(filtered))

print(len(time[1:]-time[:-1]))
print(len(filtered[1:]+filtered[:-1]))
vel = np.cumsum(0.5*((time[1:]-time[:-1])*(filtered[1:]+filtered[:-1])))
pos = np.cumsum(0.5*((time[2:]-time[1:-1])*(vel[1:]+vel[:-1])))

plt.subplot(4, 1, 1)
plt.plot(time, axt)
plt.subplot(4, 1, 2)
plt.plot(time, filtered)
plt.subplot(4, 1, 3)
plt.plot(time[1:], vel)
plt.subplot(4, 1, 4)
plt.plot(time[2:], pos)
plt.show()
