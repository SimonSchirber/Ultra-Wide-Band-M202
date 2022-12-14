import pygame,math, os, serial, time
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import asyncio
from tplinkcloud import TPLinkDeviceManager

######Streaming Data Method####
DATA_POINT_HEADER = ["Time (sec)", "Alpha", "Beta", "Gamma", "Ax", "Ay", "Az", "AxT", "AyT", "AzT", "Anchor_1_dis", "Anchor_2_dis"]
NUM_DATA_POINTS = len(DATA_POINT_HEADER)
BAUD_RATE = 115200
ser = 0
USE_EXCEL = False
EXCEL_PATH = r'"C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/Sanity_Test_2.xlsx"'
EXCEL_TIME_DIFF = .05
#inch to meter conversion
IM = 39.37
######Calibration/Room Setup########
#Room wall length dimension (X, Y) in meters
wall_len = [334/IM, 339/IM]
#Anchors: Known Cordinates (x,y, z) in room (m) where 0,0,0 is top left corner in diplay
Anchor1 = [0, 0, 37.5/IM]
Anchor2 = [0, 67.5/IM, 137.5/IM]
dis_anchors = 0
anchor1_dis = .5
anchor2_dis = .5
anchor_pos_list = [Anchor1, Anchor2]
anchor_name_list = ["Anchor1", "Anchor2"]
#Smart Device objects
#No tape Light
object1 = [83/IM, 111/IM, 52/IM]
#Tape light 
object2 = [313/IM, 210/IM, 49/IM]
#BLuetooth speaker
object3 = [313/IM, 280/IM, 34/IM]
object4 = [120/IM, .3, 1.00]
object5 = [ 50/IM, 300/IM, 1.00]
obj_pos_list = [object1, object2, object3, object4, object5]
obj_name_list = ["Smart Light Zero", "Smart Light One", "Bluetooth Speaker 0", "Smart TV", "Bluetooth Speaker 1"]
OBJECT_RADIUS = 1.5 
comb_pos_list = [Anchor1, Anchor2]
comb_name_list = ["Anchor1", "Anchor2"]
for obj in range(len(obj_pos_list)):
    comb_pos_list.append(obj_pos_list[obj])
    comb_name_list.append(obj_name_list[obj])

#Magnetometer calibration facing 0 degrees
alpha_offset = 0
###Accelerometer offsets
ax_offset, ay_offset, az_offset = 0, 0, 0
###Height which objects will be set to unless specificed otherwise
default_height = 0

##KASA Connect Login
load_dotenv()
username = os.getenv("kasausername")
password = os.getenv("password")
device_manager = TPLinkDeviceManager(username, password)
light_0_on, light_1_on = True, True

###########Sensor Data Readings#############
#Magnetometer Angle
alpha = 0
###Gyroscope Angle####
beta = 0
####Barrel Role Angle(Not displayed)####
gamma = 0
###########Calculated Change in Distance (200ms every print * 3moving average = .6 sec Mean)#######
pos_dx, pos_dy, pos_dz = [0,0,0], [0,0,0], [0,0,0]
### .6s Moving average distance sum
dx, dy, dz = 0, 0, 0

#Gyroscope Readings (Gx, Gy, Gz)
G = [10, 5.26, -1.3]
#Raw Accelerometer Readings(Ax, Ay, Az)
A = [32.5, 72.97, 32.56]
#Tranlated Accelerometer Readings
A_T = [0, 0, 0]
#Anchor Relatives Distances from tag (one dist reading/anchor)
anchor_dist_list = [5.45, 10.3]
#point two in the line to define line of sight
X2, Y2, Z2 = 0, 0 , 0

#####Predictions#####
#User Predicted Position (Tag Position, x, y, z)
predicted_pos = [0, 0, 50/IM]
hit_index = -1
show_anchor_pos = False
tracking = True
##Screen x y pos to see movements over time
tracked_pos = [[], []]

######Pygame Display Settings####
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (110,110,110)
black = (0,0,0)
yellow= (255, 255, 0)
wall_color = red
calibration_mode = False
need_render = True

#Display Dimensions, where column 1 is room display
length_display = 700
width_column1 = 700
width_column2 = 250
width_column3 = 350
width_display = width_column1 + width_column2 + width_column3
column3_xcord = width_column1 + width_column2
zero_cordinate = [0, 0]
scale_dim = 0

#General Variables
running = True
cwd = os.getcwd()
github_dir = os.path.abspath(os.curdir)
images_dir = github_dir + "\Main\Images"
space = 10
obj_space = 50

#Initiate Pygame 
pygame.init()
screen = pygame.display.set_mode((width_display, length_display))
small_font = pygame.font.SysFont('Corbel', 30)
smallest_font = pygame.font.SysFont('Corbel', 15)

