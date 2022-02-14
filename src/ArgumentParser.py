#!/usr/bin/env python3

"""@package docstring
Documentation for this module.
 
More details.
"""

import argparse
import configparser
import os.path
    
def parse_arguments():
    """Documentation for a function.
    
    More details.
    """
	print("Parsing command line arguments")
	parser = argparse.ArgumentParser(description='Program that watches changes on Motion Sensor on a given RBPI PIN')
	parser.add_argument('--pin', default = 18, help = "number of PIN to which sensor is connected")
	parser.add_argument('--name', default = 'sensor_1', help = "identifier of sensor used in csv file title")
	parser.add_argument('--test', action = 'store_true', help = "run the program in test mode")
	parser.add_argument('-f', help = "bulk option for jupyter")
	parser.add_argument('--save', help = 'choose a save handler [console|file]')
	parser.add_argument('--output', default = '/var/log/SensorWatch', help = "program storage url")
	parser.add_argument('--resolution', default = 0.25, help = "consumer thread timer resolution")
	parser.add_argument('--sensor', default = 'MotionSensor|RPMSensor', help = "")
	parser.add_argument('--config', default = '/etc/sensorwatch/default.ini')
	
	return parser.parse_args()

def check_environment(args):
    if args.test:
        print("Checking environment")
    
    #check and create if necessary instance directory
    if not os.path.isdir(args.output):
        print("CSV storage path:",args.output,"does not exists or is not a directory")
        print("Please create it using `sudo mkdir",args.output,"`")
        return False

    if not os.access(args.output, os.W_OK):
        print("CSV storage directory:",args.output,"is not writeable")
        print("Please change ownership of this directory using: `sudo chown {}:{} {}`".format(getpass.getuser(),getpass.getuser(),args.output))
        print("also change permission of this directory using: `sudo chmod 750 {}`".format(args.output))
        return False
        
    if not os.path.isdir(os.path.join(args.output, args.name)):
        os.mkdir(os.path.join(args.output, args.name))
            
    return True
