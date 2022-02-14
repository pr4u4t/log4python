OBJ := src/LockMechanism.py src/PiMotionSensor.py src/PiSensor.py src/SaveHandlers.py

test:
	@for source in $(OBJ) ; do \
		echo "Executing test for: $$source"; \
		./$$source --test ; \
		if [ $$? -ne 0 ]; then \
			echo "TEST: failed!!" ; \
			false ; \
		else \
			echo "TEST: passed!!" ; \
		fi ; \
	done
