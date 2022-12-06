import time
import pandas as pd
import pygame
pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([500, 500])

# Data interface
path = r"C:/Users/schir/Desktop/Code_Projects/GITHUB/Ultra-Wide-Band-M202/Main/Excel_Data/Sanity_Test_2.xlsx"
print(path)
excel_data = pd.read_excel(path)
data = pd.DataFrame(excel_data, columns=['Time (sec)', 'Ax', 'Ay', 'Az', 'AxT', 'AyT', 'AzT', 'Anchor1_dis', 'Anchor2_dis'])
print(len(data))
d_index = 1


# Tag
def circle_intersect(anch1_r, anch2_r):
    d = 138
    a = (anch1_r ** 2 - anch2_r ** 2 + d ** 2) / (2 * d)
    h = (anch1_r ** 2 - a ** 2) ** (1/2)

    return a, h


# Run until the user asks to quit
running = True
while running:
    time.sleep(.05)

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with white
    #screen.fill((170, 171, 173))

    i_x, i_y = circle_intersect(data['Anchor1_dis'][d_index], data['Anchor2_dis'][d_index])
    
    pygame.draw.circle(screen, (0, 0, 255), (i_x, i_y), 2)

    # Flip the display
    pygame.display.flip()
    if d_index < len(data) - 1:
        print(data['Time (sec)'][d_index])
        d_index += 1

# Done! Time to quit.
pygame.quit()