OBJ := LockMechanism.py PiMotionSensor.py PiSensor.py SaveHandlers.py

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
