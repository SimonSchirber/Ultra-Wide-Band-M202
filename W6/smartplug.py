from tplinkcloud import TPLinkDeviceManager
import asyncio
import os
from dotenv import load_dotenv
import time

##KASA Connect Login
load_dotenv()
username = os.getenv("kasausername")
password = os.getenv("password")

device_manager = TPLinkDeviceManager(username, password)

##########Toglle Tape Plug#######
#Toggle 
async def toggleTape():
    device_name = "Tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Toggling {device_name}')
        await device.toggle()
    else:  
        print(f'Could not find {device_name}')

#Turn on 
async def TurnOnTape():
    device_name = "Tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Turning On {device_name}')
        await device.power_on()
    else:  
        print(f'Could not find {device_name}')
#Turn off
async def TurnOffTape():
    device_name = "Tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Turning Off {device_name}')
        await device.power_off()
    else:  
        print(f'Could not find {device_name}')

###################No tape Plug##############
#Toggle 
async def toggleNoTape():
    device_name = "No tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Toggling {device_name}')
        await device.toggle()
    else:  
        print(f'Could not find {device_name}')

#Turn on 
async def TurnOnNoTape():
    device_name = "No tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Turning On {device_name}')
        await device.power_on()
    else:  
        print(f'Could not find {device_name}')
#Turn off
async def TurnOffNoTape():
    device_name = "No tape (UCLA)"
    device = await device_manager.find_device(device_name)
    if device:
        #print(f'Found {device.model_type.name} device: {device.get_alias()}')
        print(f'Turning Off {device_name}')
        await device.power_off()
    else:  
        print(f'Could not find {device_name}')

asyncio.run(toggleTape())
asyncio.run(toggleNoTape())
time.sleep(1)
asyncio.run(toggleTape())
asyncio.run(toggleNoTape())
