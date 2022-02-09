#!/usr/bin/env python3

from queue import Queue
import queue
from threading import Thread
from threading import Lock
import datetime

class PiSensor:
    def __init__(self,args):
        self.time_queue = Queue()
        self.consumer_lock = Lock()
        self.consumer_lock.acquire()
        self.args = args
        self.th = Thread(target = self.consumer, args = ( os.path.join(self.args.output, "machine_{}/data.csv".format(self.args.name)), args.resolution, args.name))

    def stop(self):
        self.consumer_lock.release()
        if not self.args.test:
            self.th.join()

    def start(self):
        self.th.start()
        
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
        pass
    
    def minute_changed(self,now):
        pass
    
    def hour_changed(self,now):
        pass
    
    def day_changed(self,now):
        pass
    
    def to_stdout(self,data):
        SaveHandlers.ConsoleHandler(self.args).save(data)
    
    def to_file(self,data):
        SaveHandlers.FileSaveHandler(self.args).save(data)
    
    """
    Consumer thread function
    """
    def consumer(self,output, resolution, machname):
        print("consumer thread started")
        
        self.setup_changed(datetime.datetime.now())
        
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
