# log4python

SensorWatch.py [-h] [--pin PIN] [--name NAME] [--test] [-f F] [--save SAVE] [--output OUTPUT] [--resolution RESOLUTION] [--sensor SENSOR]
                      [--config CONFIG]

Program that watches changes on choosen sensor type on a given RBPI PIN

options:
  -h, --help            show this help message and exit
  --pin PIN             number of PIN to which sensor is connected
  --name NAME           identifier of sensor used in csv file title
  --test                run the program in test mode
  -f F                  bulk option for jupyter
  --save SAVE           choose a save handler [console|file]
  --output OUTPUT       program storage url
  --resolution RESOLUTION
                        consumer thread timer resolution
  --sensor SENSOR
  --config CONFIG
