#!/usr/bin/env python3

import socket
import threading
import socketserver

"""
Lock and inter process communication 
"""
class ThreadedStreamRequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        pass
    
    def handle(self):
        print("Handling connection")
        data = str(self.request.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.request.sendall(response)
        
    def finish():
        pass

class ThreadedStreamServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    pass
