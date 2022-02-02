from gpiozero import MotionSensor
from signal import pause
import time

machine_one = MotionSensor(18)

def start_motion():
    print("Machine #1 ON")

def end_motion():
    print("Machine #1 OFF")
    
print("Initializing sensor...")
machine_one.wait_for_no_motion()
print("Sensor initialized successfully")

machine_one.when_motion = start_motion
machine_one.when_no_motion = end_motion

pause()
