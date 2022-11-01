import pygame
import math
import os

# from pyparsing import And

######Calibration/Room Setup########
#Room wall length dimension (X, Y) in meters
wall_len = [20, 15]
#Anchors: Known Cordinates (x,y, z) in room (m) where 0,0,0 is top left corner in diplay
Anchor1 = [5.29, 11.54, 29.52]
Anchor2 = [14.32, 3.56, 5.93]
anchor_pos_list = [Anchor1, Anchor2]
anchor_name_list = ["Anchor1", "Anchor2"]
#Smart Device objects
object1 = [3.01, 7.56, 8.31]
object2 = [4.39, 7.82, 2.78]
obj_pos_list = [object1, object2]
obj_name_list = ["Smart Light", "Smart TV"]
comb_pos_list = [Anchor1, Anchor2, object1, object2]
comb_name_list = ["Anchor1", "Anchor2", "Smart Light", "Smart TV"]
#Magnetometer calibration to which was is north facing in the room
north_angle = 3*math.pi/4

###########Sensor Data Readings#############
#Magnetometer Angle
mag_angle = 0
#Gyroscope Readings (Gx, Gy, Gz)
G = [10, 5.26, -1.3]
#Accelerometer Readings(Ax, Ay, Az)
A = [32.5, 72.97, 32.56]
#Anchor Relatives Distances from tag (one dist reading/anchor)
anchor_dist_list = [5.45, 10.3]

#####Predictions#####
#User Predicted Position (Tag Position, x, y, z)
predicted_pos = [0, 0, 0]
predicted_device = "Smart Light"

######Pygame Display Settings####
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
grey = (110,110,110)
black = (0,0,0)
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
light_on = True
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

#Pygame Images
anchor_img = pygame.image.load(images_dir + "\\anchor.png").convert_alpha()
anchor_img = pygame.transform.rotozoom(anchor_img, 0., .05)
bulb_img = pygame.image.load(images_dir + "\\bulb.png").convert_alpha()
bulb_img = pygame.transform.rotozoom(bulb_img, 0., .12)
tv_img = pygame.image.load(images_dir + "\\tv.png").convert_alpha()
tv_img = pygame.transform.rotozoom(tv_img, 0., .05)
user_tag_img = pygame.image.load(images_dir + "\\user.png").convert_alpha()
user_tag_img = pygame.transform.rotozoom(user_tag_img, 0., .05)


def calibrate_pos(object_number):
    global predicted_pos
    global comb_pos_list

    if (object_number == len(comb_pos_list)+ 1):
        try:
            x = float(input("X position(m) of User: "))
            if not(x > 0 and x < wall_len[0]):
                raise ValueError("Not in x wall range")
            y = float(input("Y position(m) of User: "))
            if not(x > 0 and x < wall_len[1]):
                raise ValueError("Not in Y wall range")
            predicted_pos[0] = x
            predicted_pos[1] = y
            predicted_pos[2] = float(input("Z position(m) of User: "))
        except:
            print("Not a valid input")
    else:
        object_number -= 1
        try:
            comb_pos_list[object_number][0] = float(input(f"X position(m) of {comb_name_list[object_number]}: "))
            comb_pos_list[object_number][1] = float(input(f"Y position(m) of Object {comb_name_list[object_number]}: "))
            comb_pos_list[object_number][2] = float(input(f"Z position(m) of Object {comb_name_list[object_number]}: "))
        except:
            print("Not a valid input")
    
def draw_mag_line(line_angle, color, radius):
    """Draw the lines that move the magnetometer/compass"""
    xcenter_mag = (width_column1 + column3_xcord)/2
    ycenter_mag =  length_display*.5
    xouter_mag = xcenter_mag + radius * math.cos(line_angle)
    youter_mag = ycenter_mag + radius * math.sin(line_angle)
    pygame.draw.line(screen, color, (xcenter_mag, ycenter_mag), (xouter_mag, youter_mag), 2)
    pygame.draw.circle(screen, black, (xcenter_mag, ycenter_mag), 5, 0)
    pygame.draw.circle(screen, color, (xouter_mag, youter_mag), 5, 0)

def render_smart_light(light_id):
    print("rendering")
    
def toggle_smart_light():
    global light_on 
    light_on = not light_on

