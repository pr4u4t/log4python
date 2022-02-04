#!/usr/bin/env python3

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
import socket
import threading
import socketserver

#Enumeration definition
class MachineState(Enum):
    OFF     = 0
    ON      = 1

"""
Lock and inter process communication 
"""
class ThreadedStreamRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        pass
    
    def handle(self):
        print("Handling connection")
        data = str(self.request.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.request.sendall(response)
        
    def finish():
        pass

class ThreadedStreamServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    pass




class Application:
    def __init__(self):
        ### Global declarations
        time_queue = Queue()
        machine = MotionSensor(args.pin) if not args.test else 0
        consumer_lock = Lock()
        consumer_lock.acquire()
        th = Thread(target = sensor_motion_consumer, args = ( args.output, args.resolution, args.machname))

    """
    Parse command line arguments
    """
    def parse_argumnets(self):
        print("Parsing command line arguments")
        parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
        parser.add_argument('--pin', default = 18, help = "number of PIN to which sensor is connected")
        parser.add_argument('--machname', default = 1, help = "identifier of machine used in csv file title")
        parser.add_argument('--test', action = 'store_true', help = "run the program in test mode")
        parser.add_argument('-f', help = "bulk option for jupyter")
        parser.add_argument('--output', default = '/var/log/SensorWatch', help = "program storage directory")
        parser.add_argument('--resolution', default = 0.25, help = "consumer thread timer resolution")
        return parser.parse_args()

    def check_env(self):
        print("")
        if not args.test:
            #RBPI dev related imports only if not in test mode
            from gpiozero import MotionSensor

        #check and create if necessary instance directory
        if not os.path.isdir(args.output):
            print("CSV storage path:",args.output,"does not exists or is not a directory")
            print("Please create it using `sudo mkdir",args.output,"`")
            sys.exit()
            return False

        if not os.access(args.output, os.W_OK):
            print("CSV storage directory:",args.output,"is not writeable")
            print("Please change ownership of this directory using: `sudo chown {}:{} {}`".format(getpass.getuser(),getpass.getuser(),args.output))
            print("also change permission of this directory using: `sudo chmod 750 {}`".format(args.output))
            sys.exit()
            return False
        
        if not os.path.isdir(os.path.join(args.output, "machine_{}".format(args.machname))):
            os.mkdir(os.path.join(args.output, "machine_{}".format(args.machname)))
    
    #Catch main thread interrupt to perform graceful exit
    def signal_handler(self,signum, frame):
        print("Shutdown signal received")
        consumer_lock.release()
        th.join()
        print("exiting")
        sys.exit()
    ###

    def signal_setup(self):
        print("Performing signal handler setup")
        ### Main thread OS signal handle
        signal.signal(signal.SIGHUP,signal_handler)
        signal.signal(signal.SIGINT,signal_handler)
        signal.signal(signal.SIGTERM,signal_handler)
        
    def sensor_motion_exec():
        th.start()
        pause()
        #this should never happen
        #th.join()


class MotionSensor:
    def __init__(self):
        

    def tofile(self,output,machname,data):
        print("Writing uptime statistics to file {}".format(output))
        total = 0
        with open(output,mode="w",encoding="utf-8") as fd:
            fd.write("Machine name, {}\r\n".format(machname))
            fd.write("Hour, Uptime\r\n")
            for index in range(len(data)):
                total += data[index]
                fd.write("{}, {:.2f}\r\n".format(index,data[index]))
            fd.write("Total, {:.2f}\r\n".format(total))
        fd.close()

    def tostdout(self,machname,data):
        print("Writing uptime statistics to stdout")
        total = 0
        print("Machine name, {}".format(machname))
        print("Hour, Uptime")
        for index in range(len(data)):
            total += data[index]
            print("{}, {:.2f}".format(index,data[index]))
        print("Total, {:.2f}".format(total))

    """
    Consumer thread function
    """
    def consumer(self,output, resolution, machname):
        print("consumer thread started")
        data = numpy.zeros(24)
        now = datetime.datetime.now()
            
        laston = 0
        hidx = now.hour
        didx = now.day
        
        while consumer_lock.locked():
            now = datetime.datetime.now()
            try:
                item = sensor_motion_pop(resolution)
                print("POPED: {}".format(item))
                if item[0] == MachineState.ON:
                    print("machine state changed to ON")
                    laston = item[1]
                else:
                    print("machine state changed to OFF")
                    if laston != 0:
                        print("making calculation")
                        data[hidx] += ((now.timestamp() - laston)/60)
                    laston = 0
                    
            except queue.Empty:
                #pretend nothing happend
                pass
            
            if now.hour != hidx:
                print("Hour changed")
                if laston != 0:
                    data[hidx] += ((now.timestamp() - laston)/60)
                    laston = now.timestamp()
                #switch index to next hour
                hidx = now.hour
                
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
    
    """
    Functions that handles RBPI interrupt on PIN this functions 
    adds data to queue which is processed by another thread to not 
    waste time for processing in main program thread

    Additional function to handle interrupt from signal HUP, TERM, INT
    """

    #push current MachineState into the queue
    def motion_push(state):
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        time_queue.put([state,ts])
        return ts

    def motion_pop(resolution = 0.25):
        return time_queue.get(True,resolution)

    #Interrupt handler when machine changes state to `ON`
    def sensor_motion_start():
        ts = sensor_motion_push(MachineState.ON)
        print("Machine #",args.machname," ON",ts)

    #Interrupt handler when machine changes state to `OFF`
    def sensor_motion_end():
        ts = sensor_motion_push(MachineState.OFF)
        print("Machine #",args.machname," OFF",ts)
    
    """
    Main program functions
    """
    def setup():
        print("Initializing sensor...")
        machine.wait_for_no_motion()
        #we have been patiently waiting until machine state is OFF
        #record that state and timestamp
        sensor_motion_push(MachineState.OFF)
        print("Sensor initialized successfully")
        machine.when_motion = sensor_motion_start
        machine.when_no_motion = sensor_motion_end
        print("Finished setup")
    


#args = parse_arguments()
#
#Execute
#if not args.test:
#    sensor_motion_setup()
#    
#sensor_motion_exec()
