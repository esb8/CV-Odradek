# Template

import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

com = input("select COM Port by #")
for i in range(len(portsList)):
    if portsList[i].startswith("COM" + str(com)):
        use = "COM" + str(com)
        print(use)

serialInst.baudrate = 9600
serialInst.port = use
serialInst.open()

while True:
    command = input("On/Off/exit")
    serialInst.write(command.encode('utf-8')) # converts to utf-8 

    if command == "exit":
        exit()
        
# Template Code
# Implement 3 commands 
# Implement sensor

