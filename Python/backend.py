# File: servo_backend.py
# This file contains the backend logic for controlling servos

import time
import json
import serial.tools.list_ports


class ServoController:
    def __init__(self, num_servos=3):
        self.connected = False
        self.servo_Array = [] * 5

    def connect(self):
        """Establish connection to servo hardware"""
        ports = serial.tools.list_ports.comports()
        serialInst = serial.Serial()
        portsList = []
    

        
        # Com Port
        for one in ports:
            portsList.append(str(one))
            print(str(one))
        #prompt
        com = input("select COM Port by #")
        for i in range(len(portsList)):
            if portsList[i].startswith("COM" + str(com)):
                use = "COM" + str(com)
                print(use)
    def reset(self):
        for array in servo_Array[]:
            array.set_position(0)

        

        serialInst.baudrate = 9600
        serialInst.port = use
        serialInst.open()


    '''
        while True:
            command = input("On/Off/exit")
            serialInst.write(command.encode('utf-8')) # converts to utf-8 

            if command == "exit":
                exit()
                
                print("Backend: Connecting to servo hardware...")
                time.sleep(0.5)
                self.connected = True
                print("Backend: Connected successfully!")
                return self.connected
'''       

class Servo:
    def __init__(self, id, angle):
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

        
    def disconnect(self):
        """Disconnect from servo hardware"""
        if self.connected:
            # In a real application, close connections properly
            # Example: self.serial.close()
            print("Backend: Disconnecting from servo hardware...")
            self.connected = False
            print("Backend: Disconnected.")
        return True
        
    ''' def set_all_positions(self, positions):
      
        return success
        
    def center_all(self):
        """Center all servos to 90°"""
        return self.set_all_positions([90] * self.num_servos)
        
    def reset_all(self):
        """Reset all servos to 0°"""
        return self.set_all_positions([0] * self.num_servos)
        
    def save_current_positions(self, name=None):
        """Save current positions for later retrieval"""
        if name is None:
            name = f"Position {len(self.saved_positions) + 1}"
            
        position_data = {
            "name": name,
            "timestamp": time.time(),
            "positions": self.servo_positions.copy()
        }
        
        self.saved_positions.append(position_data)
        
        # Save to a file
        with open("servo_positions.json", "w") as f:
            json.dump({"positions": self.saved_positions}, f, indent=2)
            
        print(f"Backend: Saved position set '{name}': {self.servo_positions}")
        return position_data
        
    def load_positions(self, index=None, name=None):
        """Load a previously saved position set"""
        if index is not None and 0 <= index < len(self.saved_positions):
            positions = self.saved_positions[index]["positions"]
            return self.set_all_positions(positions)
            
        if name is not None:
            for pos_set in self.saved_positions:
                if pos_set["name"] == name:
                    return self.set_all_positions(pos_set["positions"])
                    
        return False

        '''
   