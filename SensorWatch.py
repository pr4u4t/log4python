#!/usr/bin/env python3

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import argparse
import sys

from enum import Enum
from numpy import array
import numpy
import os.path
import getpass
import configparser
import LockMechanism
import SaveHandlers
import PiSensor

#Enumeration definition
class MachineState(Enum):
    OFF     = 0
    ON      = 1



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
        parser.add_argument('--name', default = 1, help = "identifier of sensor used in csv file title")
        parser.add_argument('--test', action = 'store_true', help = "run the program in test mode")
        parser.add_argument('-f', help = "bulk option for jupyter")
        parser.add_argument('--save', help = 'choose a save handler [console|file]')
        parser.add_argument('--output', default = '/var/log/SensorWatch', help = "program storage url")
        parser.add_argument('--resolution', default = 0.25, help = "consumer thread timer resolution")
        parser.add_argument('--sensor', default = 'MotionSensor|RPMSensor', help = "")
        parser.add_argument('--config', default = '/etc/sensorwatch/default.ini')
        
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
        
        if not os.path.isdir(os.path.join(self.args.output, "machine_{}".format(self.args.name))):
            os.mkdir(os.path.join(self.args.output, "machine_{}".format(self.args.name)))
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




        
class PiMotionSensor(PiSensor):
    def __init__(self,args):
        super().__init__(args)
        self.data = numpy.zeros(24)
        
        if not args.test:
            #RBPI dev related imports only if not in test mode
            from gpiozero import MotionSensor
            self.sensor = MotionSensor(args.pin)
            self.setup()
       
    def setup_changed(self,now):
        self.priv = { 
            'laston'  : 0,
            'midx'    : now.minute,
            'hidx'    : now.hour,
            'didx'    : now.day
        }
    
    def minute_changed(self,now):
        pass
    
    def hour_changed(self,now):
        if laston != 0:
            self.data[hidx] += ((now.timestamp() - laston)/60)
            self.priv.laston = now.timestamp()
        #switch index to next hour
        self.priv.hidx = now.hour
        
    
    def day_changed(self,now):
        self.to_file(self.data)
        #reset data and start all over again
        self.data = numpy.zeros(24,dtype = int)
        #switch index to next day and 0 hour
        self.priv.didx = now.day
        self.priv.hidx = now.hour #this probably be 0  
        
    """
    Functions that handles RBPI interrupt on PIN this functions 
    adds data to queue which is processed by another thread to not 
    waste time for processing in main program thread

    Additional function to handle interrupt from signal HUP, TERM, INT
    """
    
    #Interrupt handler when machine changes state to `ON`
    def motion_start(self):
        ts = self.event_push(MachineState.ON)
        print("Machine #",self.args.machname," ON",ts)

    #Interrupt handler when machine changes state to `OFF`
    def motion_end(self):
        ts = self.event_push(MachineState.OFF)
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
    
    def process_event(self,item,now):
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
    
######################## MAIN ####################################

Application().run()
