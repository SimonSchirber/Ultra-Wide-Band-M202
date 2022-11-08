import serial
import time


# make sure the 'COM#' is set according the Windows Device Manager
for i in range(20):
    try:
        ser = serial.Serial(F'COM{i}', 9600, timeout=1)
        if (ser.isOpen()):
            print(f"Using Com{i}")
        break
    except:
        print(f"Not Com{i}")
    if (i == 19):
        print("no Com found")
        exit()
        break
    

time.sleep(1)
while True:
    try:
        arduinoData = ser.readline().decode('ascii')
        orientation = [float(orient) for orient in arduinoData.split(", ")]
        print(arduinoData)
        
   
    except:
        print("No Byte")
        

ser.close()