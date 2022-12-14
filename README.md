# Ultra-Wide-Band-M202
Using UWB and IMU measurements to aide in localization.

Code/resources that are finalized to be shared and tested is put in main folder.
All other weekly research and development and code forks in progress are put into the corresponding "WX" folder


# How to run

Navigate to the "Main" Folder and read the "Readme.md" instrunctions 




# To Do
- Soldering for UWB chip/Dev Board 
    Dev Board = ESP32 UWB DW3000(Ultra Wideband), WROVER core)
    Dev Specs: https://www.makerfabs.com/esp32-uwb-dw3000.html
- Run initial tests to see that UWB is working with arduino:
    Github Example: https://github.com/Makerfabs/Makerfabs-ESP32-UWB-DW3000
    Calibration: https://www.makerfabs.cc/article/esp32-uwb-antenna-delay-calibrating.html
    2 Anchor Distance Calculations:  
    Youtube Example: https://www.youtube.com/watch?v=OG3cMSpVonk&list=WL&index=8&t=207s
- Decide how many tags using
    - 1 versus 2 tag in 2D plane or 3d space assumption
- Sensor orientation fusion: magnetometer,accelerometer, gyroscope  
    - Matlab or what are we using to display?
    - may be easier/cheaper to buy I2C to hook up to dev board 
    - should we buy  MPU9250 or other option: Just got (Adafruit 9-DOF Absolute Orientation IMU Fusion Breakout)
    - https://www.youtube.com/watch?v=0rlvvYgmTvI&list=PLirRO_7kjRkxWDF-lFMNvZNWQDvqWO2xd&index=1&t=299s

- Decide how implementing state based on Kallman filter
    looking at gyroscope + IMU?? if so how are we choosing and updating, how many samples/observations in past are we doing?
- Make sure we have fast enough bluetooth connection
    - can python connect and read from the device fast enough from bluetooth, Will we have to use seiral connection
- Set up smart device connection
    Add scripts to control smart lights
- Update python GUI to be functional (track user based on assumed position, show smart devices, calibrate function)
    - add all additional calculations needed
- Come up with test plan to measure accuracy of assumed location/orientation and intention to control device