def display_setup():
    """Draw Room Display and Initiate Column Lines and Room display"""
    #Vertical Column Lines
    pygame.draw.line(screen, white, (width_column1, 0), (width_column1, length_display), 1)
    pygame.draw.line(screen, white,(column3_xcord, 0), (column3_xcord, length_display), 1)
    ########  First Column (Room Display)  ############
    #Scale Room to fit Screen: Check if x dimonsion is greater than y, scale display based on X to fill 90% of screen width
    global zero_cordinate
    global scale_dim
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
    #Add dimension count
    xwall_text = small_font.render(f"{wall_len[0]}m", True, red)
    ywall_text = small_font.render(f"{wall_len[1]}m", True, red)
    ywall_text = pygame.transform.rotate(ywall_text, 90)
    screen.blit(xwall_text, (rectx + x_wall_dis/2 - 30, recty - 35))
    screen.blit(ywall_text, (rectx - 35, recty + (y_wall_dis/2) - 30))
    zero_cordinate_text = smallest_font.render("(0,0)", True, red)
    screen.blit(zero_cordinate_text, (rectx - 20, recty - 20))

def calibration_mode_render():
    #########1st Column#######

    for anchor in range(len(anchor_pos_list)):
        anchorx_pos  = anchor_pos_list[anchor][0] * scale_dim + zero_cordinate[0]
        anchory_pos = anchor_pos_list[anchor][1] * scale_dim + zero_cordinate[1]
        screen.blit(anchor_img, (anchorx_pos, anchory_pos))
        pygame.draw.circle(screen, green, (anchorx_pos, anchory_pos), 2, 0)
    for device in range(len(obj_pos_list)):
        devicex_pos = obj_pos_list[device][0] * scale_dim + zero_cordinate[0]
        devicey_pos = obj_pos_list[device][1] * scale_dim + zero_cordinate[1]
        device_name = obj_name_list[device].lower()
        if ("light" in device_name):
            screen.blit(bulb_img, (devicex_pos,devicey_pos))
        elif ('tv' in device_name):
            screen.blit(tv_img, (devicex_pos,devicey_pos))
        pygame.draw.circle(screen, green, (devicex_pos, devicey_pos), 2, 0)
    userx_pos = predicted_pos[0] * scale_dim + zero_cordinate[0]
    usery_pos = predicted_pos[1] * scale_dim + zero_cordinate[1]
    screen.blit(user_tag_img, (userx_pos, usery_pos))
    pygame.draw.circle(screen, green, (userx_pos, usery_pos), 2, 0)
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
    calibrate_text = smallest_font.render("Recalibrate Posiiton ->", True, green)
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
    gyro_text = smallest_font.render("Calibrate Gyro", True, green)
    gyrokey_text = small_font.render("G", True, green)
    screen.blit(gyro_text, (column2_divider + space, y2_dis + space))
    screen.blit(gyrokey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    accel_text = smallest_font.render("Calibrate Accelerometer", True, green)
    accelkey_text = small_font.render("D", True, green)
    screen.blit(accel_text, (column2_divider + space, y2_dis + space))
    screen.blit(accelkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    mag_text = smallest_font.render("Calibrate Mag", True, green)
    magkey_text = small_font.render("M", True, green)
    screen.blit(mag_text, (column2_divider + space, y2_dis + space))
    screen.blit(magkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    uwb_text = smallest_font.render("Calibrate UWB (2m)", True, green)
    uwbkey_text = small_font.render("U", True, green)
    screen.blit(uwb_text, (column2_divider + space, y2_dis + space))
    screen.blit(uwbkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    tag_text = smallest_font.render("show UWB tag pos guess", True, green)
    tagkey_text = small_font.render("G", True, green)
    screen.blit(tag_text, (column2_divider + space, y2_dis + space))
    screen.blit(tagkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))
    reconnect_text = smallest_font.render("Reconnect tag", True, green)
    reconnectkey_text = small_font.render("R", True, green)
    screen.blit(reconnect_text, (column2_divider + space, y2_dis + space))
    screen.blit(reconnectkey_text, (width_column1 + space, y2_dis + space))
    y2_dis += obj_space
    pygame.draw.line(screen, white, (width_column1, y2_dis ), (column3_xcord,y2_dis))

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
        if (obj_num ==  len(comb_pos_list) - 1):
            y_obj_dis = (2 + obj_num) * obj_space
            pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
            pygame.draw.line(screen, white, (xobj_text_dis-space, 0), (xobj_text_dis-space, y_obj_dis), 1)
            pygame.draw.line(screen, white, (yobj_text_dis- space, 0), (yobj_text_dis-space, y_obj_dis), 1)
            pygame.draw.line(screen, white, (zobj_text_dis- space, 0), (zobj_text_dis-space, y_obj_dis), 1)

def active_mode_render():

    """Draw Second and Third Column Sensor maps for active mode"""
    ########  Second Column  ########
    #Column 2 Horizaontal Line Dividers
    pygame.draw.line(screen, white, (width_column1, length_display/3), (column3_xcord, length_display/3), 1)
    pygame.draw.line(screen, white, (width_column1, length_display*2/3), (column3_xcord, length_display*2/3), 1)
    column_head_pos = width_column1 + 30
    ####Gyroscope
    gyro_text = small_font.render("Gyroscope (Tilt)", True, green)
    screen.blit(gyro_text, (column_head_pos, space))
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
    tilt_text = smallest_font.render("GX: " + str(G[0]) + ",  GY: " + str(G[1]) + ",  GZ: " + str(G[2]), True, green)
    screen.blit(tilt_text,(width_column1 + 15 ,obj_space + 155))
    ###Magnetometer
    mag_text = small_font.render('Magnetometer', True, green)
    angle_text = small_font.render(f"Angle: {mag_angle}", True, green)
    screen.blit(mag_text, (width_column1 + 30,  length_display/3 + space))
    radius_mag = length_display*1/9
    pygame.draw.circle(screen, grey, ((width_column1 + column3_xcord)/2, length_display * .5), radius_mag, 0) 
    pygame.draw.circle(screen, white, ((width_column1 + column3_xcord)/2, length_display * .5), radius_mag, 3)
    draw_mag_line(north_angle, red, radius_mag)
    draw_mag_line(mag_angle, green, radius_mag)
    screen.blit(angle_text, (width_column1 +60, 2/3*length_display - 35))
    ###Predictions
    prediction_text = small_font.render('Predictions', True, green)
    x_pred_text = small_font.render(f'X(m): {predicted_pos[0]}', True, green)
    y_pred_text = small_font.render(f'Y(m): {predicted_pos[1]}', True, green)
    z_pred_text = small_font.render(f'Z(m): {predicted_pos[2]}', True, green)
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
        tag_dist_text = small_font.render(str(anchor_dist_list[anchor]), True, green)
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
    z_text = small_font.render("+Z", True, white)
    screen.blit(z_text, (middle_column3 + 90, y_obj_dis-30))
    pygame.draw.line(screen, white, ztop_point, zbottom_point, 1)
    y_obj_dis += 180
    accel_text = smallest_font.render(f"Ax: {A[0]},  Ay: {A[1]}, Az: {A[2]}", True, green)
    screen.blit(accel_text, (column3_xcord + 70, y_obj_dis))
    y_obj_dis += 40
    pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    ####Device Control
    device_text = small_font.render(f"Device: {predicted_device}", True, green)
    screen.blit(device_text, (middle_column3 -150,  y_obj_dis + space))
    light_img = pygame.image.load("C:\\Users\\schir\\Desktop\\Code_Projects\\GITHUB\\Ultra-Wide-Band-M202\\Main\\Images\\bulb_on.png").convert_alpha()
    light_img = pygame.transform.rotozoom(light_img, 0, .40)
    screen.blit(light_img, (middle_column3 - 150 , y_obj_dis + 40))

while running: 
    if (need_render):
        screen.fill(black)
        display_setup()  
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
            elif event.key == pygame.K_2:
                calibrate_pos(2)
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
            elif event.key == pygame.K_g:
                calibrate_pos(7)
            elif event.key == pygame.K_d:
                calibrate_pos(7)
            elif event.key == pygame.K_m:
                calibrate_pos(7)
            elif event.key == pygame.K_u:
                calibrate_pos(7)
            elif event.key == pygame.K_g:
                calibrate_pos(7)
            elif event.key == pygame.K_r:
                calibrate_pos(7)
            calibration_mode_render()
            

            



    

    


