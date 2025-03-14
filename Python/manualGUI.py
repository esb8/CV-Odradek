# File: servo_frontend.py
# This file contains the GUI (frontend) for servo control
import tkinter as tk
from tkinter import ttk, messagebox
from backend import ServoController

class ServoControlGUI:
    def __init__(self, root, controller):
        self.root = root
        self.root.title("Servo Control Panel")
        self.root.geometry("500x400")
        self.controller = controller
        
        # Create the main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = ttk.Label(main_frame, text="Servo Control System", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # Create frame for servo controls
        self.servo_frame = ttk.LabelFrame(main_frame, text="Servo Controls")
        self.servo_frame.pack(fill=tk.BOTH, 
                              expand=True, 
                              pady=10)
        
        # Create sliders for each servo
        self.sliders = []
        for i in range(controller.num_servos):
            frame = ttk.Frame(self.servo_frame)
            frame.pack(fill=tk.X, 
                       padx=10, 
                       pady=5)
            
            # Label for the servo
            label = ttk.Label(frame, text=f"Servo {i+1}")
            label.pack(side=tk.LEFT, padx=5)
            
            # angle_string to show current position of servo
            angle_string = tk.StringVar(value="0°")  # StringVar to display the angle
            value_label = ttk.Label(frame, textvariable=angle_string, width=5)
            value_label.pack(side=tk.RIGHT, padx=5)
            
            # Create slider (ttk.Scale)
            slider = ttk.Scale(
                frame,
                from_=0,
                to=180,
                orient=tk.HORIZONTAL,
                length=300,
                command=lambda v, idx=i, var=angle_string: self.update_servo(idx, v, var)
            )
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.sliders.append((slider, angle_string))
       
    def update_servo(self, idx, floatAngle, stringAngle):
        #  Set Position
        angle = int(floatAngle)
        self.controller.set_position(idx, angle)
        # Set Labels
        stringAngle.set(f"{angle}°")
        # self.status_var.set(f"Servo {idx+1} moved to position {position}°")

'''      
    def center_all(self):
        for i, (slider, value_var) in enumerate(self.sliders):
            slider.set(90)
            self.servo_values[i] = 90
            value_var.set("90°")
        self.status_var.set("All servos centered at 90°")
        
    def reset_all(self):
        if self.controller.reset_all():
            # Update all sliders to match
            for i, (slider, value_var) in enumerate(self.sliders):
                slider.set(0)
                value_var.set("0°")
            self.status_var.set("All servos reset to 0°")
        '''  