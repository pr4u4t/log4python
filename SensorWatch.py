#!/usr/bin/env python3

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import argparse
import sys
import os.path
import getpass
import configparser
import LockMechanism
import PiSensor
import PiMotionSensor


class Application:
    def __init__(self):
        print("New Application instance")
        self.args = self.parse_arguments()
        self.check_env()
        self.signal_setup()
        self.sensor = PiMotionSensor.PiMotionSensor(self.args)
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

######################## MAIN ####################################

Application().run()
