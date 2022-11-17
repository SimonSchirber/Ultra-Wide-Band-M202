import math

test_angles = [0, math.pi/2, math.pi, 3*math.pi/2, 2*math.pi]
# needs to be radians
# +x is north, +y is east, +z is down
alpha = 0   # compass rotation      0       , 2pi
beta = 0    # tilt up/down          -pi/2   , pi/2
gamma = 0   # barrel roll           -pi     , pi

ax = 1      # accelerometer reference x vector
ay = 1      # accelerometer reference y vector
az = 1      # accelerometer reference z vector

# ax is easiest
ax_x = ax * math.cos(alpha) * math.cos(beta)
ax_y = ax * math.sin(alpha) * math.cos(beta)
ax_z = -ax * math.sin(beta)
print(ax_x, ax_y, ax_z)
print(math.sqrt(ax_x ** 2 + ax_y ** 2 + ax_z ** 2))

# ay
ay_x = ay * (math.cos(alpha) * math.sin(beta) * math.cos(gamma) + math.sin(alpha) * math.cos(gamma))
ay_y = ay * (math.sin(alpha) * math.sin(beta) * math.sin(gamma) + math.cos(alpha) * math.cos(gamma))
ay_z = ay * (math.cos(beta) * math.sin(gamma))
print(ay_x, ay_y, ay_z)
print(math.sqrt(ay_x ** 2 + ay_y ** 2 + ay_z ** 2))

# az
az_x = az * (math.cos(alpha) * math.sin(beta) * math.cos(gamma) + math.sin(alpha) * math.sin(gamma))
az_y = az * (math.sin(alpha) * math.sin(beta) * math.cos(gamma) - math.cos(alpha) * math.sin(gamma))
az_z = az * math.cos(beta) * math.cos(gamma)
print(az_x, az_y, az_z)
print(math.sqrt(az_x ** 2 + az_y ** 2 + az_z ** 2))

x = ax_x + ay_x + az_x
y = ax_y + ay_y + az_y
z = ax_z + ay_z + az_z
print(x,y,z)