# log4python

SensorWatch.py [-h] [--pin PIN] [--name NAME] [--test] [-f F] [--save SAVE] [--output OUTPUT] [--resolution RESOLUTION] [--sensor SENSOR]
                      [--config CONFIG]

Program that watches changes on choosen sensor type on a given RBPI PIN

```
Arguments:
-h, --help                show this help message and exit
--pin PIN                 number of PIN to which sensor is connected
--name NAME               identifier of sensor used in csv file title
--test                    run the program in test mode
-f F                      bulk option for jupyter
--save SAVE               choose a save handler [console|file]
--output OUTPUT           program storage url
--resolution RESOLUTION   consumer and producer thread timer resolution
--sensor SENSOR           sensor type (TODO)
--config CONFIG           configuration file location (TODO)
```

```
Example:
./src/SensorWatch.py --pin 18 --name machine_1 --save file --resolution 0.25

./src/SensorWatch.py --pin 14 --name machine_2 --save file --resolution 0.25

```