#Pygame Room Images
anchor_img = pygame.image.load(images_dir + "\\anchor.png").convert_alpha()
anchor_img = pygame.transform.rotozoom(anchor_img, 0., .05)
bulb_img = pygame.image.load(images_dir + "\\bulb.png").convert_alpha()
bulb_img = pygame.transform.rotozoom(bulb_img, 0., .12)
tv_img = pygame.image.load(images_dir + "\\tv.png").convert_alpha()
tv_img = pygame.transform.rotozoom(tv_img, 0., .08)
user_tag_img = pygame.image.load(images_dir + "\\user.png").convert_alpha()
user_tag_img = pygame.transform.rotozoom(user_tag_img, 0., .1)
speaker_img = pygame.image.load(images_dir + "\\speaker.png").convert_alpha()
speaker_img = pygame.transform.rotozoom(speaker_img, 0., .1)
#Larger Guessed images
tv_full_img = pygame.image.load(images_dir + "\\tv_full.png").convert_alpha()
tv_full_img = pygame.transform.rotozoom(tv_full_img, 0, .5)
bulb_on_full_img = pygame.image.load(images_dir + "\\bulb_on.png").convert_alpha()
bulb_on_full_img = pygame.transform.rotozoom(bulb_on_full_img, 0, .40)
bulb_off_full_img = pygame.image.load(images_dir + "\\bulb_off.png").convert_alpha()
bulb_off_full_img = pygame.transform.rotozoom(bulb_off_full_img, 0, .11)
speaker_full_img = pygame.image.load(images_dir + "\\speaker.png").convert_alpha()
speaker_full_img = pygame.transform.rotozoom(speaker_full_img, 0., .4)
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
            print("no Com found")
            exit()
            break
 
def read_excel():
    global need_render, alpha, beta, gamma, A, A_T, pos_dx, pos_dy, pos_dz, anchor1_dis, anchor2_dis, ax_offset, ay_offset, az_offset, alpha_offset
    #["Time (sec)", "Alpha", "Beta", "Gamma", "Ax", "Ay", "Az", "AxT", "AyT", "AzT", "pos_dx,", "pos_dy", "pos_dz", "Anchor_1_dis", "Anchor_2_dis"]
    alpha = data[DATA_POINT_HEADER[1]][d_index]
    beta = data[DATA_POINT_HEADER[2]][d_index]
    gamma = data[DATA_POINT_HEADER[3]][d_index]
    A[0] = data[DATA_POINT_HEADER[4]][d_index]
    A[1] = data[DATA_POINT_HEADER[5]][d_index]
    A[2] = data[DATA_POINT_HEADER[6]][d_index]
    A_T[0] = data[DATA_POINT_HEADER[7]][d_index] 
    A_T[1] = data[DATA_POINT_HEADER[8]][d_index] 
    A_T[2] = data[DATA_POINT_HEADER[9]][d_index]
    anchor1_dis = data[DATA_POINT_HEADER[10]][d_index]
    anchir2_dis = data[DATA_POINT_HEADER[11]][d_index]
    for i in range(NUM_DATA_POINTS):
        print(data[i][d_index])
    need_render = True

def draw_mag_line(line_angle, color, radius):
    """Draw the lines that move the magnetometer/compass"""
    xcenter_mag = (width_column1 + column3_xcord)/2
    ycenter_mag =  length_display*.5
    xouter_mag = xcenter_mag + radius * math.sin(math.radians(line_angle))
    youter_mag = ycenter_mag - radius * math.cos(math.radians(line_angle))
    pygame.draw.line(screen, color, (xcenter_mag, ycenter_mag), (xouter_mag, youter_mag), 2)
    pygame.draw.circle(screen, black, (xcenter_mag, ycenter_mag), 5, 0)
    pygame.draw.circle(screen, color, (xouter_mag, youter_mag), 5, 0)

def draw_gyro_line(middle_cord):
    xcenter_mag = middle_cord[0]
    ycenter_mag =  middle_cord[1]
    xouter_mag = xcenter_mag + 66 * math.cos(beta * np.pi/180)
    youter_mag = ycenter_mag + -66 * math.sin(beta * np.pi/180)
    pygame.draw.line(screen, blue, (xcenter_mag, ycenter_mag), (xouter_mag, youter_mag), 2)
    pygame.draw.circle(screen, black, (xcenter_mag, ycenter_mag), 5, 0)
    pygame.draw.circle(screen, blue, (xouter_mag, youter_mag), 5, 0)

def draw_accel_data(centerxy, centerz):
    ###Assuming full = 75 pixels
    mag_x = A_T[0] * 60
    mag_y = A_T[1] *60
    mag_z = -(A_T[2] + 9.8) * 60
    if (abs(mag_x) > 75 and abs(mag_x) > abs(mag_y)):
        scale_f = 75/mag_x
        mag_x *= scale_f
        mag_y *= scale_f
    elif (abs(mag_y) > 75):
        scale_f = 75/mag_y
        mag_x *= scale_f
        mag_y *= scale_f
    if (abs(mag_z) > 75):
        scale_f = 75/mag_z
        mag_z *= scale_f
    
    pygame.draw.line(screen, blue, (centerxy[0], centerxy[1]), (centerxy[0] + mag_x, centerxy[1] + mag_y), 2)
    pygame.draw.line(screen, blue,(centerz[0], centerxy[1]), (centerz[0], centerxy[1] - mag_z), 2)
    
    pygame.draw.circle(screen, blue, (centerxy[0], centerxy[1]), 5, 0)
    pygame.draw.circle(screen, blue, (centerxy[0] + mag_x, centerxy[1] + mag_y), 5, 0)
    
    pygame.draw.circle(screen, blue, (centerz[0], centerxy[1]), 3, 0)
    pygame.draw.circle(screen, blue, (centerz[0], centerxy[1] - mag_z), 3, 0)

