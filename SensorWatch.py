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
import configparser

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
        print("New Application instance")
        self.args = self.parse_arguments()
        self.check_env()
        self.signal_setup()
        self.sensor = PiMotionSensor(self.args)
        self.sensor.start()
        
    def create_sensor(self):
        pass
    
    def read_configuration(self):
        pass
    
    """
    Parse command line arguments
    """
    def parse_arguments(self):
        print("Parsing command line arguments")
        
        parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
        parser.add_argument('--pin', default = 18, help = "number of PIN to which sensor is connected")
        parser.add_argument('--machname', default = 1, help = "identifier of machine used in csv file title")
        parser.add_argument('--test', action = 'store_true', help = "run the program in test mode")
        parser.add_argument('-f', help = "bulk option for jupyter")
        parser.add_argument('--output', default = '/var/log/SensorWatch', help = "program storage directory")
        parser.add_argument('--resolution', default = 0.25, help = "consumer thread timer resolution")
        parser.add_argument('--sensor', default = 'MotionSensor', help = "")
        
        return parser.parse_args()

    def check_env(self):
        print("Checking environment")
        #check and create if necessary instance directory
        if not os.path.isdir(self.args.output):
            print("CSV storage path:",self.args.output,"does not exists or is not a directory")
            print("Please create it using `sudo mkdir",self.args.output,"`")
            return False

        if not os.access(self.args.output, os.W_OK):
            print("CSV storage directory:",self.args.output,"is not writeable")
            print("Please change ownership of this directory using: `sudo chown {}:{} {}`".format(getpass.getuser(),getpass.getuser(),self.args.output))
            print("also change permission of this directory using: `sudo chmod 750 {}`".format(self.args.output))
            return False
        
        if not os.path.isdir(os.path.join(self.args.output, "machine_{}".format(self.args.machname))):
            os.mkdir(os.path.join(self.args.output, "machine_{}".format(self.args.machname)))
        return True
    
    #Catch main thread interrupt to perform graceful exit
    def signal_handler(self,signum, frame):
        print("Shutdown signal received")
        self.sensor.stop()
        print("exiting")
        sys.exit()
    ###

    def signal_setup(self):
        print("Performing signal handler setup")
        ### Main thread OS signal handle
        signal.signal(signal.SIGHUP,self.signal_handler)
        signal.signal(signal.SIGINT,self.signal_handler)
        signal.signal(signal.SIGTERM,self.signal_handler)
        
    def run(self):
        print("Application Run")
        pause()
        #this should never happen
        #th.join()

class PiSensor:
    def __init__(self):
        pass

class PiMotionSensor:
    def __init__(self,args):
        self.time_queue = Queue()
        self.consumer_lock = Lock()
        self.consumer_lock.acquire()
        self.args = args
        self.data = numpy.zeros(24)
        
        if not args.test:
            #RBPI dev related imports only if not in test mode
            from gpiozero import MotionSensor
            self.sensor = MotionSensor(args.pin)
            self.setup()
        
        self.th = Thread(target = self.consumer, args = ( os.path.join(self.args.output, "machine_{}/data.csv".format(self.args.machname)), args.resolution, args.machname))

    def stop(self):
        self.consumer_lock.release()
        if not self.args.test:
            self.th.join()

    def start(self):
        self.th.start()

    def to_file(self):
        print("Writing uptime statistics to file {}".format(self.args.output))
        total = 0
        with open(self.args.output,mode="w",encoding="utf-8") as fd:
            fd.write("Machine name, {}\r\n".format(self.args.machname))
            fd.write("Hour, Uptime\r\n")
            for index in range(len(self.data)):
                total += self.data[index]
                fd.write("{}, {:.2f}\r\n".format(index,self.data[index]))
            fd.write("Total, {:.2f}\r\n".format(total))
        fd.close()

    def to_stdout(self):
        print("Writing uptime statistics to stdout")
        total = 0
        print("Machine name, {}".format(self.args.machname))
        print("Hour, Uptime")
        for index in range(len(self.data)):
            total += self.data[index]
            print("{}, {:.2f}".format(index,self.data[index]))
        print("Total, {:.2f}".format(total))

    """
    Consumer thread function
    """
    def consumer(self,output, resolution, machname):
        print("consumer thread started")
        
        now = datetime.datetime.now()
        laston = 0
        hidx = now.hour
        didx = now.day
        
        while self.consumer_lock.locked():
            now = datetime.datetime.now()
            try:
                item = self.motion_pop(resolution)
                print("POPED: {}".format(item))
                if item[0] == MachineState.ON:
                    print("machine state changed to ON")
                    laston = item[1]
                else:
                    print("machine state changed to OFF")
                    if laston != 0:
                        print("making calculation")
                        self.data[hidx] += ((now.timestamp() - laston)/60)
                    laston = 0
                    
            except queue.Empty:
                #pretend nothing happend
                pass
            
            if now.hour != hidx:
                print("Hour changed")
                if laston != 0:
                    self.data[hidx] += ((now.timestamp() - laston)/60)
                    laston = now.timestamp()
                #switch index to next hour
                hidx = now.hour
                
            if now.day != didx:
                print("Day changed")
                self.to_file()
                #reset data and start all over again
                self.data = numpy.zeros(24,dtype = int)
                #switch index to next day and 0 hour
                didx = now.day
                hidx = now.hour #this probably be 0 
                
        print("consumer thread quitting")
        self.to_stdout()
    
    """
    Functions that handles RBPI interrupt on PIN this functions 
    adds data to queue which is processed by another thread to not 
    waste time for processing in main program thread

    Additional function to handle interrupt from signal HUP, TERM, INT
    """

    #push current MachineState into the queue
    def motion_push(self,state):
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        self.time_queue.put([state,ts])
        return ts

    def motion_pop(self,resolution = 0.25):
        return self.time_queue.get(True,resolution)

    #Interrupt handler when machine changes state to `ON`
    def motion_start(self):
        ts = self.motion_push(MachineState.ON)
        print("Machine #",self.args.machname," ON",ts)

    #Interrupt handler when machine changes state to `OFF`
    def motion_end(self):
        ts = self.motion_push(MachineState.OFF)
        print("Machine #",self.args.machname," OFF",ts)
    
    """
    Main program functions
    """
    def setup(self):
        print("Initializing sensor...")
        self.sensor.wait_for_no_motion()
        #we have been patiently waiting until machine state is OFF
        #record that state and timestamp
        self.motion_push(MachineState.OFF)
        print("Sensor initialized successfully")
        self.sensor.when_motion = self.motion_start
        self.sensor.when_no_motion = self.motion_end
        print("Finished setup")
    
######################## MAIN ####################################

Application().run()
