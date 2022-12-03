import serial, time, math
import pandas as pd
import keyboard
from os.path import exists

DOC_NAME = "Sanity_Test_1q"
PATH_SAVE = f"C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/{DOC_NAME}.xlsx"
#DATA_POINT_HEADER = ["Time (sec)", "Alpha", "Beta", "Gamma", "Ax", "Ay", "Az", "AxT", "AyT", "AzT", "vel_x", "vel_y", "vel_z", "vel_dx", "vel_dy", "vel_dz", "pos_x,", "pos_y", "pos_z", "pos_dx,", "pos_dy", "pos_dz"]
DATA_POINT_HEADER = ["Time (sec)", "Alpha", "Beta", "Gamma", "Ax", "Ay", "Az", "AxT", "AyT", "AzT", "Anchor1_dis", "Anchor2_dis"]
NUM_DATA_POINTS = len(DATA_POINT_HEADER)
BAUD_RATE = 115200
OVERWRITE = False
##Stop listening after first timer (looking at the time reported in the first column of data points)
STOP_TIMER = 120

if (exists(PATH_SAVE) and (OVERWRITE == False)):
    print("File already exists, Rename file or change overwrite to True ")
    print(f"File: {PATH_SAVE}")
    quit()


serial_data_input = []
ser = None
running = True
excel_data = []

for i in range(NUM_DATA_POINTS):
    excel_data.append([DATA_POINT_HEADER[i]])
excel_data.append(["offset_ax"])
excel_data.append(["offset_ay"])
excel_data.append(['offset_az (from -9.81)'])
excel_data.append(['alpha offset'])

def connect_serial():
    global ser
    for i in range(30):
        try:
            ser = serial.Serial(F'COM{i}', BAUD_RATE, timeout=1)
            if (ser.isOpen()):
                print(f"Using Com{i}")
            break
        except:
            print(f"Not Com{i}")
        if (i == 29):
            print("No Com found, connect and try again")
            exit()
            
def ReadSerial():
    global serial_data_input, running
    try:
        arduinoData = ser.readline().decode('ascii')
        print(arduinoData)
        serial_data_input = [float(data) for data in arduinoData.split(", ")]
        if (len(serial_data_input) == NUM_DATA_POINTS):
            for i in range(NUM_DATA_POINTS):
                excel_data[i].append(serial_data_input[i])
        elif (len(serial_data_input) == 4):
            excel_data[NUM_DATA_POINTS + 0].append(serial_data_input[0])
            excel_data[NUM_DATA_POINTS + 1].append(serial_data_input[1])
            excel_data[NUM_DATA_POINTS + 2].append(serial_data_input[2])
            excel_data[NUM_DATA_POINTS + 3].append(serial_data_input[3])
        if (float(serial_data_input[0]) > STOP_TIMER):
            print("Timeout")
            running = False      
    except:
        print("Not Saving Serial Line:")  

connect_serial()
while running:
    ReadSerial()
    if keyboard.is_pressed('q'):  # if key 'q' is pressed 
        print('Quitting')
        break  # finishing the loop

print(f"Saving to {PATH_SAVE}")
df = pd.DataFrame(excel_data).T
df.to_excel(excel_writer = PATH_SAVE)