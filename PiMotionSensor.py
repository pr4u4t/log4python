#!/usr/bin/env python3

import PiSensor
from enum import Enum
import numpy
from numpy import array
from signal import pause

#Enumeration definition
class MachineState(Enum):
    OFF     = 0
    ON      = 1

class PiMotionSensor(PiSensor.PiSensor):
    def __init__(self,args):
        super().__init__(args)
        self.data = numpy.zeros(24)
        
        if not args.test:
            #RBPI dev related imports only if not in test mode
            from gpiozero import MotionSensor
            self.sensor = MotionSensor(args.pin)
       
       
    def setup_changed(self,now):
        self.priv['laston'] = 0
    
    def minute_changed(self,now):
        self.priv['midx'] = now.minute
    
    def hour_changed(self,now):
        if laston != 0:
            self.data[hidx] += ((now.timestamp() - laston)/60)
            self.priv['laston'] = now.timestamp()
        #switch index to next hour
        self.priv['hidx'] = now.hour
        
    
    def day_changed(self,now):
        self.to_file(self.data)
        #reset data and start all over again
        self.data = numpy.zeros(24,dtype = int)
        #switch index to next day and 0 hour
        self.priv['didx'] = now.day
        self.priv['hidx'] = now.hour #this probably be 0  
        
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
        if not self.args.test:
            self.sensor.wait_for_no_motion()
            #we have been patiently waiting until machine state is OFF
            #record that state and timestamp
            self.motion_push(MachineState.OFF)
            print("Sensor initialized successfully")
            self.sensor.when_motion = self.motion_start
            self.sensor.when_no_motion = self.motion_end
        else:
            print("Running in test mode")
            
        print("Finished setup")
        #pause()
    
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

