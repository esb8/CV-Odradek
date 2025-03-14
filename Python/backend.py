# File: servo_backend.py
# This file contains the backend logic for controlling servos
# File will contain different servo functions
# Backend recieves data and sends it directly to ESP which sends to ARDUINO

class Servo:
    def __init__(self, id, angle, num_sources=3):
        self.id = id
        self.angle = angle

    #init postions, use when conecting servos
    def set_position(self, servo_id, angle):
        self.id = servo_id
        self.angle = angle
        # Implememnt servo moves
        return False
    
    def get_position(self):
        return self.id + self.angle
        
    def reset_position(self):
        self.id = 0

    def get_closest_face(self, x_angle, y_angle, distance):
        self.x_angle = x_angle
        self.y_angle = y_angle
        self.distance = distance
        face_data_string = f"X Angle: {x_angle}, Y Angle: {x_angle}, Distance: {distance}"
        
        return face_data_string
                
    def disconnect(self):
        """Disconnect from servo hardware"""
        if self.connected:
            # In a real application, close connections properly
            # Example: self.serial.close()
            print("Backend: Disconnecting from servo hardware...")
            self.connected = False
            print("Backend: Disconnected.")
        return True  
    
