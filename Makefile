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
	$(MAKE) -C src/ install
	$(MAKE) -C doc/ install

clean:
	$(MAKE) -C src/ clean
	$(MAKE) -C doc/ clean

uninstall:
	rm /etc/systemd/system/SensorWatch.service
	rm -r /var/log/SensorWatch
	rm -r /etc/SensorWatch
	$(MAKE) -C src/ uninstall
	$(MAKE) -C soc/ uninstall

dist-clean: clean
	rm -rf ./__pycache__/*
	

test:
	$(MAKE) -C src/ test
