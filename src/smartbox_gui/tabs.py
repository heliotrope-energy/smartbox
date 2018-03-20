#!/usr/bin/python

from smartbox.sb_resource_controller_client import SmartBoxResourceControllerClient
import smartbox.smartbox_resource_controller_pb2 as sb_pb2

from tkinter import *
from tkinter import ttk
#from gpiozero import Motor, CPUTemperature
import time
#import cv2
from PIL import Image, ImageTk
import numpy as np
#import Adafruit_ADS1x15


class App:
    def __init__(self, root):
        self.client = SmartBoxResourceControllerClient(1)
        
        self.setup_grid(root)

        # creating Notebook that holds tabs   
        nb = ttk.Notebook(root)
        nb.grid(row =0, column = 0, columnspan=50, rowspan=50, sticky="NESW")

        # The first tab 
        control_tab = ttk.Frame(nb) 
        nb.add(control_tab, text = 'Control')
        # self.createButtons(control_tab)

        # Label for updating the angle 
        self.angle = Label(control_tab)
        self.angle.grid(row = 39, column = 40)
        self.update_angle()

        # The secons tab
        percepts_tab = ttk.Frame(nb)
        nb.add(percepts_tab, text = 'Percepts')
        self.setup_grid(percepts_tab)
        #     self.set_camera_image(percepts_tab)

        # Label for updating the temperature 
        # what I trying to sat is the 52 row of the percepts tab. I do not get my mssage across.
        self.temp = Label(percepts_tab, width = 50, height = 5)
        self.temp.grid(row = 52, column = 0)
      #  self.temp.grid_propagate(0)
      #   self.cpu = CPUTemperature()
      #    self.update_temp()

        info_tab = ttk.Frame(nb)
        nb.add(info_tab, text = 'Info')
        
        self.tree = ttk.Treeview(info_tab)
        self.tree["columns"] = ("one")
        self.tree.column("one", width = 100)
        self.tree.heading("one", text = "Value")
        
        self.id =  self.tree.insert('', 0, text = "Voltage")
      
        self.update_voltage()
        self.tree.pack()

            # wind_stow code 
        self.TOLERANCE = 0.1
        #self.adc = Adafruit_ADS1x15.ADS1115()
        self.GAIN  = 2/3
        self.EW_PIN = 1
        self.NS_PIN = 0
        self.scale = 6.144/32767

        goto_tab = ttk.Frame(nb)
        nb.add(goto_tab, text = 'Position')
        self.setup_grid(goto_tab)
        self.change_position(goto_tab)

        self.limits = {self.NS_PIN:[0,6.0], self.EW_PIN:[0,12.0]}
    # self.motors = {self.NS_PIN:motor_ns, self.EW_PIN:motor_ew}
        
    def calculate_inches(self, pin_num, voltage): 
        if (pin_num == self.NS_PIN):
            v_per_in = -1.335*voltage + 6.917
        if (pin_num == self.EW_PIN):
            v_per_in = -2.67*voltage + 13.83
        return v_per_in

    def get_position(self, direction):
        value = self.client(direction, gain=self.GAIN)
        voltage = value * self.scale
        inches =  self.calculate_inches(direction, voltage); 
        return inches

    def move_axis_to_position(self, direction, pos):
        min_limit, max_limit = self.limits[direction]
        current_position = self.get_position(direction)
        motor = self.motors[direction]

        if pos < min_limit:
            pos = min_limit
        if pos > max_limit:
            pos = max_limit
        while abs(current_position - pos) > self.TOLERANCE: 
            current_position = self.get_position(direction)
            print("Current Pos {}\nDesired pos {}".format(current_position, pos))
            if current_position > pos:
                motor.forward(speed = 1)
            else:
                motor.backward(speed = 1)
        motor.stop()

    def change_position(self, tab):
        
        label1 = Label(tab, text="North-South position").grid(row =10, column = 0)
        self.ns_position = Entry (tab,  width = 20);
        self.ns_position.grid(row =10, column = 10)

        label2 = Label(tab, text="East-West position").grid(row = 20, column = 0)
        self.ew_position = Entry (tab,  width = 20);
        self.ew_position.grid(row = 20, column = 10)
        
        b = Button(tab, text="Go to", width=10,\
                   command = self.on_press)
        b.grid(row = 20, column = 30)

    def on_press(self):
        ew_str = self.ew_position.get()
        ns_str = self.ns_position.get()
        
        print ("East-west {}".format(ew_str))
        print ("North-south {}".format(ns_str))
        is_error = False
        current_pos_ew = self.client.get_ew_position()
        try:
            ew_pos = float(ew_str)
        except ValueError:
            ew_pos = current_pos_ew
            self.ew_position.delete(0, END)
            self.ew_position.insert(0, ew_pos)
            is_error= True

        ew_min,ew_max = self.limits[self.EW_PIN]
        if ew_pos < ew_min:
            self.ew_position.delete(0, END)
            self.ew_position.insert(0, ew_min)
        if ew_pos > ew_max:
            self.ew_position.delete(0, END)
            self.ew_position.insert(0, ew_max)
        

        current_pos_ns = self.client.get_ns_position()
        try:
            ns_pos = float(ns_str)
        except ValueError:
            ns_pos = current_pos_ns
            self.ns_position.delete(0, END)
            self.ns_position.insert(0, ns_pos)
            is_error = True

        ns_min,ns_max = self.limits[self.NS_PIN]
        if ns_pos < ns_min:
            self.ns_position.delete(0, END)
            self.ns_position.insert(0, ns_min)
        if ns_pos > ns_max:
            self.ns_position.delete(0, END)
            self.ns_position.insert(0, ns_max)
            
        if not is_error:
            print ("Positions: {} {}".format(ns_pos, ew_pos))
            self.client.move_panel_to_linear_position(ns_pos, ew_pos)
            
        
    def move_panel_to_position(self, ns_pos, ew_pos):
        self.move_axis_to_position(self.EW_PIN, ew_pos)
        self.move_axis_to_position(self.NS_PIN, ns_pos)

    def update_voltage(self):
        self.tree.set(self.id, column = "one", value=self.client.get_battery_voltage())
        self.tree.after(100, self.update_voltage)
        
    # Replace this method by the formula of angle calculation 
    def update_angle(self):
        ns = self.client.get_ns_position()
        ew = self.client.get_ew_position()
        
        self.angle.configure(text = "Position: {:.3f} {:.3f}".format(ns, ew))
        self.angle.after(100, self.update_angle)

    def update_temp(self):
        self.temp.configure(text = "Temperature: "+ str(self.cpu.temperature))
        self.temp.after(100, self.update_temp)

    def set_camera_image(self, tab):
        
        imageFrame = ttk.Frame(tab, width = 350, height = 350)
        imageFrame.grid(rowspan = 50)
        # making sure that my settings hold
        imageFrame.grid_propagate(0)

        

        self.lmain = Label(imageFrame)
        self.lmain.grid(row = 0, column = 1, rowspan = 10)
        self.cap = cv2.VideoCapture(0)
        self.video_loop()

    def video_loop(self):
        
        ok, fr = self.cap.read()
        fr  = cv2.flip(fr, 1) 
        cv2image = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
        # cv2.PutText(currentframe, datetime.now().strftime("%Y.%m.%d %H:%M:%S"), (10, 30), self.timeFont, 0)
        # making a timestamp 
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image = img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image = imgtk)
        self.lmain.after(10, self.video_loop)     
        
    def move_forward(self, event, motor_name):
        print("Moving forward")
        motor_name.forward(speed=1)

    def move_backward(self, event, motor_name):
        print("Moving backward")
        motor_name.backward(speed=1)

    def release(self, event, motor_name):
        print("Stopped")
        motor_name.stop()

    def createButtons(self, tab):
       
        self.setup_grid(tab); 
        
        self.button1 = Button(tab, text = "North")
        self.button2 = Button(tab, text = "South")
        self.button3 = Button(tab, text = "West")
        self.button4 = Button(tab, text = "East")

        self.button1.grid(row = 10, column = 25)
        self.button2.grid(row = 30, column = 25)
        self.button3.grid(row = 20, column = 15)
        self.button4.grid(row = 20, column = 35)

        # Motor 1
        self.button1.bind("<ButtonPress>", lambda event, arg = motor_ns: self.move_forward(event, arg))
        self.button2.bind("<ButtonPress>", lambda event, arg = motor_ns: self.move_backward(event, arg))

        self.button1.bind("<ButtonRelease>", lambda event, arg = motor_ns: self.release(event, arg))
        self.button2.bind("<ButtonRelease>", lambda event, arg = motor_ns: self.release(event, arg))
      
        # Motor 2
        self.button3.bind("<ButtonPress>", lambda event, arg = motor_ew: self.move_forward(event, arg))
        self.button4.bind("<ButtonPress>", lambda event, arg = motor_ew: self.move_backward(event, arg))

        self.button3.bind("<ButtonRelease>", lambda event, arg = motor_ew: self.release(event, arg))
        self.button4.bind("<ButtonRelease>", lambda event, arg = motor_ew: self.release(event, arg))


    #assigning weight to the cells in a grid => make sure that the positioning is as expected 
    def setup_grid(self, grid_name):
        row=0
        while row<50:
            grid_name.rowconfigure(row, weight=1)
            grid_name.columnconfigure(row, weight=1)
            row +=1
            
        
main = Tk()
main.title("Python GUI")
main.geometry('500x500')

#motor_ns = Motor(26,20)
#motor_ew= Motor(21,16)

app = App (main)
main.bind()
main.mainloop()



    

