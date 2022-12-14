import time
import pandas as pd
import pygame
import matplotlib.pyplot as plt

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])

# Data interface
<<<<<<< HEAD
path = r"C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/Sanity_Test_2.xlsx"
print(path)
excel_data = pd.read_excel(path)
data = pd.DataFrame(excel_data, columns=['Time (sec)', 'Ax', 'Ay', 'Az', 'AxT', 'AyT', 'AzT', 'Anchor1_dis', 'Anchor2_dis'])
=======
path = r"C:\Users\James Migdal\Downloads\no_offsets_Stop_Straight_Stop_Back_Middle_Left_Right_260cm.xlsx"
print(path)
excel_data = pd.read_excel(path)
print(excel_data)
data = pd.DataFrame(excel_data, columns=['Time (sec)', "Alpha", "Beta", "Gamma", 'AxT', 'AyT', 'AzT', 'Anchor1_dis', 'Anchor2_dis'])
>>>>>>> f2d5bb4c4a4f02da5add892e3bc4e92f1961bb33
print(len(data))
d_index = 1


# Tag
def circle_intersect(anch1_r, anch2_r):
<<<<<<< HEAD
    d = 138
=======
    d = 260
>>>>>>> f2d5bb4c4a4f02da5add892e3bc4e92f1961bb33
    a = (anch1_r ** 2 - anch2_r ** 2 + d ** 2) / (2 * d)
    h = (anch1_r ** 2 - a ** 2) ** (1/2)

    return a, h


# Run until the user asks to quit
running = True
pause = False
t_arr = []
axT_arr = []
ayT_arr = []
velx = []
vely = []
while running:
    time.sleep(.02)

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_SPACE:
                if pause:
                    pause = False
                else:
                    pause = True
        elif event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    if d_index == 0:
        screen.fill((170, 171, 173))

    i_x, i_y = circle_intersect(data['Anchor1_dis'][d_index], data['Anchor2_dis'][d_index])
<<<<<<< HEAD
    
    pygame.draw.circle(screen, (0, 0, 255), (i_x, i_y), 2)
=======
    pygame.draw.circle(screen, (0, 0, int(255 * (d_index / len(data)))), (i_x, i_y), 2)
>>>>>>> f2d5bb4c4a4f02da5add892e3bc4e92f1961bb33

    # Flip the display
    pygame.display.flip()
    if d_index < len(data) - 1 and not pause:
        t = data['Time (sec)'][d_index]
        axt = data['AxT'][d_index]
        ayt = data['AyT'][d_index]
        azt = data['AzT'][d_index]
        alpha = data['Alpha'][d_index]
        beta = data['Beta'][d_index]
        gamma = data['Gamma'][d_index]
        print(f'{t} \t {axt} \t {ayt} \t {azt} \t {alpha} \t {beta} \t {gamma}')
        d_index += 1

        if len(t_arr) > 0:
            if t < t_arr[-1]:
                t_arr = []
                axT_arr = []
                ayT_arr = []
                velx = []
                vely = []
                plt.clf()

        t_arr.append(t)
        axT_arr.append(axt)
        ayT_arr.append(ayt)
        if len(t_arr) > 1:
            velx.append( (t_arr[-1] - t_arr[-2]) * axt + velx[-1] )
            vely.append( (t_arr[-1] - t_arr[-2]) * ayt + vely[-1] )
        else:
            velx.append(0)
            vely.append(0)

        #if len(t_arr) > 10:
        #    axt_ref = axT_arr[-1]
        #    ayt_ref = ayT_arr[-1]
        #    axt_zero = True
        #    ayt_zero = True
        #    for i in range(8):
        #        if abs(axT_arr[-(i+2)] - axt_ref) > 0.1:
        #            axt_zero = False
        #        if abs(ayT_arr[-(i+2)] - ayt_ref) > 0.1:
        #            ayt_zero = False

        #    if axt_zero:
        #        velx[-1] = 0

        #    if ayt_zero:
        #        vely[-1] = 0

        #else:
        #    velx[-1] = 0
        #    vely[-1] = 0


        #plt.subplot(2, 2, 1)
        #plt.plot(t_arr, axT_arr)
        #plt.subplot(2, 2, 2)
        #plt.plot(t_arr, ayT_arr)
        #plt.subplot(2, 2, 3)
        #plt.plot(t_arr, velx)
        #plt.subplot(2, 2, 4)
        #plt.plot(t_arr, vely)
        #plt.pause(0.01)
        #plt.show()



# Done! Time to quit.
pygame.quit()
