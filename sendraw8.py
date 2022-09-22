import time
import sys

import tkinter as tk
from tkinter import filedialog as fd
import ctypes,os

import serial.tools.list_ports


if (os.name=='nt'): #for Windows:
    def micros():
        "return a timestamp in microseconds (us)"
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()

        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics)) 
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq))  
        
        t_us = tics.value*1e6/freq.value
        return t_us
        
    def millis():
        "return a timestamp in milliseconds (ms)"
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()

        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics)) 
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq)) 
        
        t_ms = tics.value*1e3/freq.value
        return t_ms

def delayMicroseconds(delay_us):
    "delay for delay_us microseconds (us)"
    t_start = micros()
    while (micros() - t_start < delay_us):
      pass #do nothing 
    return 

    
 

class Timer:
    def __init__(self, parent):

        self.root = parent
        self.root.title("fastloader")

        self.label = tk.Label(parent, text = "hello", width=100)
        self.label.pack()
        
        self.button2 = tk.Button(parent,text = "load tzx file",command = self.load_data)
        self.button2.pack()

        self.button = tk.Button(parent,text = "send",command = self.send_data)
        self.button.pack()

        self.button3 = tk.Button(parent,text = "exit",command = self.exit)
        self.button3.pack()

        ports = list(serial.tools.list_ports.comports())
        coms_available = []
        for p in ports:
            print(p,type(p),p.device)
            if p.device[0:3] =="COM":
                coms_available.append(p)
        if len(coms_available)==0:
            print("no COM port available - is the device plugged in?")
            self.label.config(text="no COM port available - is the device plugged in?", width=100)
            #sys.exit()
        elif len(coms_available)!=1:
            print("too many COMs available - can only cope with one!")
            #sys.exit()
                
        else:
            if (ports[0].device[0:3] == "COM"):
                self.ser = serial.Serial(port=ports[0].device)
                print("connecting...")
                self.label.config(text="Connecting to "+ports[0].device, width=100)

    def exit(self):
        self.root.destroy()
        
        # show the open file dialog
    def load_data(self):
        filename = fd.askopenfile().name
        print(filename)
        
        f = open(filename,"rb")

        self.data = f.read()
        f.close()
        self.data2 = []


        print(len(self.data))
        for i in range(len(self.data)):
            if self.data[i] == 60:  # stream start char
                self.data2+=[61,0]
            elif self.data[i] == 62: # stream end char
                self.data2+=[61,2]
            elif self.data[i] == 61: # escape char char
                self.data2+=[61,1]
            else:
                self.data2+=[self.data[i]]

        print(len(self.data2))

        

    def send_data(self):
        self.ser.write(bytearray([60]))
        i=0
        while True:
           if (i+1)*100 < len(self.data2):
              self.ser.write(bytearray(self.data2[i*100:(i+1)*100]))

              delayMicroseconds(100)

           else:
              self.ser.write(bytearray(self.data2[i*100:]))
              break
           i+=1

        
        time.sleep(0.01)
        self.ser.write(bytearray([62]))

        

if __name__ == "__main__":
    root = tk.Tk()
    timer = Timer(root)
    root.mainloop()
