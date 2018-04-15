#!/usr/bin/python

from smartbox.client.resource_controller_client import SmartBoxResourceControllerClient


from tkinter import *
from tkinter import ttk
import time
from PIL import Image, ImageTk
import numpy as np
import datetime, os, math, pvlib
import os
import pandas as pd



class App:
    def __init__(self, root):
        self.root  = root

        # client is initialised once "Connect" button is pressed
        self.client = None
        self.setup_grid(root)
        
        # creating Notebook that holds tabs   
        self.nb = ttk.Notebook(root)
        self.nb.grid(row =0, column = 0, columnspan=50, rowspan=50, sticky="NESW")

        self.create_control_tab()
        self.create_percepts_tab()
        self.create_info_tab()
        self.create_goto_position_tab()
        self.create_goto_angle_tab()
        
        self.update_all_functions()


    def create_control_tab(self):
        """
            Manages the first, control, tab. 
            Creates the direction and "connect" buttons. Is responsible for the angle labels. 
        """
        self.control_tab = ttk.Frame(self.nb) 
        self.setup_grid(self.control_tab)
        self.nb.add(self.control_tab, text = 'Control')
        
        self.createButtons(self.control_tab)
        self.create_angle_labels(self.control_tab);

    def create_percepts_tab(self): 
        """
            Manages the second, percepts, tab. 
            Administers the video loop and creates labels for the azimuth/elevation and temperature values. 
        """

        percepts_tab = ttk.Frame(self.nb)
        self.setup_grid(percepts_tab)
        self.nb.add(percepts_tab, text = 'Percepts')

        self.set_camera_image(percepts_tab)

        self.temp = ttk.Label(percepts_tab, width = 20, text = "Temperature: ")
        self.temp.grid(row = 60, column = 15)

        self.azimuth = ttk.Label(percepts_tab, width = 20, text = "Azimuth: ")
        self.azimuth.grid(row = 62, column = 14)

        self.elevation = ttk.Label (percepts_tab, width = 20, text = "Elevation: ")
        self.elevation.grid(row = 62, column = 20)

    def create_info_tab(self):
        """
            Is responsible for displaying important information about the charge controller. 
            Using python's ttk.Treeview to do. 
        """
        info_tab = ttk.Frame(self.nb)
        self.nb.add(info_tab, text = 'Info')
        
        self.tree = ttk.Treeview(info_tab, height = 300)
        self.tree["columns"] = ("one")
        self.tree.column("one", width = 300)
        self.tree.heading("one", text = "Value")
        
        # A dictionary associating the names with their unique IDs in the Tree. 
        self.tree_ids = {"Battery Voltage": self.tree.insert('', 0, text = "Battery Voltage"), 
                         "Solar Panel Voltage": self.tree.insert('', 1, text = "Solar Panel Voltage"),
                         "Load Voltage": self.tree.insert('', 2, text = "Load Voltage"), 
                         "Charging Current": self.tree.insert('', 3, text = "Charging Current"), 
                         "Load Current": self.tree.insert('', 4, text = "Load Current"), 
                         "Charge Status": self.tree.insert('', 5, text = "Charge Status")
                         }

        self.tree.pack()

    def create_goto_position_tab(self):
        """
            Creates a tab, where you could input the values of the desired position of the panel.  
            As goto_angle_tab is very similar to goto_position_tab, I am going to be using 
            a generic move_setip() method to set them up. 
        """
        goto_position_tab = ttk.Frame(self.nb)
        self.nb.add(goto_position_tab, text = 'Position')
        self.setup_grid(goto_position_tab)

        # As I am using generic move_setup, I need to differentiate the entries. 
        self.ns_pos = Entry (goto_position_tab,  width = 20);
        self.ew_pos = Entry (goto_position_tab, width = 20 )
        
        self.move_setup(goto_position_tab, "position", self.ns_pos, self.ew_pos); 
    
    def create_goto_angle_tab(self):
        """
            Creates a tab, where you could input the values of the desired angle of the panel. 
        """
        goto_angle_tab = ttk.Frame(self.nb)
        self.nb.add(goto_angle_tab, text = 'Angle')
        self.setup_grid(goto_angle_tab)

        self.ns_ang = Entry (goto_angle_tab,  width = 20)
        self.ew_ang = Entry (goto_angle_tab, width = 20 )

        self.move_setup(goto_angle_tab, "angle", self.ns_ang, self.ew_ang)
    
    def createButtons(self, tab):  
        """
            Created Buttons using https://dabuttonfactory.com/, which administer the motors.
        """

        # creating absolute paths for the images. Hopefully, you will be able to see them. 
        north_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'button_north.gif'))
        south_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'button_south.gif'))
        east_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'button_east.gif'))
        west_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'button_west.gif'))
        connect_img = os.path.abspath(os.path.join(os.path.dirname(__file__), 'button_connect.gif'))

        # Program must keep an extra reference to the image object, so that the image is not garbage-collected 
        # when function returns, hence local variables store them. 
        
        north = PhotoImage(file = north_img)
        south = PhotoImage(file = south_img)
        east = PhotoImage(file = east_img)
        west = PhotoImage(file = west_img)
        connect = PhotoImage(file = connect_img)

        self.north_btn = Button (tab, image =  north)
        self.south_btn = Button (tab, image = south)
        self.east_btn  = Button (tab, image = east)
        self.west_btn = Button (tab, image = west)

        self.connect_btn = Button(tab, image = connect, command = self.initialise_client)

        self.connect_btn.grid(row = 40, column = 10)
        self.north_btn.grid(row = 10, column = 30)
        self.south_btn.grid(row = 30, column = 30)
        self.east_btn.grid(row = 20, column = 10)
        self.west_btn.grid(row = 20, column = 35)



        images = {self.north_btn: north, 
                  self.south_btn: south, 
                  self.east_btn: east, 
                  self.west_btn: west}
        self.connect_btn  = connect

        # The main role of the function is to assign the previously created local variables to the button's "image" field. 
        # Since 4 of the buttons have a Release event in common, I am also going to include the bind functio here. 
        for key, value in images.items():
            key.image = value
            key.bind("<ButtonRelease>", lambda event: self.release(event))


        self.north_btn.bind("<ButtonPress>", lambda event: self.move_north(event))
        self.south_btn.bind("<ButtonPress>", lambda event: self.move_south(event))
        self.east_btn.bind("<ButtonPress>", lambda event: self.move_west(event))
        self.west_btn.bind("<ButtonPress>", lambda event: self.move_east(event))

    def move_east(self, event):
        """
           Moves the panel in the east direction
        """
        if self.client is not None: 
            self.client.tracker.move_east()

    def move_west(self, event):
        """
           Moves the panel in the west direction
        """
        if self.client is not None:
            self.client.tracker.move_west()
            

    def move_south(self, event):
        """
           Moves the panel in the south direction
        """
        if self.client is not None: 
            self.client.tracker.move_south()

    def move_north(self, event):
        """
           Moves the panel in the north direction
        """
        if self.client is not None: 
            self.client.tracker.move_north()

    def release(self, event):
        """
           Stops the motors when a direction button is released 
        """
        if self.client is not None: 
            self.client.tracker.stop()

    def initialise_client(self):
        """
            When the connect button is pressed, the client gets initialised. 
            This function is created to make sure that GUI is still displayable when the client is not connected. 
        """
        if self.client is None: 
            self.client = SmartBoxResourceControllerClient(10)
            
            # These are the limits of movement in terms of position and angles. For example, you can't move north by 
            # less than -2 degrees and more than 38
            self.pos_limits = {"ns": [0,6.0], "ew": [0,12.0]}
            self.ang_limits = {"ns":[-2, 38], "ew": [-40, 40]}

            # These tuples contain the information associated with angles and positions respectively. They are used to make
            # move_general() more generic :) 
            self.ang_tuple = self.client.tracker.get_ns_angle, self.client.tracker.get_ew_angle, self.ang_limits, \
                             self.client.tracker.move_panel_to_angular_position
            self.pos_tuple = self.client.tracker.get_ns_position, self.client.tracker.get_ew_position, self.pos_limits, \
                             self.client.tracker.move_panel_to_linear_position

            self.option = {"position": self.pos_tuple, \
                           "angle": self.ang_tuple}
        
        
    def create_angle_labels(self, tab):
        """
            Create labels for the angles on the Control tab. 
        """

        s = ttk.Style()
        s.configure('TLabel', foreground = 'blue', font = ('Caviar','14')) 

        self.ns_angle_label = ttk.Label(tab, text = "  North-South Angle: ")
        self.ns_angle_label.grid(row = 39, column = 35)

        self.ew_angle_label = ttk.Label(tab, text = "East-West Angle:")
        self.ew_angle_label.grid(row = 41, column = 35)


    def update_angle(self):
        """
            Is called by update_all_functions() and updates the angles of the panel displayed on the Control tab. 
        """

        if self.client is not None:
            ns = self.client.tracker.get_ns_angle()
            ew = self.client.tracker.get_ew_angle()

            self.ns_angle_label.configure(text = "North-South Angle:  {:.3f}".format(ns))
            self.ew_angle_label.configure(text = "East-West Angle:    {:.3f}".format(ew))
            
            
    
    def set_camera_image(self, tab):
        """
            Creates a frame and a label that will contain a camera image. 
        """
        imageFrame = ttk.Frame(tab, width = 750, height = 380)
        imageFrame.grid(rowspan = 50, columnspan= 30)
        
        # This function makes sure that the Frame does not shrink
        imageFrame.grid_propagate(0)
        
        self.image_label = Label(imageFrame, width = 700, height = 380, bg  = 'black')
        self.image_label.grid(row = 0, column = 0)
        self.image_label.grid_propagate(0)

    def video_loop(self):
        """
            Is called by update_all_functions(). Grabs the image and displays it. 
        """
        if self.client is not None:
            self.cv2image  = self.client.camera.get_image()

            if self.cv2image is not None: 
                img = Image.fromarray(self.cv2image)
                imgtk = ImageTk.PhotoImage(image = img)
                self.image_label.imgtk = imgtk
                self.image_label.configure(image = imgtk)

    def update_temp(self):
        """
            Is called by update_all_functions(). Displays the temperature.   
            Please, uncomment the line when self.client.weather.get_weather() is fixed. 
        """
        if self.client is not None:
            self.temp.configure(text = "Temperature: ")
            #self.temp.configure(text = "Temperature: {:.3f}".format(self.client.weather.get_weather()))

    def update_azimuth_and_elevation(self):
        """
            Is called by update_all_functions(). Updates the values of azimuth and elevation by    
            calling a function calculate_azimuth()
        """
        if self.client is not None: 
            azimuth, elevation = self.calculate_azimuth()
            self.azimuth.configure(text = "Azimuth: {:.3f}".format(azimuth))
            self.elevation.configure(text = "Elevation: {:.3f}".format(elevation))

    def calculate_azimuth(self):
        """
            This is the method that Stephen developed for calculating the azimuth. The next 
            method is what Eddie developed using the pvlib library. Unfortunately, I did 
            not manage to make the outputs match however hard I tried. The major challenge is 
            that there are a lot of ways to interpret the components of the normal. I have consulted 
            a lot of sources in the Internet, trying to figure out, but in vain. However, here are the 
            websites, that prove that the logic behind my calculations make sense. 

            http://pydoc.net/PsychoPy/1.82.01/psychopy.tools.coordinatetools/
            http://nipy.org/dipy/theory/spherical.html
            https://github.com/numpy/numpy/issues/5228
        """

        if self.client is not None: 
            ns = self.client.tracker.get_ns_angle()
            ew = self.client.tracker.get_ew_angle()

            r_y = [ [math.cos(ns), 0, math.sin(ns)], 
                    [0, 1, 0], 
                    [-math.sin(ns), 0, math.cos(ns)]]

            r_x = [ [1, 0, 0], 
                    [0, math.cos(ew), -math.sin(ew)], 
                    [0, math.sin(ew), math.cos(ew)]]

            m = np.matmul(r_y, r_x)
            normal = np.matmul(m, [0, 0, 1])

            x = normal [0]
            y = normal [1]
            z = normal [2]

            # Here are the two analogous ways that yield the same result. 

            #First: radius = r, elevation = theta, azimuth = phi
            #polar_r = np.sqrt(x**2 + y**2 + z**2)
            #theta = math.degrees(math.acos(z/polar_r))
            #phi2 = math.degrees(math.atan2(y, x))

           # Second: I have taken it from one of the websites mentioned above, but it yields the same result
           # as the method I came up with. 
            
            radius = np.sqrt(x**2 + y**2 + z**2)
            azimuth = np.arctan2(y, x)
            elevation = np.arctan2(z, np.sqrt(x**2+y**2))

            #convert azimuth and elevation angles into degrees
            azimuth *=(180.0/np.pi)
            elevation *=(180.0/np.pi)
            
            return azimuth, elevation
    
    def calc_azimuth(self):
        """
            This is the method developed by Eddie using pvlib. 
            Once we have got angle_pos, I assume we are looking for tracker_theta? 
            From pvlib: tracker_theta is the rotation angle of the tracker. 
            Tracker_theta = 0 is horizontal, and positive rotation angles are clockwise.
        """

        now = pd.to_datetime('now').tz_localize('UTC')
        pos_data = pvlib.solarposition.get_solarposition(now, 41.8240, -71.4128)
        angle_pos = pvlib.tracking.singleaxis(pos_data['apparent_zenith'], pos_data['azimuth'], backtrack=False)
        return angle_pos['tracker_theta']

    def get_info_from_tracker_status(self, status):
        """
            Returns a dictionary, associating the values with their respective names. 
        """
        data = {"Battery Voltage": status.charge_controller.battery_voltage,
                "Solar Panel Voltage": status.charge_controller.array_voltage,
                "Load Voltage": status.charge_controller.load_voltage,
                "Charging Current": status.charge_controller.charge_current, 
                "Load Current": status.charge_controller.load_current, 
                "Charge Status": status.charge_controller.charge_state, 
                }
        return data

    def update_info(self):
        """
            Updates the "Value" column of the Treeview by getting the data from the tracker. 
        """

        if self.client is not None:
            status = self.client.tracker.get_tracker_data()
            data = self.get_info_from_tracker_status(status)
        
            for key, value in data.items():
                tree_id = self.tree_ids[key]
                self.tree.set(tree_id, column = "one", value=value)

    def move_setup(self, tab, position, ns, ew):
        """
            Sets up the goto_position_tab and goto_angle_tab. 
            The "position" parameter corresponds to either "position" or "angle". 
            Depending on that, different labels are displayed and different paramaters are passed in to 
            move_general(). 
        """

        label1 = ttk.Label(tab, text="North-South " + position).grid(row =10, column = 0)
        ns.grid(row =10, column = 10)

        label2 = ttk.Label(tab, text="East-West  " + position).grid(row = 20, column = 0)
        ew.grid(row = 20, column = 10)
        
        b = Button(tab, text="Go to " + position, width=10, command = lambda north_south = ns, east_west = ew: self.move_general(ns, ew, position))
        b.grid(row = 20, column = 30)

    def move_general(self, ns, ew, position):
        """
            This method is a result of me trying to combine two methods move_to_angular() and move_to_linear() in one. 
            It also takes "position" as a parameters, which takes two values: "angle" or "position", depending 
            on which tab we are pressing the "Go to..." button. 

            I have used the Dictionary extensively here, I am not sure whether it is the best solution. Would be happy 
            to talk about a better solution! :) 
            
            Quick reminder of what self.option corresponds to: (defined in initialise_client())

            self.option = {"position": self.pos_tuple, \
                           "angle": self.ang_tuple} 

            self.ang_tuple = self.client.tracker.get_ns_angle, self.client.tracker.get_ew_angle, self.ang_limits, \
                             self.client.tracker.move_panel_to_angular_position
            self.pos_tuple = self.client.tracker.get_ns_position, self.client.tracker.get_ew_position, self.pos_limits, \
                             self.client.tracker.move_panel_to_linear_position

            self.pos_limits = {"ns": [0,6.0], "ew": [0,12.0]}
            self.ang_limits = {"ns":[-2, 38], "ew": [-40, 40]}

        """

        if self.client is not None:
            ew_str = ew.get()
            ns_str = ns.get()
            
            current_ns = self.option[position][0]
            current_ew = self.option[position][1]

            # if input is not valid, this dummy variable will turn true. 
            is_error = False

            # Making sure that the input is valid. 
            try:
                ew_pos = float(ew_str)
            except ValueError:
                ew_pos = current_ew
                ew.delete(0, END)
                ew.insert(0, ew_pos)
                is_error= True

            try:
                ns_pos = float(ns_str)
            except ValueError:
                ns_pos = current_ns
                ns.delete(0, END)
                ns.insert(0, ns_pos)
                is_error = True

            ew_min,ew_max = self.option[position][2]["ew"]
            ns_min,ns_max = self.option[position][2]["ns"]

            # Making sure that the values are within the specified limits. 
            if ew_pos < ew_min:
                ew_pos = ew_min
                ew.delete(0, END)
                ew.insert(0, ew_min)
            if ew_pos > ew_max:
                ew_pos = ew_max
                ew.delete(0, END)
                ew.insert(0, ew_max)

            if ns_pos < ns_min:
                ns_pos = ns_min
                ns.delete(0, END)
                ns.insert(0, ns_min)
            if ns_pos > ns_max:
                ns_pos = ns_max
                ns.delete(0, END)
                ns.insert(0, ns_max)
            
            # finally, calling the respective function.  
            if not is_error:
                print (position + ": {} {}".format(ns_pos, ew_pos))
                self.option[position][3](ns_pos, ew_pos)
       
    def update_all_functions(self):
        """
            This function is going to call all the functions that have to be updated within a specific time interval, 
            using the "after" function of widgets in python. 
            Please, uncomment self.video_loop() when camera is fixed. 
        """
        # control tab
        self.update_angle()

        # percepts tab
        self.update_temp()
        self.update_azimuth_and_elevation()
        #self.video_loop()

        #info_tab
        self.update_info()

        # after takes the time interval after which the callback function should be called. 
        self.root.after(1000, self.update_all_functions)

    def setup_grid(self, grid_name):
        """
            Assigning weight to the cells in a grid to ensure exact positioning
        """
        row=0
        while row<70:
            grid_name.rowconfigure(row, weight=1)
            grid_name.columnconfigure(row, weight=1)
            row +=1
            
if __name__ == "__main__":
    main = Tk()
    main.title("Python GUI")
    main.geometry('800x420')

    app = App (main)
    main.bind()
    main.mainloop()



    

