#!/usr/bin/env python3

import argparse
import configparser

def parse_arguments():
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
