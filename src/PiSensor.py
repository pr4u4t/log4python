#!/usr/bin/env python3

from time import sleep
from queue import Queue
import queue
from threading import Thread
from threading import Lock
import datetime
import os.path
import SaveHandlers

class PiSensor:
    def __init__(self,args):
        self.time_queue = Queue()
        self.consumer_lock = Lock()
        self.consumer_lock.acquire()
        self.args = args
        self.data = []
        self.setup_changed(datetime.datetime.now())
        #TODO: clean
        self.consumer = Thread(target = self.consumer, args = ( os.path.join(self.args.output, "machine_{}/data.csv".format(self.args.name)), args.resolution))
        self.producer = Thread(target = self.producer, args = ( self.args.name, args.resolution))

    def stop(self):
        if self.consumer_lock.locked():
            self.consumer_lock.release()
            self.consumer.join()
            self.producer.join()

    def start(self):
        self.producer.start()
        self.consumer.start()
        
    #push current MachineState into the queue
    def event_push(self,state):
        ct = datetime.datetime.now()
        ts = ct.timestamp()
        self.time_queue.put([state,ts])
        return ts

    def event_pop(self,resolution = 0.25):
        return self.time_queue.get(True,resolution)
    
    def process_event(self,item,now):
        pass
    
    def setup_changed(self,now):
        self.priv = { 
            'midx'    : now.minute,
            'hidx'    : now.hour,
            'didx'    : now.day
        }
    
    def minute_changed(self,now):
        pass
    
    def hour_changed(self,now):
        pass
    
    def day_changed(self,now):
        self.to_file(self.data)
        self.priv['didx'] = now.day
    
    def setup(self):
        pass
    
    def to_stdout(self,data):
        SaveHandlers.ConsoleHandler(self.args).save(data)
    
    def to_file(self,data):
        SaveHandlers.FileSaveHandler(self.args).save(data)
    
    """
    Watcher thread function
    """
    def producer(self,name,resolution):
        print("producer thread started")
        self.setup()
        
        while self.consumer_lock.locked():
            sleep(resolution)
            
        print("producer thread quitting")
            
    """
    Consumer thread function
    """
    def consumer(self,output,resolution):
        print("consumer thread started")
        
        #self.setup_changed(datetime.datetime.now())
        
        while self.consumer_lock.locked():
            try:
                now = datetime.datetime.now()
                item = self.event_pop(resolution)
                self.process_event(item,now)
            except queue.Empty:
                #pretend nothing happend
                pass
            
            if now.minute != self.priv['midx']:
                print("Minute changed")
                self.minute_changed(now)
            
            if now.hour != self.priv['hidx']:
                print("Hour changed")
                self.hour_changed(now)
                
            if now.day != self.priv['didx']:
                print("Day changed")
                self.day_changed(now)
                
        print("consumer thread quitting")
        self.to_stdout(self.data)


if __name__ == "__main__":
    print("Basic class test")
    from ArgumentParser import parse_arguments
    from ArgumentParser import check_environment
    import sys
    
    args = parse_arguments()
    if not check_environment(args):
        print("Failed to prepare running environment")
        sys.exit(-1)
    try:
        sensor = PiSensor(args)
        sensor.start()
        sensor.priv['didx'] += 1
        sleep(1)
        sensor.stop()
    except:
        print("print exception caught not good")
        raise
