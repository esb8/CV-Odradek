import tkinter as tk
from tkinter import ttk
import cv2
import PIL.Image, PIL.ImageTk
import threading
import time

# Import your camera module
import OpenCV

class ESP32CameraApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        # Get URL from imported module
        self.url = OpenCV.URL
        
        # Initialize camera
        self.init_camera()
        
        # Create GUI
        self.create_widgets()
        
        # Current frame placeholder
        self.current_frame = None
        
        # Start video stream in a separate thread
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Set window close handler
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start update loop
        self.update()
        
    def init_camera(self):
        """Initialize camera connection"""
        try:
            # Use the reconnect_camera function from your imported module
            self.cap = OpenCV.reconnect_camera(self.url)
            if self.cap is None:
                print("Failed to open video stream")
                return False
                
            # Set initial resolution using your existing function
            success = OpenCV.set_resolution(self.url, index=8, verbose=True)
            if not success:
                print("Failed to set initial resolution")
            
            # Use face_classifier from your module
            self.face_classifier = OpenCV.face_classifier
                
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False
            
    def create_widgets(self):
        # Video display area
        self.canvas = tk.Canvas(self.window, width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Controls area
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Resolution selection
        res_label = ttk.Label(control_frame, text="Resolution:")
        res_label.pack(side=tk.LEFT, padx=5)
        
        # Only include valid resolutions (remove empty strings)
        resolutions = ['0: QQVGA(160x120)', '3: HQVGA(240x176)', '4: QVGA(320x240)', 
                      '5: CIF(400x296)', '6: VGA(640x480)', '7: SVGA(800x600)', 
                      '8: XGA(1024x768)', '9: SXGA(1280x1024)', '10: UXGA(1600x1200)']
        
        # Create a mapping from resolution text to index value
        self.res_map = {}
        for res in resolutions:
            index = int(res.split(':')[0])
            self.res_map[res] = index
        
        # Set default to XGA (index 8)
        self.res_var = tk.StringVar(value='8: XGA(1024x768)')
        res_menu = ttk.Combobox(control_frame, textvariable=self.res_var, values=resolutions)
        res_menu.pack(side=tk.LEFT, padx=5)
        res_menu.bind("<<ComboboxSelected>>", self.change_resolution)
        
        # Face detection toggle
        self.face_var = tk.BooleanVar(value=True)
        face_check = ttk.Checkbutton(control_frame, text="Face Detection", variable=self.face_var)
        face_check.pack(side=tk.LEFT, padx=20)
        
        # Quality control
        quality_label = ttk.Label(control_frame, text="Quality:")
        quality_label.pack(side=tk.LEFT, padx=5)
        
        self.quality_var = tk.IntVar(value=10)
        quality_scale = ttk.Scale(control_frame, from_=10, to=63, variable=self.quality_var, 
                                 orient=tk.HORIZONTAL, length=100)
        quality_scale.pack(side=tk.LEFT, padx=5)

    
        # Apply quality button
        quality_btn = ttk.Button(control_frame, text="Apply Quality", 
                                command=self.change_quality)
        quality_btn.pack(side=tk.LEFT, padx=5)
        
        # AWB toggle button
        awb_btn = ttk.Button(control_frame, text="Toggle AWB", command=self.toggle_awb)
        awb_btn.pack(side=tk.LEFT, padx=10)
        
        # Reconnect button
        reconnect_btn = ttk.Button(control_frame, text="Reconnect", command=self.reconnect)
        reconnect_btn.pack(side=tk.RIGHT, padx=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(self.window, textvariable=self.status_var)
        status_label.pack(side=tk.BOTTOM, pady=5)
        
        # Bind resize event
        self.window.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        # Only process if it's the main window being resized
        if event.widget == self.window:
            # Update canvas size
            self.canvas.config(width=event.width-20, height=event.height-100)
        
    def change_resolution(self, event=None):
        """Handle resolution change from dropdown"""
        res_name = self.res_var.get()
        res_index = self.res_map[res_name]
        print(f"Changing resolution to {res_name} (index {res_index})")
        
        self.status_var.set(f"Changing resolution to {res_name}...")
        
        # Set resolution using the imported module's function
        if OpenCV.set_resolution(self.url, index=res_index, verbose=True):
            # Reconnect camera with new settings
            self.reconnect()
            self.status_var.set(f"Resolution set to {res_name}")
        else:
            self.status_var.set("Failed to change resolution")
            
    def change_quality(self):
        """Change camera quality"""
        quality = self.quality_var.get()
        print(f"Changing quality to {quality}")
        
        self.status_var.set(f"Changing quality to {quality}...")
        
        if OpenCV.set_quality(self.url, value=quality):
            self.reconnect()
            self.status_var.set(f"Quality set to {quality}")
        else:
            self.status_var.set("Failed to change quality")
            
    def toggle_awb(self):
        """Toggle auto white balance"""
        global AWB  # Use the global AWB variable from OpenCV module
        
        self.status_var.set("Toggling AWB...")
        
        # Toggle AWB using the imported module's function
        OpenCV.AWB = OpenCV.set_awb(self.url, OpenCV.AWB)
        
        self.status_var.set(f"AWB is now {'ON' if OpenCV.AWB else 'OFF'}")
            
    def reconnect(self):
        """Reconnect the camera after settings change"""
        print("Reconnecting camera from GUI...")
        self.status_var.set("Reconnecting camera...")
        
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        
        # Wait for camera to adjust to new settings
        time.sleep(2)
        
        # Use the reconnect function from imported module
        self.cap = OpenCV.reconnect_camera(self.url)
        
        if self.cap is not None and self.cap.isOpened():
            self.status_var.set("Camera reconnected successfully")
        else:
            self.status_var.set("Failed to reconnect camera")
        
    def video_loop(self):
        frame_count = 0
        start_time = time.time()
        
        while not self.stop_event.is_set():
            if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
                # Use the get_frame function from your module
                self.cap, frame = OpenCV.get_frame(self.cap, self.url)
                
                if frame is not None:
                    frame_count += 1
                    if frame_count >= 30:
                        fps = frame_count / (time.time() - start_time)
                        print(f"FPS: {fps:.2f}")
                        self.status_var.set(f"FPS: {fps:.2f}")
                        frame_count = 0
                        start_time = time.time()
                    
                    # Process face detection if enabled
                    if self.face_var.get():
                        try:
                            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            gray = cv2.equalizeHist(gray)
                            faces = self.face_classifier.detectMultiScale(gray)
                            for (x, y, w, h) in faces:
                                frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 4)
                        except Exception as e:
                            print(f"Face detection error: {e}")
                    
                    # Convert frame for display
                    self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                # If camera is disconnected, try to reconnect
                if hasattr(self, 'cap') and self.cap is None:
                    self.status_var.set("Camera disconnected. Attempting to reconnect...")
                    self.reconnect()
            
            time.sleep(0.01)  # Small delay to reduce CPU usage
            
    def update(self):
        if hasattr(self, 'current_frame') and self.current_frame is not None:
            try:
                # Convert OpenCV image to PhotoImage for Tkinter
                self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.current_frame))
                
                # Get canvas dimensions
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                
                # Center the image on the canvas
                self.canvas.create_image(canvas_width//2, canvas_height//2, 
                                        image=self.photo, anchor=tk.CENTER)
            except Exception as e:
                print(f"Update error: {e}")
            
        # Schedule next update
        self.window.after(30, self.update)
        
    def on_close(self):
        print("Closing application...")
        self.status_var.set("Closing application...")
        self.stop_event.set()
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        self.window.destroy()

def main():
    # Create root window
    root = tk.Tk()
    root.title("ESP32 Camera Viewer")
    root.geometry("1024x768")  # Set initial window size
    
    # Create app
    app = ESP32CameraApp(root, "ESP32 Camera Viewer")
    
    # Start GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
