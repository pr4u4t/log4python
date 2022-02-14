PSOURCES := LockMechanism.py PiMotionSensor.py PiSensor.py SaveHandlers.py
CSOURCES := LockMechanism.c PiMotionSensor.c PiSensor.c SaveHandlers.c
OBJECTS  := LockMechanism.o PiMotionSensor.o PiSensor.o SaveHandlers.o
CFLAGS	 := $(shell python3.10-config --includes)
LIBS	 := $(shell python3.10-config --ldflags)

all: $(CSOURCES) SensorWatch.c $(OBJECTS) SensorWatch.o
	gcc $(LIBS) -o SensorWatch $(OBJECTS) SensorWatch.o -lpython3.10

SensorWatch.c: SensorWatch.py
	cython -3 --embed -o $@ $<

%.c: %.py
	cython -3 -o $@ $<

%.o: %.c
	gcc $(CFLAGS) -c $< -o $@ 

install:
	cp -f SensorWatch /usr/bin/

test:
	@for source in $(PSOURCES) ; do \
		echo "Executing test for: $$source"; \
		./$$source --test &> /dev/null ; \
		if [ $$? -ne 0 ]; then \
			echo "TEST: failed!!" ; \
			false ; \
		else \
			echo "TEST: passed!!" ; \
            	fi ; \
	done

dist-clean: clean 
	rm -rf __pycache__

clean:
	rm -rf $(OBJECTS) SensorWatch.o
	rm -rf $(CSOURCES) SensorWatch.c
	rm -f SensorWatch
