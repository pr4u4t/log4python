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
import os.path
import getpass

#Enumeration definition
class MachineState(Enum):
    OFF     = 0
    ON      = 1


"""
Parse command line arguments
"""
parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
parser.add_argument('--pin', default = 18, help = "number of PIN to which sensor is connected")
parser.add_argument('--machname', default = 1, help = "identifier of machine used in csv file title")
parser.add_argument('--test', action = 'store_true')
parser.add_argument('-f')
parser.add_argument('--output', default = '/var/log/SensorWatch/MotionSensor.csv')
parser.add_argument('--resolution', default = 0.25, help = "consumer thread timer resolution")
args = parser.parse_args()

### Global declarations
time_queue = Queue()
machine = 0
consumer_lock = Lock()
consumer_lock.acquire()

if not args.test:
    #RBPI dev related imports only if not in test mode
    from gpiozero import MotionSensor

def sensor_motion_tofile(output,machname,data):
    print("Writing uptime statistics to file {}".format(output))
    total = 0
    with open(output,mode="w",encoding="utf-8") as fd:
        fd.write("Machine name, {}\r\n".format(machname))
        fd.write("Hour, Uptime\r\n")
        for index in range(len(data)):
            total += data[index]
            fd.write("{}, {}\r\n".format(index,data[index]))
        fd.write("Total, {}\r\n".format(total))
        fd.close()

def sensor_motion_tostdout(machname,data):
    print("Writing uptime statistics to stdout")
    total = 0
    print("Machine name, {}".format(machname))
    print("Hour, Uptime")
    for index in range(len(data)):
        total += data[index]
        print("{}, {}".format(index,data[index]))
    print("Total, {}".format(total))

"""
Consumer thread function
"""
def sensor_motion_consumer(output, resolution, machname):
    print("consumer thread started")
    data = numpy.zeros(24,dtype = int)
    now = datetime.datetime.now()
        
    laston = 0
    hidx = now.hour
    didx = now.day
    
    while consumer_lock.locked():
        now = datetime.datetime.now()
        
        try:
            item = sensor_motion_pop()
            if item[0] == MachineState.ON:
                print("machine state changed to ON")
                laston = item[1]
            else:
                print("machine state changed to OFF")
                laston = 0
                #
            
        except queue.Empty:
            #pretend nothing happend
            pass
        
        if now.hour != hidx:
            print("Hour changed")
            #switch index to next hour
            hidx = now.hour
            if laston != 0:
                laston = now.timestamp()
        
        if now.day != didx:
            print("Day changed")
            sensor_motion_tofile(output,machname,data)
            #reset data and start all over again
            data = numpy.zeros(24,dtype = int)
            #switch index to next day and 0 hour
            didx = now.day
            hidx = now.hour #this probably be 0 
            
    print("consumer thread quitting")
    sensor_motion_tostdout(machname,data)
    
th = Thread(target = sensor_motion_consumer, args = ( args.output, args.resolution, args.machname))

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
if not os.path.isdir(os.path.dirname(args.output)):
    print("CSV storage path:",os.path.dirname(args.output),"does not exists or is not a directory")
    print("Please create it using `sudo mkdir",os.path.dirname(args.output),"`")
    sys.exit()

if not os.access(os.path.dirname(args.output), os.W_OK):
    print("CSV storage directory:",os.path.dirname(args.output),"is not writeable")
    print("Please change ownership of this directory using: `sudo chown {}:{} {}`".format(getpass.getuser(),getpass.getuser(),os.path.dirname(args.output)))
    print("also change permission of this directory using: `sudo chmod 750 {}`".format(os.path.dirname(args.output)))
    sys.exit()

if not args.test:
    sensor_motion_setup()
    
sensor_motion_exec()
