SUBDIRS := doc src

all: 
	$(MAKE) -C src/
docs:
	@[ -d ./doc ] || mkdir ./doc
	doxygen

install:
	cp contrib/SensorWatch.service /etc/systemd/system 
	@[ -d /var/log/SensorWatch ] || mkdir /var/log/SensorWatch
	@[ -d /etc/SensorWatch ] || mkdir /etc/SensorWatch
	$(MAKE) -C src/
	#$(MAKE) -C doc/

clean:
	$(MAKE) -C src/ clean
	$(MAKE) -C doc/ clean

dist-clean: clean
	rm -rf ./__pycache__/*
	

test:
	$(MAKE) -C src/ test