def move_object(user_pos = False, Object_num = None):
    global predicted_pos, comb_pos_list
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x = (mouse_x - rectx) /scale_dim
    mouse_y  = (mouse_y - recty) / scale_dim
    mouse_x = round(mouse_x,2)
    mouse_y = round(mouse_y, 2)
    if (user_pos == True):
        predicted_pos = [mouse_x, mouse_y, 0]
    elif (Object_num != None):
        comb_pos_list[Object_num] = [mouse_x, mouse_y, 0]

def calibrate_pos(object_number):
    global predicted_pos
    global comb_pos_list
    object_number -= 1
    waiting_for_click = True
    while waiting_for_click:
        render_room()
        calibration_mode_render()
        pygame.display.update()
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                move_object(Object_num = object_number)
                waiting_for_click = False
    # try:
    #     comb_pos_list[object_number][2] = float(input(f"Z position(m) of Object {comb_name_list[object_number]}: "))
    # except:
    #     print("Not a valid Z input")
    #     comb_pos_list[object_number][2] = default_height
    comb_pos_list[object_number][2] = default_height
    
def render_room():
    #########1st Column#######
    #Scale Room to fit Screen: Check if x dimonsion is greater than y, scale display based on X to fill 90% of screen width
    global zero_cordinate, scale_dim, rectx, recty
    if (wall_len[0] > wall_len[1]):
        scale_dim = width_column1 * .9 / wall_len[0]
        rectx = width_column1 - (.95* width_column1)
        recty = length_display/2 - (wall_len[1] * scale_dim/2)
    else:
        scale_dim = length_display * .9 / wall_len[1]  
        rectx = width_column1/2 - (wall_len[0] * scale_dim/2)
        recty = length_display - (.95 * length_display) 
    zero_cordinate = [rectx, recty]
    x_wall_dis = wall_len[0] * scale_dim
    y_wall_dis = wall_len[1] * scale_dim
    #Draw Walls: rect(TLcorner x, y, xlen, ylen)
    pygame.draw.rect(screen, red, pygame.Rect(rectx, recty, x_wall_dis, y_wall_dis), width = 3)
    #Add dimensions to walls
    xwall_text = small_font.render(f"{round(wall_len[0], 2)}m", True, red)
    ywall_text = small_font.render(f"{round(wall_len[1], 2)}m", True, red)
    ywall_text = pygame.transform.rotate(ywall_text, 90)
    screen.blit(xwall_text, (rectx + x_wall_dis/2 - 30, recty - 35))
    screen.blit(ywall_text, (rectx - 35, recty + (y_wall_dis/2) - 30))
    zero_cordinate_text = smallest_font.render("(0,0)", True, red)
    screen.blit(zero_cordinate_text, (rectx - 20, recty - 20))
    ##Check if mouse position in walls to get posiiton, then drae
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if ((mouse_x > rectx) and (mouse_x < rectx + x_wall_dis) and (mouse_y > recty) and (mouse_y < recty + y_wall_dis)):
        pygame.draw.circle(screen, green, (mouse_x, mouse_y), 2, 0)
        mouse_x = "{:.2f}".format((mouse_x - rectx) /scale_dim)
        mouse_y  = "{:.2f}".format((mouse_y - recty) / scale_dim)
        mouse_text = small_font.render(f"X: {mouse_x}m Y: {mouse_y}m", True, green)
        screen.blit(mouse_text, (20, length_display- 30)) 
    #If tracking, render
    for i in range(len(tracked_pos[0])):
        pygame.draw.circle(screen, green, (tracked_pos[0][i], tracked_pos[1][i]), 2, 0)    
    #Draw Items in Room 
    for device in range(len(comb_pos_list)):
        devicex_pos = comb_pos_list[device][0] * scale_dim + zero_cordinate[0]
        devicey_pos = comb_pos_list[device][1] * scale_dim + zero_cordinate[1]
        device_name = comb_name_list[device].lower()
        if ("anchor" in device_name):
            screen.blit(anchor_img, (devicex_pos,devicey_pos))
            ###Show Distance Mode
            if (show_anchor_pos):
                color = yellow
                if (device % 2 == 0):
                    color = blue
                for i in range(5):
                    #draw lines for every meter
                    sphere_radius = i + 1
                    dist_from_center = comb_pos_list[device][2] - predicted_pos[2]
                    circle_radius = calc_circle_radius( dist_from_center, sphere_radius)

                    pygame.draw.circle(screen, color, (devicex_pos, devicey_pos ), circle_radius*scale_dim , 2)
        elif ("light" in device_name):
            screen.blit(bulb_img, (devicex_pos,devicey_pos))
        elif ('tv' in device_name):
            screen.blit(tv_img, (devicex_pos,devicey_pos))
        elif('speaker' in device_name):
            screen.blit(speaker_img, (devicex_pos,devicey_pos))
        pygame.draw.circle(screen, green, (devicex_pos, devicey_pos), 2, 0)
    userx_pos = predicted_pos[0] * scale_dim + zero_cordinate[0]
    usery_pos = predicted_pos[1] * scale_dim + zero_cordinate[1]
    screen.blit(user_tag_img, (userx_pos, usery_pos))
    pygame.draw.circle(screen, green, (userx_pos, usery_pos), 2, 0)
    if (tracking):
        tracked_pos[0].append(userx_pos)
        tracked_pos[1].append(usery_pos)
             
