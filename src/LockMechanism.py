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

if __name__ == "__main__":
    print("Basic class test")
    from ArgumentParser import parse_arguments
    from ArgumentParser import check_environment
    import sys
    from time import sleep
    
    args = parse_arguments()
    if not check_environment(args):
        print("Failed to prepare running environment")
        sys.exit(-1)
    try:
        print("TODO: test")
    except:
        print("print exception caught not good")
        raise
