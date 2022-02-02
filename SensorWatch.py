#!/usr/bin/env python2.7

from Queue import Queue
from threading import Thread
import time
from signal import pause
import argparse
import sys

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
"""
#Interrupt handler when machine changes state to `ON`
def sensor_motion_start():
    print("Machine #1 ON")

#Interrupt handler when machine changes state to `OFF`
def sensor_motion_end():
    print("Machine #1 OFF")
###

"""
Main program functions
"""
def sensor_motion_setup():
    machine_one = MotionSensor(pin)    
    print("Initializing sensor...")
    machine_one.wait_for_no_motion()
    print("Sensor initialized successfully")
    machine_one.when_motion = start_motion
    machine_one.when_no_motion = end_motion

def sensor_motion_exec():
    #TODO spawn handler
    pause()
