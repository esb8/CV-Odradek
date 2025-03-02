# File: servo_frontend.py
# This file contains the GUI (frontend) for servo control

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
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
            
            # Value label to show current position
            value_var = tk.StringVar(value="0°")
            value_label = ttk.Label(frame, textvariable=value_var, width=5)
            value_label.pack(side=tk.RIGHT, padx=5)
            
            # Scale (slider) for the servo
            slider = ttk.Scale(
                frame,
                from_=0,
                to=180,
                orient=tk.HORIZONTAL,
                length=300,
                command=lambda v, 
                idx=i, 
                var=value_var: self.update_servo(idx, v, var)
            )
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.sliders.append((slider, value_var))
    '''
        # Create control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Center position button
        center_btn = ttk.Button(button_frame, text="Center All", command=self.center_all)
        center_btn.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_btn = ttk.Button(button_frame, text="Reset All", command=self.reset_all)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        # Save position button
        save_btn = ttk.Button(button_frame, text="Save Position", command=self.save_position)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Load position button
        load_btn = ttk.Button(button_frame, text="Load Position", command=self.load_position)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    ''' 
       
    def update_servo(self, idx, angleInput, value_var):
        #  Set Position
        angle = int(float(angleInput))
        self.controller.set_position(idx, position)

        # Set Labels
        value_var.set(f"{angle}°")
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