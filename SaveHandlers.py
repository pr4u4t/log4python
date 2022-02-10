#!/usr/bin/env python3

class SaveHandler:
    def save(self,args):
        pass

class FileSaveHandler(SaveHandler):
    def __init__(self,args):
        self.args = args
    
    def save(self,data):
        print("Writing uptime statistics to file {}/{}/data.csv".format(self.args.output,self.args.name))
        total = 0
        with open("{}/{}/data.csv".format(self.args.output,self.args.name),mode="w",encoding="utf-8") as fd:
            fd.write("Machine name, {}\r\n".format(self.args.name))
            fd.write("Hour, Uptime\r\n")
            for index in range(len(data)):
                total += data[index]
                fd.write("{}, {:.2f}\r\n".format(index,data[index]))
            fd.write("Total, {:.2f}\r\n".format(total))
        fd.close()
        print("Finished statistics write to file")

class ConsoleHandler(SaveHandler):
    def __init__(self,args):
            self.args = args
    
    def save(self,data):
        print("Writing uptime statistics to stdout")
        total = 0
        print("Machine name, {}".format(self.args.name))
        print("Hour, Uptime")
        for index in range(len(data)):
            total += data[index]
            print("{}, {:.2f}".format(index,data[index]))
        print("Total, {:.2f}".format(total))

SaveHandlers = {
    "file"      :  lambda args : FileSaveHandler(args),   
    "console"   :  lambda args : ConsoleHandler(args)
}
