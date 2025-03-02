# File: main.py
# This file runs the application by connecting the frontend to the backend

import tkinter as tk
from backend import ServoController
from gui import ServoControlGUI

def main():
    # Initialize the backend controller
    controller = ServoController(num_servos=3)
    
    # Connect to servo hardware
    if controller.connect():
        # Create the GUI window
        root = tk.Tk()
        
        # Create the GUI and connect it to the controller
        app = ServoControlGUI(root, controller)
        
        # Set up cleanup on window close
        root.protocol("WM_DELETE_WINDOW", lambda: cleanup_and_exit(root, controller))
        
        # Start the main loop
        root.mainloop()
    else:
        print("Failed to connect to servo hardware. Exiting.")

def cleanup_and_exit(root, controller):
    """Properly disconnect from hardware before exiting"""
    controller.disconnect()
    root.destroy()

if __name__ == "__main__":
    main()