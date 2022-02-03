#!/usr/bin/env python3.10

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import argparse
import sys
from queue import Queue
import queue
from threading import Thread
from threading import Lock
import datetime
from enum import Enum
from numpy import array
import numpy

#Enumeration definition
class MachineState(Enum):
    OFF     = 0
    ON      = 1


"""
Parse command line arguments
"""
parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
parser.add_argument('--pin', default = 18)
parser.add_argument('--machname', default = 1)
parser.add_argument('--test', action = 'store_true')
parser.add_argument('-f')
parser.add_argument('--output', default = '/var/log/SensorWatch/MotionSensor.csv')
args = parser.parse_args()

### Global declarations
time_queue = Queue()
machine = 0
consumer_lock = Lock()
consumer_lock.acquire()

if not args.test:
    #RBPI dev related imports only if not in test mode
    from gpiozero import MotionSensor

"""
Consumer thread function
"""
def sensor_motion_consumer(output):
    print("consumer thread started")
    data = numpy.zeros(24,dtype = int)
    now = datetime.datetime.now()
        
    laston = 0
    hidx = 0
    didx = now.day
    
    while consumer_lock.locked():
        now = datetime.datetime.now()
        print(now.hour)
        try:
            item = sensor_motion_pop()
            if item[0] == MachineState.ON:
                laston = item[1]
            else:
                laston = 0
            
        except queue.Empty:
            print("timedout with empty")
            
        if now.day > didx:
            with open(output,mode="w",encoding="utf-8") as fd:
                for index in range(len(data)):
                    fd.write('{},{}'.format(index,data[index]))
            fd.close()
            
    print("consumer thread quitting")
    
th = Thread(target = sensor_motion_consumer, args = ( args.output, ))


"""
Functions that handles RBPI interrupt on PIN this functions 
adds data to queue which is processed by another thread to not 
waste time for processing in main program thread

Additional function to handle interrupt from signal HUP, TERM, INT
"""

#push current MachineState into the queue
def sensor_motion_push(state):
    ct = datetime.datetime.now()
    ts = ct.timestamp()
    time_queue.put([state,ts])
    return ts

def sensor_motion_pop():
    return time_queue.get(True,0.25)

#Interrupt handler when machine changes state to `ON`
def sensor_motion_start():
    ts = sensor_motion_push(MachineState.ON)
    print("Machine #",args.machname," ON",ts)

#Interrupt handler when machine changes state to `OFF`
def sensor_motion_end():
    ts = sensor_motion_push(MachineState.OFF)
    print("Machine #",args.machname," OFF",ts)
    

#Catch main thread interrupt to perform graceful exit
def signal_handler(signum, frame):
    print("Shutdown signal received")
    consumer_lock.release()
    th.join()
    print("exiting")
    sys.exit()
###

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
    #we have been patiently waiting until machine state is OFF
    #record that state and timestamp
    sensor_motion_push(MachineState.OFF)
    print("Sensor initialized successfully")
    machine.when_motion = sensor_motion_start
    machine.when_no_motion = sensor_motion_end
    print("Finished setup")
    
def sensor_motion_exec():
    th.start()
    pause()
    #this should never happen
    #th.join()

#Execute
if not args.test:
    sensor_motion_setup()
    
sensor_motion_exec()
