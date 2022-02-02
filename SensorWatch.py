#!/usr/bin/env python2.7

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import argparse
import sys
from Queue import Queue
from threading import Thread

"""
Parse command line arguments
"""
parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
parser.add_argument('--pin', default = 18)
parser.add_argument('--machname', default = 1)
parser.add_argument('--test', action = 'store_true')
args = parser.parse_args()

if not args.test:
    #RBPI dev related imports only if not in test mode
    from gpiozero import MotionSensor

"""
Functions that handles RBPI interrupt on PIN this functions 
adds data to queue which is processed by another thread to not 
waste time for processing in main program thread

Additional function to handle interrupt from signal HUP, TERM, INT
"""
#Interrupt handler when machine changes state to `ON`
def sensor_motion_start():
    print("Machine #",args.machname," ON")

#Interrupt handler when machine changes state to `OFF`
def sensor_motion_end():
    print("Machine #",args.machname," OFF")

#Catch main thread interrupt to perform graceful exit
def signal_handler(signum, frame):
    print("Shutdown signal received")
    #TODO store all pending data
    print("exiting")
    sys.exit()
###

### Global Queue declaration
time_queue = Queue()
### Main thread OS signal handle
signal.signal(signal.SIGHUP,signal_handler)
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)

"""
Main program functions
"""
def sensor_motion_setup():
    machine = MotionSensor(args.pin)    
    print("Initializing sensor...")
    machine.wait_for_no_motion()
    print("Sensor initialized successfully")
    machine.when_motion = start_motion
    machine.when_no_motion = end_motion

def sensor_motion_exec():
    #TODO spawn handler
    pause()


#Execute

if not args.test:
    sensor_motion_setup()
    
sensor_motion_exec()
