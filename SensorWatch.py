#!/usr/bin/env python3

import time
import signal
from signal import SIGHUP, SIGINT, SIGTERM
import os
from signal import pause
import sys
import os.path
import getpass
from ArgumentParser import parse_arguments
from ArgumentParser import check_environment
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
        return parse_arguments()

    def check_env(self):
        return check_environment(self.args)
    
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
