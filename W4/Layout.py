import pygame

# x,y Cordinates of objects in room
Anchor1 = [0,0]
Anchor2 = [0,0]
Anchor3 = [0,0]
#Wall length X, Y
wall_len = [300, 1000]
running = True

###Sensor Data 
#Magnetometer Angle of User (0-360)
Compass = 0
#Gyroscope Angle (-90 to 90) where 0 is level to ground, 90 is up
Angle = 0
#Position
User_pos = [0,0]


white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

##display_cord Setup
wall_color = red
anchor_color = green
display_cord = [900, 600]
#how much room from right left to display compass orientation and gyro angle 
x_clearance = 300
x_dis = display_cord[0] - x_clearance
y_dis = display_cord[1]


#Initiate display_cord
pygame.init()
screen = pygame.display.set_mode((display_cord[0], display_cord[1]))


def scale_display():
    """Initilize/Scale the display based on Wall length, give scaled x/y results for future cordinate movement"""
    #if x is greater than y, scale display based on X to fill 90% of screen width
    if (wall_len[0] > wall_len[1]):
        scale_dim = x_dis * .9 / wall_len[0]
        rectx = x_dis - (.95* x_dis)
        recty = y_dis/2 - (wall_len[1] * scale_dim/2)
    else:
        scale_dim = y_dis * .9 / wall_len[1]  
        rectx = x_dis/2 - (wall_len[0] * scale_dim/2)
        recty = y_dis - (.95 * y_dis) 
    x_wall_dis = wall_len[0] * scale_dim
    y_wall_dis = wall_len[1] * scale_dim
    #Draw gyro/compass seperating lines
    pygame.draw.line(screen, white, (x_dis, 0), (x_dis, y_dis), 1)
    pygame.draw.line(screen, white, (x_dis, y_dis/2), (display_cord[0], y_dis/2), 1)
    
    #Draw Walls (corner x,y, xlen, ylen)
    pygame.draw.rect(screen, red, pygame.Rect(rectx, recty, x_wall_dis, y_wall_dis), width = 3)


scale_display()


while True:
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            running = False


    

    


