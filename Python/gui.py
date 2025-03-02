import tkinter as tk
from tkinter import ttk
import time

class ServoControlGUI:
    def __init__(self, root, num_servos=3):
        self.root = root
        self.root.title("Servo Control Panel")
        self.root.geometry("500x400")
        self.num_servos = num_servos
        self.servo_values = [0] * num_servos
        
        # Create the main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = ttk.Label(main_frame, text="Servo Control System", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # Create frame for servo controls
        self.servo_frame = ttk.LabelFrame(main_frame, text="Servo Controls")
        self.servo_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create sliders for each servo
        self.sliders = []
        for i in range(num_servos):
            frame = ttk.Frame(self.servo_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
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
                command=lambda v, idx=i, var=value_var: self.update_servo(idx, v, var)
            )
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.sliders.append((slider, value_var))
            
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
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_servo(self, idx, value, value_var):
        # Convert to integer
        position = int(float(value))
        self.servo_values[idx] = position
        value_var.set(f"{position}°")
        
        # Here you would add the code to actually control the servo
        # For example: servo.write(position)
        self.status_var.set(f"Servo {idx+1} moved to position {position}°")
        
    def center_all(self):
        for i, (slider, value_var) in enumerate(self.sliders):
            slider.set(90)
            self.servo_values[i] = 90
            value_var.set("90°")
        self.status_var.set("All servos centered at 90°")
    def reset_all(self):
        for i, (slider, value_var) in enumerate(self.sliders):
            slider.set(0)
            self.servo_values[i] = 0
            value_var.set("0°")
        self.status_var.set("All servos reset to 0°")
        
    def save_position(self):
        position_str = ", ".join([f"{val}°" for val in self.servo_values])
        self.status_var.set(f"Position saved: {position_str}")
        # Here you could add code to save positions to a file
        print(f"Saved positions: {self.servo_values}")


# Simulate connection to servos
def connect_to_servos():
    # In a real application, this would establish connection to servo hardware
    print("Connecting to servo hardware...")
    time.sleep(0.5)
    print("Connected successfully!")
    return True

# Main function to run the application
def main():
    # Initialize servo connection
    connected = connect_to_servos()
    
    # Create the GUI
    root = tk.Tk()
    app = ServoControlGUI(root)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()