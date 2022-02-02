#!/usr/bin/env python3.10

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import argparse
import sys
from queue import Queue
from threading import Thread
import datetime

"""
Parse command line arguments
"""
parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
parser.add_argument('--pin', default = 18)
parser.add_argument('--machname', default = 1)
parser.add_argument('--test', action = 'store_true')
parser.add_argument('-f')

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
    ct = datetime.datetime.now()
    ts = ct.timestamp()
    print("timestamp:-", ts)
    print("Machine #",args.machname," ON")

#Interrupt handler when machine changes state to `OFF`
def sensor_motion_end():
    ct = datetime.datetime.now()
    ts = ct.timestamp()
    print("timestamp:-", ts)
    print("Machine #",args.machname," OFF")

#Catch main thread interrupt to perform graceful exit
def signal_handler(signum, frame):
    print("Shutdown signal received")
    #TODO store all pending data
    print("exiting")
    sys.exit()
###

### Global declarations
time_queue = Queue()
machine = MotionSensor(args.pin)

### Main thread OS signal handle
signal.signal(signal.SIGHUP,signal_handler)
signal.signal(signal.SIGINT,signal_handler)
signal.signal(signal.SIGTERM,signal_handler)

"""
Main program functions
"""
def sensor_motion_setup():
    print("Initializing sensor...")
    machine.wait_for_no_motion()
    print("Sensor initialized successfully")
    machine.when_motion = sensor_motion_start
    machine.when_no_motion = sensor_motion_end
    print("Finished setup")
    
def sensor_motion_exec():
    #TODO spawn handler
    pause()


#Execute

if not args.test:
    sensor_motion_setup()
    
sensor_motion_exec()