async def toggleTape():
    #Smart Light 0
    global light_0_on
    light_0_on = not(light_0_on)
    device_name = "Tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Toggling {device_name}')
        await device.toggle()
    else:  
        print(f'Could not find {device_name}')

async def toggleNoTape():
    #Smart Light 1
    global light_1_on
    light_1_on = not(light_1_on)
    device_name = "No tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Toggling {device_name}')
        await device.toggle()
    else:  
        print(f'Could not find {device_name}')
  
def calibration_mode_render():
    #Vertical Column Lines
    pygame.draw.line(screen, white, (width_column1, 0), (width_column1, length_display), 1)
    pygame.draw.line(screen, white,(column3_xcord, 0), (column3_xcord, length_display), 1)
    #########1st Column#######
    render_room()
    active_menu_text = smallest_font.render("'A': Active Menu", True, green)
    screen.blit(active_menu_text, (width_column1 - 150, length_display - 25))
    ######2nd Column
    y2_dis = obj_space
    column2_divider = width_column1 + 70
    pygame.draw.line(screen, white, (width_column1, y2_dis), (column3_xcord, y2_dis), 1)
    pygame.draw.line(screen, white, (column2_divider, 0), (column2_divider, length_display), 1)
    key_text = small_font.render("Key", True, green)
    function_text = small_font.render("Function", True, green)
    screen.blit(key_text, (width_column1 + space, space))
    screen.blit(function_text, (width_column1 + 70 + space, space))
    num_objects = len(comb_pos_list)
    hot_key = 1
    calibrate_text = smallest_font.render("Recalibrate Positon ->", True, green)
    for object in range(num_objects):
        hotkey_text = small_font.render(str(hot_key), True, green)
        screen.blit(hotkey_text, (width_column1 + space, y2_dis + space))
        screen.blit(calibrate_text, (column2_divider + space, y2_dis + space))
        hot_key += 1
        y2_dis += obj_space
        pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    user_pred_text = smallest_font.render("Send User Prediction", True, green)
    hotkey_text = small_font.render(str(hot_key), True, green)
    screen.blit(hotkey_text, (width_column1 + space, y2_dis + space))
    screen.blit(user_pred_text, (column2_divider + space, y2_dis + space))
    hot_key +=1
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    mag_text = smallest_font.render("Calibrate Mag", True, green)
    magkey_text = small_font.render("M", True, green)
    screen.blit(mag_text, (column2_divider + space, y2_dis + space))
    screen.blit(magkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    tag_text = smallest_font.render("Show UWB meter Lines", True, green)
    tagkey_text = small_font.render("S", True, green)
    screen.blit(tag_text, (column2_divider + space, y2_dis + space))
    screen.blit(tagkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    reconnect_text = smallest_font.render("Stop/Start Track Pos", True, green)
    reconnectkey_text = small_font.render("T", True, green)
    screen.blit(reconnect_text, (column2_divider + space, y2_dis + space))
    screen.blit(reconnectkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    reconnect_text = smallest_font.render("Clear Tracking Pos", True, green)
    reconnectkey_text = small_font.render("Q", True, green)
    screen.blit(reconnect_text, (column2_divider + space, y2_dis + space))
    screen.blit(reconnectkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    # reconnect_text = smallest_font.render("Reconnect tag", True, green)
    # reconnectkey_text = small_font.render("R", True, green)
    # screen.blit(reconnect_text, (column2_divider + space, y2_dis + space))
    # screen.blit(reconnectkey_text, (width_column1 + space, y2_dis + space))
    # y2_dis += obj_space
    # pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))

    #######3rd Column#####
    ###Anchor/Smart Device Positions
    obj_text = small_font.render('Object', True, green)
    x_text = small_font.render('X(m)', True, green)
    y_text = small_font.render('Y(m)', True, green)
    z_text = small_font.render('Z(m)', True, green)
    xobj_text_dis = column3_xcord + round(width_column3*.35)
    yobj_text_dis = column3_xcord + round(width_column3 * .57)
    zobj_text_dis = column3_xcord + round(width_column3 * .79)
    screen.blit(obj_text, (column3_xcord + space, space))
    screen.blit(x_text, (xobj_text_dis, space)) 
    screen.blit(y_text, (yobj_text_dis, space))
    screen.blit(z_text, (zobj_text_dis, space))
    #Write Details of positions in X,Y, Z boxes
    for obj_num in range(len(comb_pos_list)):
        y_obj_dis = (1 + obj_num) * obj_space
        pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
        x_data_text = small_font.render(str(comb_pos_list[obj_num][0]), True, green)
        y_data_text = small_font.render(str(comb_pos_list[obj_num][1]), True, green)
        z_data_text = small_font.render(str(comb_pos_list[obj_num][2]), True, green)
        name_data_text = smallest_font.render(comb_name_list[obj_num], True, green)
        screen.blit(name_data_text, (space + column3_xcord, space + y_obj_dis))
        screen.blit(x_data_text, (xobj_text_dis, space + y_obj_dis))
        screen.blit(y_data_text, (yobj_text_dis, space + y_obj_dis))
        screen.blit(z_data_text, (zobj_text_dis, space + y_obj_dis))   
        #Draw the bottom line and horizontal dividers
        # if (obj_num ==  len(comb_pos_list) - 1):
        #     y_obj_dis = (2 + obj_num) * obj_space
        #     pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
        #     pygame.draw.line(screen, white, (xobj_text_dis-space, 0), (xobj_text_dis-space, y_obj_dis), 1)
        #     pygame.draw.line(screen, white, (yobj_text_dis- space, 0), (yobj_text_dis-space, y_obj_dis), 1)
        #     pygame.draw.line(screen, white, (zobj_text_dis- space, 0), (zobj_text_dis-space, y_obj_dis), 1)
    ##Add user Pos
    y_obj_dis += obj_space
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    x_data_text = small_font.render(str(round(predicted_pos[0], 2)), True, green)
    y_data_text = small_font.render(str(round(predicted_pos[1], 2)), True, green)
    z_data_text = small_font.render(str(round(predicted_pos[2], 2)), True, green)
    name_data_text = smallest_font.render("Pred User Pos", True, green)
    screen.blit(name_data_text, (space + column3_xcord, space + y_obj_dis))
    screen.blit(x_data_text, (xobj_text_dis, space + y_obj_dis))
    screen.blit(y_data_text, (yobj_text_dis, space + y_obj_dis))
    screen.blit(z_data_text, (zobj_text_dis, space + y_obj_dis))   
    y_obj_dis += obj_space
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    pygame.draw.line(screen, white, (xobj_text_dis-space, 0), (xobj_text_dis-space, y_obj_dis), 1)
    pygame.draw.line(screen, white, (yobj_text_dis- space, 0), (yobj_text_dis-space, y_obj_dis), 1)
    pygame.draw.line(screen, white, (zobj_text_dis- space, 0), (zobj_text_dis-space, y_obj_dis), 1)

def active_mode_render():
    global light_1_on, light_0_on
    """Draw Display for active mode"""
    #Vertical Column Lines
    pygame.draw.line(screen, white, (width_column1, 0), (width_column1, length_display), 1)
    pygame.draw.line(screen, white,(column3_xcord, 0), (column3_xcord, length_display), 1)
    ######## First column #########
    render_room()
    calib_menu_text = smallest_font.render("'C': Calibration Menu", True, green)
    screen.blit(calib_menu_text, (width_column1 - 150, length_display - 25))
    ########  Second Column  ########
    #Column 2 Horizaontal Line Dividers
    pygame.draw.line(screen, white, (width_column1, length_display/3), (column3_xcord, length_display/3), 1)
    pygame.draw.line(screen, white, (width_column1, length_display*2/3), (column3_xcord, length_display*2/3), 1)
    column_head_pos = width_column1 + 30
    ####Gyroscope
    gyro_text = small_font.render("Beta (Tilt)", True, green)
    screen.blit(gyro_text, (column_head_pos + 40, space))
    up_text = smallest_font.render("Up", True, green)
    down_text = smallest_font.render("Down", True, green)
    forward_text = smallest_font.render("Forward", True, green)
    xgyro_line = width_column1 + 70
    top_point = (xgyro_line, obj_space)
    middle_point = (xgyro_line, obj_space + 66)
    bottom_point =(xgyro_line, obj_space + 132) 
    forward_point = (xgyro_line +66, obj_space + 66)
    screen.blit(up_text, (width_column1+ 30, obj_space))
    screen.blit(down_text, (width_column1 +15 , obj_space + 120))
    screen.blit(forward_text, (xgyro_line + 71, obj_space + 60))
    pygame.draw.line(screen, white, top_point, bottom_point)
    pygame.draw.line(screen, white, middle_point, forward_point)
    tilt_text = small_font.render(f"Angle: {beta}", True, green)
    screen.blit(tilt_text,(width_column1 + 40 , obj_space + 140))
    draw_gyro_line(middle_point)
    ###Magnetometer
    mag_text = small_font.render(f"Alpha (Compass)", True, green)
    angle_text = small_font.render(f"Angle: {round(alpha,2)}", True, green)
    screen.blit(mag_text, (width_column1 + 30,  length_display/3 + space))
    radius_mag = length_display*1/9
    pygame.draw.circle(screen, grey, ((width_column1 + column3_xcord)/2, length_display * .5), radius_mag, 0) 
    pygame.draw.circle(screen, white, ((width_column1 + column3_xcord)/2, length_display * .5), radius_mag, 3)
    draw_mag_line((360 - alpha_offset), red, radius_mag)
    draw_mag_line((360 - alpha_offset) + alpha, green, radius_mag)
    screen.blit(angle_text, (width_column1 +60, 2/3*length_display - 35))
    ###Predictions
    prediction_text = small_font.render('Pos Prediction', True, green)
    x_pred_text = small_font.render(f'X(m): {"{:.2f}".format(predicted_pos[0])}m', True, green)
    y_pred_text = small_font.render(f'Y(m): {"{:.2f}".format(predicted_pos[1])}m', True, green)
    z_pred_text = small_font.render(f'Z(m): {"{:.2f}".format(predicted_pos[2])}m', True, green)
    screen.blit(prediction_text, (column_head_pos,  length_display *2/3 + space))
    screen.blit(x_pred_text, (width_column1 + 20,  length_display *2/3 + 50))
    screen.blit(y_pred_text, (width_column1 + 20,  length_display *2/3 + 100))
    screen.blit(z_pred_text, (width_column1 + 20,  length_display *2/3 + 150))
    ######  Third Column   #######
    middle_column3 = (width_display + column3_xcord)/2
    y_obj_dis = 0
    ####UWB Anchor Distance
    UWB_text = small_font.render('UWB Anchors', True, green)
    Anchor_text = small_font.render('Name', True, green)
    Dist_text = small_font.render('Dist(m)', True, green)
    screen.blit(UWB_text, (middle_column3 - 100, y_obj_dis+space))
    screen.blit(Anchor_text, (column3_xcord + 30 , y_obj_dis + obj_space + space))
    screen.blit(Dist_text, (middle_column3 + 30, y_obj_dis + obj_space + space))
    y_obj_dis += obj_space
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    ydiv_uwb_start = y_obj_dis
    for anchor in range(len(anchor_pos_list)):
        anchor_text = small_font.render(anchor_name_list[anchor], True, green)
        if (anchor == 0):
            anchor_dis = anchor1_dis
        else:
            anchor_dis = anchor2_dis
        tag_dist_text = small_font.render(str(round(anchor_dis, 2)), True, green)
        y_obj_dis += obj_space
        screen.blit(anchor_text, (column3_xcord + 30, y_obj_dis + space))
        screen.blit(tag_dist_text, (middle_column3 + 50, y_obj_dis +space))
        pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
        if (anchor == len(anchor_pos_list)- 1):
            y_obj_dis += obj_space
            pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
        pygame.draw.line(screen, white, (middle_column3, ydiv_uwb_start), (middle_column3, y_obj_dis), 1)
    ###Accelerometer
    accel_text = small_font.render("Accelerometer", True, green)
    screen.blit(accel_text, (middle_column3 - 100, y_obj_dis+space))
    y_obj_dis += obj_space
    #pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    y_obj_dis += 30
    #X,Y Acceleromter Cross Visual
    top_point = (middle_column3- 50, y_obj_dis)
    middle_point = (middle_column3- 50,y_obj_dis + 75)
    bottom_point = (middle_column3- 50, y_obj_dis+ 150)
    left_point = (middle_column3- 125, y_obj_dis + 75)
    right_point = (middle_column3 + 25, y_obj_dis + 75)
    pygame.draw.line(screen, white, top_point, bottom_point, 1)
    pygame.draw.line(screen, white, left_point, right_point, 1)
    x_text = small_font.render("+X", True, white)
    y_text = small_font.render("+Y", True, white)
    screen.blit(x_text, right_point)
    screen.blit(y_text, bottom_point)
    #Z Accelerometer Line Visual
    ztop_point = (middle_column3 + 100, y_obj_dis)
    zbottom_point=(middle_column3 + 100, y_obj_dis+ 150)
    zmiddle_point = (ztop_point[0], y_obj_dis + 75)
    z_text = small_font.render("+Z", True, white)
    screen.blit(z_text, (middle_column3 + 90, y_obj_dis-30))
    pygame.draw.line(screen, white, ztop_point, zbottom_point, 1)
    y_obj_dis += 180
    accel_text = smallest_font.render(f"Ax: {A[0]},  Ay: {A[1]}, Az: {A[2]}", True, green)
    screen.blit(accel_text, (column3_xcord + 70, y_obj_dis))
    y_obj_dis += 20
    accelT_text = smallest_font.render(f"AxT: {A_T[0]},  AyT: {A_T[1]}, AzT: {A_T[2]}", True, green)
    screen.blit(accelT_text, (column3_xcord + 70, y_obj_dis))
    draw_accel_data(middle_point, zmiddle_point)
    y_obj_dis += 40
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    
    ####Device Control Render
    if (hit_index != -1):
        device_name = comb_name_list[hit_index]
        device_text = small_font.render(f"Device: {device_name}", True, green)
        device_name = device_name.lower()
        screen.blit(device_text, (middle_column3 -150,  y_obj_dis + space))
        device_xpos = middle_column3 - 70
        device_ypos =  y_obj_dis + 40
        if ("light" in device_name):
            if ("Zero" in device_name):
                if (light_0_on):
                    screen.blit(bulb_on_full_img, (device_xpos,device_ypos))
                else:
                    screen.blit(bulb_off_full_img, (device_xpos,device_ypos))
            else:
                if (light_1_on):
                    screen.blit(bulb_on_full_img, (device_xpos,device_ypos))
                else:
                    screen.blit(bulb_off_full_img, (device_xpos,device_ypos))
            
        elif ('tv' in device_name):
            screen.blit(tv_full_img, (device_xpos,device_ypos))
        elif('speaker' in device_name):
            screen.blit(speaker_full_img, (device_xpos,device_ypos))

def anchor_dis_calc():
    global dis_anchors
    dis_anchors = math.sqrt((comb_pos_list[0][0] - comb_pos_list[1][0])**2 + (comb_pos_list[0][1] - comb_pos_list[1][1])**2)

def calc_circle_radius(dist_to_plane, sphere_raduis):
    try:
        radius = math.sqrt(sphere_raduis**2 - dist_to_plane**2)
        return radius
    except:
        return 0

def tag_pos_calc():
    global predicted_pos
    try:
        dist_from_center1 = comb_pos_list[0][2] - predicted_pos[2]
        dist_from_center2 = comb_pos_list[1][2] - predicted_pos[2]
        x1, x2 = comb_pos_list[0][0], comb_pos_list[1][0]
        y1, y2 = comb_pos_list[0][1], comb_pos_list[1][1]
        r1, r2 = calc_circle_radius(dist_from_center1, anchor1_dis), calc_circle_radius(dist_from_center2, anchor2_dis)
        d = math.sqrt((x1-x2)**2 + (y1 - y2)**2)
        l = (r1**2 - r2**2 + d **2)/(2*d)
        h = math.sqrt(r1**2 - l**2)
        solution1x =  l * (x2-x1)/d  - h*(y2-y1)/d + x1
        solution1y = l * (y2-y1)/d  + h*(x2 - x1)/d + y1
        solution2x =  l * (x2-x1)/d  + h*(y2-y1)/d + x1
        solution2y = l * (y2-y1)/d  - h*(x2 - x1)/d + y1
        if (solution1x > 0 and solution1x < wall_len[0] and solution1y >0 and solution1y < wall_len[1]):
            predicted_pos[0] = solution1x
            predicted_pos[1] = solution1y
        elif (solution2x > 0 and solution2x < wall_len[0] and solution2y >0 and solution2y < wall_len[1]):
            predicted_pos[0] = solution2x
            predicted_pos[1] = solution2y
    except:
        print(f"unsolvable: anchor_dis =  {dis_anchors}, anchor1_dis = {anchor1_dis}, anchor2_dis = {anchor2_dis}")
       
def read_serial():
    global need_render, alpha, beta, gamma, A, A_T, pos_dx, pos_dy, pos_dz, anchor1_dis, anchor2_dis, ax_offset, ay_offset, az_offset, alpha_offset
    #["Time (sec)", "Alpha", "Beta", "Gamma", "Ax", "Ay", "Az", "AxT", "AyT", "AzT", "pos_dx,", "pos_dy", "pos_dz", "Anchor_1_dis", "Anchor_2_dis"]
    try:
        arduinoData = ser.readline().decode('ascii')
        print(arduinoData)
        if (str(arduinoData[:8]) == "Clicked!"):
            print("checking sight")
            check_line_of_sight(True)
        else:
            check_line_of_sight(False)
        
        serial_data_input = [float(data) for data in arduinoData.split(", ")]
        need_render = True      
        if (len(serial_data_input) == NUM_DATA_POINTS):
            #Angles
            alpha = serial_data_input[1] 
            beta = serial_data_input[2]
            gamma = serial_data_input[3]
            #Raw Accel
            A[0] = serial_data_input[4] 
            A[1] = serial_data_input[5] 
            A[2] = serial_data_input[6] 
            #Translated Accel
            A_T[0] = serial_data_input[7] 
            A_T[1] = serial_data_input[8] 
            A_T[2] = serial_data_input[9] 
            
            #Anchor Distances
            anchor1_dis = serial_data_input[-2]/39.7
            anchor2_dis = serial_data_input[-1]/39.7
            need_render = True
        elif (len(serial_data_input) == 4):
            ax_offset = serial_data_input[0]
            ay_offset = serial_data_input[1]
            az_offset = serial_data_input[2]
            alpha_offset = serial_data_input[3]
            print(f"Alpha offest = {alpha_offset} ")
        elif (len(serial_data_input) == 2):
            anchor1_dis = serial_data_input[0]/39.7
            anchor2_dis = serial_data_input[1]/39.7
        else:
            print("No Data read")
    except:
        print("No Byte")

def check_line_of_sight(clicked):
    """Check if line intersects sphere of objects in the room"""
    global X2, Y2, Z2, hit_index, light_1_on, light_0_on

    hit_index = -1
    max_hit = 0 
    alpha_i = -((alpha - alpha_offset) - 90)
    if (alpha_i <0):
        alpha_i += 360
    X1, Y1, Z1 = predicted_pos[0], predicted_pos[1], predicted_pos[2]
    ## Convert to catersian cordinates point iof raduisu 1 Make sure you add offsets to alpha here
    magx = math.cos(math.radians(alpha_i)) * math.cos(math.radians(beta))
    magy = -  math.sin(math.radians(alpha_i)) * math.cos(math.radians(beta))
    magz =  math.sin(math.radians(beta))
    X2 = predicted_pos[0]  + magx
    Y2 = predicted_pos[1] +  magy
    Z2 = predicted_pos[2] + magz
    
    for i in range(len(obj_pos_list)):
        X3, Y3, Z3 = comb_pos_list[i + 2][0],  comb_pos_list[i + 2][1],  comb_pos_list[i + 2][2]
        a = (X2 - X1) ** 2 + (Y2 - Y1)**2 + (Z2 - Z1) **2
        b = 2 * ((X2-X1)*(X1-X3) + (Y2-Y1)*(Y1-Y3) + (Z2-Z1)*(Z1-Z3))
        c = X3**2 + Y3**2 + Z3**2 + X1**2 + Y1**2 + Z1**2 - 2*(X3*X1 + Y3*Y1 + Z3*Z1) - OBJECT_RADIUS**2
        sol = b**2 - 4*a*c
        if (sol > max_hit):
            line_dir = X2-X1
            obj_dir = X3-X1
            if ((line_dir < 0 and obj_dir < 0) or (line_dir > 0 and obj_dir > 0)):
                hit_index = i + 2

    
    screen.fill(black)
    if (clicked == True):
        print("Showing click")
        ##If Clicked, Render Line of Sight
        for i in range(len(obj_pos_list)):
            devicex_pos = comb_pos_list[i + 2][0] * scale_dim + zero_cordinate[0]
            devicey_pos = comb_pos_list[i + 2][1] * scale_dim + zero_cordinate[1]
            if (hit_index == i + 2):
                pygame.draw.circle(screen, green, (devicex_pos, devicey_pos), scale_dim*OBJECT_RADIUS, width = 2)
                print(f"Hit {obj_name_list[i]} ")
            else:
                pygame.draw.circle(screen, blue, (devicex_pos, devicey_pos), scale_dim*OBJECT_RADIUS, width = 2)
        
        userx_pos = X1 * scale_dim + zero_cordinate[0]
        usery_pos = Y1 * scale_dim + zero_cordinate[1]
        p2_xpos = magx * scale_dim + userx_pos
        p2_ypos = magy * scale_dim + usery_pos
        pygame.draw.line(screen, green, (userx_pos, usery_pos), (p2_xpos, p2_ypos), 2)
        pygame.draw.circle(screen, red, (userx_pos, usery_pos ), 3, 0)
        pygame.draw.circle(screen, red, (p2_xpos, p2_ypos), 3, 0) 
        mult = 1
        #Draw Line of sight
        x_wall_dis = wall_len[0] * scale_dim
        y_wall_dis = wall_len[1] * scale_dim
        while (p2_xpos > rectx) and (p2_xpos < rectx + x_wall_dis) and (p2_ypos > recty) and (p2_ypos < recty + y_wall_dis):
            mult += 1 
            p2_xpos = magx * scale_dim * mult + userx_pos
            p2_ypos = magy * scale_dim * mult + usery_pos
        pygame.draw.line(screen, green, (userx_pos, usery_pos), (p2_xpos, p2_ypos), 2)
        #Draw points using for Line of sight
        pygame.draw.circle(screen, red, (userx_pos, usery_pos ), 3, 0)
        pygame.draw.circle(screen, red, (p2_xpos, p2_ypos), 3, 0) 

        if (hit_index == 2):
            #Light 0
            asyncio.run(toggleTape())
        elif (hit_index == 3):
            #Light One
            asyncio.run(toggleNoTape())
          
    if (calibration_mode):
        calibration_mode_render()
    else:
        active_mode_render()    
    pygame.display.update()
    if (clicked):
        time.sleep(.75)
    


###Start Everything
##Excel data 
if (USE_EXCEL):
    excel_data = pd.read_excel(EXCEL_PATH)
    data = pd.DataFrame(excel_data, columns=DATA_POINT_HEADER)
    d_index = 1
#Serial Data 
else:
    connect_serial()
#Calculate the distance of the anchors to find intersect later  
anchor_dis_calc()

while running: 
    if (USE_EXCEL):
        time.sleep(EXCEL_TIME_DIFF)
        if d_index < len(data) - 1:
            read_excel()
        d_index += 1
    else:
        read_serial()
    tag_pos_calc()
    
    if (need_render):
        screen.fill(black)  
        if (calibration_mode):
            calibration_mode_render()
        else:
            active_mode_render()
        pygame.display.update()
        need_render = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
        if event.type == pygame.KEYDOWN:
            need_render = True
            if event.key == pygame.K_c:
                calibration_mode = True
            elif event.key == pygame.K_a:
                calibration_mode = False
            elif event.key == pygame.K_1:
                calibrate_pos(1)
                anchor_dis_calc()
            elif event.key == pygame.K_2:
                calibrate_pos(2)
                anchor_dis_calc()
            elif event.key == pygame.K_3:
                calibrate_pos(3)
            elif event.key == pygame.K_4:
                calibrate_pos(4)
            elif event.key == pygame.K_5:
                calibrate_pos(5)
            elif event.key == pygame.K_6:
                calibrate_pos(6)
            elif event.key == pygame.K_7:
                calibrate_pos(7)
            elif event.key == pygame.K_m:
                print("Calibrating Magnetometer")
                
            elif event.key == pygame.K_s:
                print("Showing Anchor Dis")
                if (show_anchor_pos == False):
                    show_anchor_pos = True
                else:
                    show_anchor_pos = False
    
            elif event.key == pygame.K_t:
                if (tracking == False):
                    print("Tracking")
                    tracking = True
                else:
                    print("Stopped Tracking")
                    tracking = False
                    
            elif event.key == pygame.K_q:
                print("Clear tracking")
                tracked_pos = [[], []]

            calibration_mode_render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            move_object(user_pos = True)    

            



    

    


