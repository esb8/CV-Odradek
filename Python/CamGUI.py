import cv2
import numpy as np
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import PIL.Image, PIL.ImageTk
import math
import time
from backend import Servo

class ESP32CameraTracker:
    def __init__(self, root, servo=None):
        self.root = root
        self.root.title("ESP32 Camera Face Tracking")
        self.root.geometry("1200x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.servo = servo if servo is not None else Servo
        
        # Variables
        self.camera_url = tk.StringVar(value="http://10.0.0.15")
        self.awb_enabled = tk.BooleanVar(value=True)
        self.is_streaming = False
        self.thread = None
        self.stopEvent = None
        
        # Camera parameters (will be calibrated)
        self.focal_length = 800  # Approximate focal length in pixels
        self.known_face_width = 16.0  # Average human face width in cm
        
        # Face tracking parameters
        self.track_faces = tk.BooleanVar(value=True)
        self.show_distance = tk.BooleanVar(value=True)
        
        # For calibration
        self.calibration_pending = False
        self.calibration_distance = 0
        
        # Face detection
        self.face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        
        # Create GUI
        self.create_gui()
        
        # Log message
        self.log("Application started")
    
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top controls
        controls_frame = ttk.LabelFrame(main_frame, text="Camera Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # URL and Connect
        url_frame = ttk.Frame(controls_frame)
        url_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(url_frame, text="ESP32 Camera URL:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(url_frame, textvariable=self.camera_url, width=30).pack(side=tk.LEFT, padx=5)
        self.connect_button = ttk.Button(url_frame, text="Connect", command=self.toggle_stream)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Calibration button
        ttk.Button(url_frame, text="Calibrate", command=self.calibrate_camera).pack(side=tk.LEFT, padx=15)
        
        # Resolution and Quality
        settings_frame = ttk.Frame(controls_frame)
        settings_frame.pack(fill=tk.X, pady=5)
        
        # Resolution
        ttk.Label(settings_frame, text="Resolution:").pack(side=tk.LEFT, padx=5)
        self.resolution_combobox = ttk.Combobox(settings_frame, width=15)
        self.resolution_combobox['values'] = (
            "UXGA (1600x1200)", 
            "SXGA (1280x1024)", 
            "XGA (1024x768)", 
            "SVGA (800x600)", 
            "VGA (640x480)", 
            "CIF (400x296)", 
            "QVGA (320x240)", 
            "HQVGA (240x176)", 
            "QQVGA (160x120)"
        )
        self.resolution_combobox.current(2)  # Default to XGA
        self.resolution_combobox.pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text="Set", command=self.set_resolution).pack(side=tk.LEFT, padx=5)
        
        # Quality
        ttk.Label(settings_frame, text="Quality (10-63):").pack(side=tk.LEFT, padx=5)
        self.quality_spinbox = ttk.Spinbox(settings_frame, from_=10, to=63, width=5)
        self.quality_spinbox.set(10)
        self.quality_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_frame, text="Set", command=self.set_quality).pack(side=tk.LEFT, padx=5)
        
        # AWB
        ttk.Checkbutton(settings_frame, text="Auto White Balance", variable=self.awb_enabled, 
                        command=self.toggle_awb).pack(side=tk.LEFT, padx=20)
        
        # Face tracking settings
        tracking_frame = ttk.Frame(controls_frame)
        tracking_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(tracking_frame, text="Track Faces", variable=self.track_faces).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(tracking_frame, text="Show Distance", variable=self.show_distance).pack(side=tk.LEFT, padx=5)
        
        # Video frame
        video_frame = ttk.LabelFrame(main_frame, text="Camera Feed", padding=10)
        video_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.video_label = ttk.Label(video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Status and Log
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        status_frame = ttk.LabelFrame(bottom_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Disconnected")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.distance_label = ttk.Label(status_frame, text="Distance: --")
        self.distance_label.pack(side=tk.LEFT, padx=10)
        
        self.angle_label = ttk.Label(status_frame, text="Angle: --")
        self.angle_label.pack(side=tk.LEFT, padx=10)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, pady=5)
        
        # Create a Text widget with a Scrollbar
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_text_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """Add a log message to the log text widget"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def toggle_stream(self):
        """Toggle camera stream on/off"""
        if self.is_streaming:
            self.stop_stream()
            self.connect_button.config(text="Connect")
        else:
            self.start_stream()
            self.connect_button.config(text="Disconnect")
   
    def start_stream(self):
        """Start the camera stream and face detection"""
        url = self.camera_url.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
        
        self.log(f"Connecting to camera at {url}")
        self.status_label.config(text=f"Connecting to {url}...")
        
        # Create a thread that will handle the streaming
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args=())
        self.thread.daemon = True
        self.thread.start()
    
    def stop_stream(self):
        """Stop the camera stream"""
        if self.stopEvent is not None:
            self.log("Disconnecting from camera")
            self.status_label.config(text="Disconnected")
            self.stopEvent.set()
            self.is_streaming = False
            
            # Clear the image
            self.video_label.config(image='')
            
            # Reset info labels
            self.distance_label.config(text="Distance: --")
            self.angle_label.config(text="Angle: --")
    
    def calibrate_camera(self):
        """Calibrate the camera for distance calculation"""
        if not self.is_streaming:
            messagebox.showerror("Error", "Please connect to the camera first")
            return
        
        calibration_dialog = tk.Toplevel(self.root)
        calibration_dialog.title("Camera Calibration")
        calibration_dialog.geometry("400x200")
        calibration_dialog.transient(self.root)
        calibration_dialog.grab_set()
        
        ttk.Label(calibration_dialog, text="Enter the known distance to your face (cm):").pack(pady=10)
        known_distance_var = tk.DoubleVar(value=100.0)
        ttk.Entry(calibration_dialog, textvariable=known_distance_var).pack(pady=5)
        
        ttk.Label(calibration_dialog, text="Enter actual face width (cm):").pack(pady=10)
        face_width_var = tk.DoubleVar(value=self.known_face_width)
        ttk.Entry(calibration_dialog, textvariable=face_width_var).pack(pady=5)
        
        def do_calibration():
            known_distance = known_distance_var.get()
            actual_face_width = face_width_var.get()
            
            if known_distance <= 0 or actual_face_width <= 0:
                messagebox.showerror("Error", "Please enter positive values")
                return
            
            self.known_face_width = actual_face_width
            # We'll use the next detected face to calibrate
            self.calibration_pending = True
            self.calibration_distance = known_distance
            self.log(f"Calibration initiated: {actual_face_width}cm face width at {known_distance}cm")
            calibration_dialog.destroy()
        
        ttk.Button(calibration_dialog, text="Calibrate", command=do_calibration).pack(pady=20)
    
    def video_loop(self):
        """Background thread to fetch frames and do face detection"""
        url = self.camera_url.get()

        stream_urls = [
        f"{url}:81/stream",  # Original approach
        f"{url}/mjpeg/1",    # Alternative MJPEG stream
        f"{url}/stream",     # Another common endpoint
        url                  # Direct camera URL
    ]
    
        for stream_url in stream_urls:
            cap = cv2.VideoCapture(stream_url)
        
        # Add a connection timeout and retry mechanism
            cap.set(cv2.CAP_PROP_CONNECT_TIMEOUT, 10)  # 5 second timeout
        
            if cap.isOpened():
                self.log(f"Connected successfully using {stream_url}")
                break
    
            if not cap.isOpened():
                self.log("Failed to connect to camera stream")
                return

        # For FPS calculation
        last_time = time.time()
        frame_count = 0
        
        try:
            while not self.stopEvent.is_set():
                ret, frame = cap.read()
                if not ret:
                    self.log("Failed to get frame from camera")
                    break
                
                # Calculate FPS
                frame_count += 1
                if frame_count >= 10:
                    current_time = time.time()
                    fps = frame_count / (current_time - last_time)
                    # Update status with FPS
                    self.status_label.config(text=f"Connected to {url} (FPS: {fps:.1f})")
                    frame_count = 0
                    last_time = current_time
                
                # Get frame dimensions
                frame_height, frame_width = frame.shape[:2]
                frame_center_x = frame_width // 2
                frame_center_y = frame_height // 2
                
                # Default values when no face is detected
                closest_face = None
                
                # Face detection if enabled
                if self.track_faces.get():
                    gray = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
                    gray = cv2.equalizeHist(gray)
                    gray = cv2.GaussianBlur(gray, (5, 5), 0)
                    
                    faces = self.face_classifier.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )
                    
                    # Process detected faces
                    min_distance = float('inf')
                    
                    for (x, y, w, h) in faces:
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 4)
                        
                        # Calculate face center
                        face_center_x = x + w // 2
                        face_center_y = y + h // 2
                        
                        # Draw face center
                        cv2.circle(frame, (face_center_x, face_center_y), 5, (0, 255, 0), -1)
                        
                        # Draw line from image center to face center
                        cv2.line(frame, (frame_center_x, frame_center_y), 
                                (face_center_x, face_center_y), (0, 255, 255), 2)
                        
                        # Calculate distance based on face width
                        distance = (self.known_face_width * self.focal_length) / w
                        
                        # Check if this is calibration
                        if self.calibration_pending:
                            self.focal_length = (w * self.calibration_distance) / self.known_face_width
                            self.log(f"Camera calibrated: focal length = {self.focal_length:.1f} pixels")
                            self.calibration_pending = False
                        
                        # Calculate angles (in degrees)
                        # Horizontal angle: positive is right, negative is left
                        horizontal_angle = math.degrees(math.atan2(face_center_x - frame_center_x, self.focal_length))
                        
                        # Vertical angle: positive is down, negative is up
                        vertical_angle = math.degrees(math.atan2(face_center_y - frame_center_y, self.focal_length))
                        
                        # Add distance and angle text to frame
                        if self.show_distance.get():
                            distance_text = f"Distance: {distance:.1f}cm"
                            angle_text = f"H: {horizontal_angle:.1f}° V: {vertical_angle:.1f}°"
                            cv2.putText(frame, distance_text, (x, y - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            cv2.putText(frame, angle_text, (x, y - 30), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Keep track of closest face
                        if distance < min_distance:
                            min_distance = distance
                            closest_face = (horizontal_angle, vertical_angle, distance)
                
                # Update GUI labels if a face was detected
                if closest_face:
                    h_angle, v_angle, dist = closest_face
                    self.root.after(0, lambda a=dist, b=h_angle, c=v_angle: 
                                    self.update_info_labels(a, b, c))
                    Servo.get_closest_face(closest_face)
                    
                # Convert to PIL format and display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = PIL.Image.fromarray(frame_rgb)
                tk_img = PIL.ImageTk.PhotoImage(image=pil_img)
                
                # Update the image in the GUI (thread-safe)
                self.root.after(0, lambda img=tk_img: self.update_image(img))
        
        except Exception as e:
            self.log(f"Error in video loop: {str(e)}")
        finally:
            cap.release()
            if not self.stopEvent.is_set():
                self.stop_stream()
                self.connect_button.config(text="Connect")
    
    def update_image(self, img):
        """Update the image in the GUI (called from main thread)"""
        self.video_label.config(image=img)
        self.video_label.image = img  # Keep a reference
    
    def update_info_labels(self, distance, h_angle, v_angle):
        """Update the distance and angle labels (called from main thread)"""
        self.distance_label.config(text=f"Distance: {distance:.1f}cm")
        self.angle_label.config(text=f"Angle: H:{h_angle:.1f}° V:{v_angle:.1f}°")
    
    def set_resolution(self):
        """Set the camera resolution"""
        if not self.is_streaming:
            self.log("Connect to camera first")
            return
        
        url = self.camera_url.get()
        resolution_idx = self.resolution_combobox.current()
        
        # Convert combobox index to the correct resolution index
        idx_mapping = {0: 10, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 0}
        resolution_value = idx_mapping.get(resolution_idx, 8)  # Default to XGA if not found
        
        try:
            response = requests.get(f"{url}/control?var=framesize&val={resolution_value}")
            if response.status_code == 200:
                self.log(f"Resolution set to {self.resolution_combobox.get()}")
            else:
                self.log(f"Failed to set resolution: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"Error setting resolution: {str(e)}")
    
    def set_quality(self):
        """Set the camera quality"""
        if not self.is_streaming:
            self.log("Connect to camera first")
            return
        
        url = self.camera_url.get()
        try:
            quality_value = int(self.quality_spinbox.get())
            if quality_value < 10 or quality_value > 63:
                self.log("Quality must be between 10 and 63")
                return
            
            response = requests.get(f"{url}/control?var=quality&val={quality_value}")
            if response.status_code == 200:
                self.log(f"Quality set to {quality_value}")
            else:
                self.log(f"Failed to set quality: HTTP {response.status_code}")
        except ValueError:
            self.log("Please enter a valid number for quality")
        except Exception as e:
            self.log(f"Error setting quality: {str(e)}")
    
    def toggle_awb(self):
        """Toggle auto white balance"""
        if not self.is_streaming:
            self.log("Connect to camera first")
            return
        
        url = self.camera_url.get()
        awb_value = 1 if self.awb_enabled.get() else 0
        
        try:
            response = requests.get(f"{url}/control?var=awb&val={awb_value}")
            if response.status_code == 200:
                self.log(f"AWB {'enabled' if self.awb_enabled.get() else 'disabled'}")
            else:
                self.log(f"Failed to set AWB: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"Error setting AWB: {str(e)}")
    
    def on_closing(self):
        """Handle window close event"""
        if self.thread is not None:
            self.stop_stream()
        self.root.destroy()

