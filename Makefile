OBJ := src/LockMechanism.py src/PiMotionSensor.py src/PiSensor.py src/SaveHandlers.py

docs:
	@[ -d ./doc ] || mkdir ./doc
	doxygen

install:
	cp contrib/SensorWatch.service /etc/systemd/system 
	@[ -d /var/log/SensorWatch ] || mkdir /var/log/SensorWatch
	@[ -d /etc/SensorWatch ] || mkdir /etc/SensorWatch

clean:
	rm -rf ./__pycache__/*

test:
	@for source in $(OBJ) ; do \
		echo "Executing test for: $$source"; \
		./$$source --test &> /dev/null ; \
		if [ $$? -ne 0 ]; then \
			echo "TEST: failed!!" ; \
			false ; \
		else \
			echo "TEST: passed!!" ; \
		fi ; \
	done
