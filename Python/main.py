# Template
from backend import Servo
from CamGUI import ESP32CameraTracker
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32CameraTracker(root)
root.mainloop()

