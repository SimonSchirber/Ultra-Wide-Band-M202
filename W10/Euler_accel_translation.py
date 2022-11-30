import serial, time, math

serial_data = []
time_data = []
# Orientation angles
alpha, beta, gamma = [], [], []
ax, ay, az = [], [], []

# make sure the 'COM#' is set according the Windows Device Manager
for i in range(30):
    try:
        ser = serial.Serial(F'COM{i}', 115200, timeout=1)
        if (ser.isOpen()):
            print(f"Using Com{i}")
        break
    except:
        print(f"Com{i} not open at 115200")
        ser.close()
    if (i == 29):
        print("No Com port detected in range 29")
        exit()
        break
def ReadSerial():
    global serial_data
    try:
        arduinoData = ser.readline().decode('ascii')
        serial_data = [float(orient) for orient in arduinoData.split(", ")]
        print(arduinoData)
    except:
        print("No proper Byte Available")

def TranslateAccel():
    alpha = serial_data[1] * math.pi/180  # compass rotation      0       , 2pi
    beta = serial_data[2]  * math.pi/180 # tilt up/down          -pi/2   , pi/2
    gamma = serial_data[3] * math.pi/180 # barrel roll           -pi     , pi

    ax = serial_data[4]     # accelerometer reference x vector
    ay = serial_data[5]      # accelerometer reference y vector
    az = serial_data[6]     # accelerometer reference z vector

    #Ax Tranlation
    ax_x = ax * math.cos(alpha) * math.cos(beta)
    ax_y = ax * math.sin(alpha) * math.cos(beta)
    ax_z = -ax * math.sin(beta)
    # print(ax_x, ax_y, ax_z)
    # print(math.sqrt(ax_x ** 2 + ax_y ** 2 + ax_z ** 2))

    #Ay Tranaslation
    ay_x = ay * (math.cos(alpha) * math.sin(beta) * math.cos(gamma) + math.sin(alpha) * math.cos(gamma))
    ay_y = ay * (math.sin(alpha) * math.sin(beta) * math.sin(gamma) + math.cos(alpha) * math.cos(gamma))
    ay_z = ay * (math.cos(beta) * math.sin(gamma))
    # print(ay_x, ay_y, ay_z)
    # print(math.sqrt(ay_x ** 2 + ay_y ** 2 + ay_z ** 2))

    #Az Translation
    az_x = az * (math.cos(alpha) * math.sin(beta) * math.cos(gamma) + math.sin(alpha) * math.sin(gamma))
    az_y = az * (math.sin(alpha) * math.sin(beta) * math.cos(gamma) - math.cos(alpha) * math.sin(gamma))
    az_z = az * math.cos(beta) * math.cos(gamma)
    # print(az_x, az_y, az_z)
    # print(math.sqrt(az_x ** 2 + az_y ** 2 + az_z ** 2))


    x = ax_x + ay_x + az_x
    y = ax_y + ay_y + az_y
    z = ax_z + ay_z + az_z
    print(f"Ax: {x}, Ay:{y}, Az:{z}")   

time.sleep(1)
while True:
    ReadSerial()
    time.sleep(.125)

        

