# How to run

1. To Run this code, you  need to install the DWM3000 library into arduino found at https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000
2. Next Upload the "Anchor 1" file to the first anchor , and the "Anchor 2" file to the second anchor (make sure they are labeled)
3. Upload the Initiator IMU_UWB Stream to the controller 
4. Connect the controlller to your pc and then in python run the "Layout.py" script
5. Press and hold the button on the controller to calibrate it facing north (straight towards 0,0)
6. To change the dimensions of the room, press c to calibrate and enter in the dimnsions of x and y
7. To change the position of the anchors and smart objects you can press "c" to enter into calibration mode and either click to move the objects (nake sure anchor 1 is in the corner at position 0,0 and anchor two is somewhere along the the adjacent wall)
8. After calibration is done the objects should render in the screen when pointed to, and your posisition should be tracked

