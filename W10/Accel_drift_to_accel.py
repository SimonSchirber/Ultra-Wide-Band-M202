import serial, time, math
import pandas as pd


serial_data = [0,0,0,0]
time_data = []
x_drift, y_drift, z_drift = [], [], []
vel_x, vel_y, vel_z = [], [], []
pos_x, pos_y, pos_z =[], [], []
running = True

# make sure the 'COM#' is set according the Windows Device Manager
for i in range(30):
    try:
        ser = serial.Serial(F'COM{i}', 115200, timeout=1)
        if (ser.isOpen()):
            print(f"Using Com{i}")
        break
    except:
        print(f"Not Com{i}")
    if (i == 29):
        print("No Com port detected in range 29")
        exit()
        break

def ReadSerial():
    global time_data, x_drift, y_drift, z_drift, serial_data, vel_x, vel_y, vel_z, pos_x, pos_y, pos_z, running
    try:
        arduinoData = ser.readline().decode('ascii')
        serial_data = [float(orient) for orient in arduinoData.split(", ")]
        time_data.append(serial_data[0])
        x_drift.append(serial_data[1])
        y_drift.append(serial_data[2])
        z_drift.append(serial_data[3])
        vel_x.append(serial_data[4])
        vel_y.append(serial_data[5])
        vel_z.append(serial_data[6])
        pos_x.append(serial_data[7])
        pos_y.append(serial_data[8])
        pos_z.append(serial_data[9])
        if (serial_data[0] > 300):
            running = False
        print(arduinoData)
    except:
        print("Not proper Byte")

while running:
    ReadSerial()
    time.sleep(.5)

array = [time_data, x_drift, y_drift, z_drift, vel_x, vel_y, vel_z, pos_x, pos_y, pos_z]
df = pd.DataFrame(array).T
df.to_excel(excel_writer = "C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/drift_data_full.xlsx")