#include <Servo.h>
#define NUM_SERVOS 2
Servo servos[NUM_SERVOS]; // Create servo objects

void setup() {
  int servoPins[] = {9, 10};
    Serial.begin(115200); // Must match ESP8266 baud rate

  for (int i = 0; i < NUM_SERVOS; i++) {
    Serial.print("Servo ");
    Serial.print(i + 1);
    Serial.println("Attached to pin ");
    Serial.println(servoPins[i]);
  }
}

void loop() {
}

void parseAndExecuteCommand(String command) {
  if (command.startsWith("S")) {
    handleMoveCommand(command);
  }
  
  else if (command.startsWith("A")) {
    handleAllServosCommand(command);
  }
  /*
  else if (command.startsWith("R")) {
    handleReadCommand(command);
  }
  */
}

// Handle command to move all servos (format: "A:45")
void handleAllServosCommand(String command) {
  int colonIndex = command.indexOf(':');
  if (colonIndex > 0) {
    int position = command.substring(colonIndex + 1).toInt();
    moveAllServos(position);
  }
}

// Handle command to move a specific servo (format: "S1:90")
void handleMoveCommand(String command) {
  int colonIndex = command.indexOf(':');
  if (colonIndex > 1) {
    //from, to
    int servoIndex = command.substring(1, colonIndex).toInt() - 1;
    int position = command.substring(colonIndex + 1).toInt();
    moveServo(servoIndex, position);
  }
}

void moveAllServos(int position) {
  if (isValidPosition(position)) {
    for (int i = 0; i < NUM_SERVOS; i++) {
      servos[i].write(position);
    }
    Serial.print("All servos moved to ");
    Serial.println(position);
  } else {
    Serial.println("Error: Invalid position");
  }
}

void moveServo(int servoIndex, int position) {
  if (isValidServo(servoIndex) && isValidPosition(position)) {
    servos[servoIndex].write(position);
    // Send confirmation
    Serial.print("Servo ");
    Serial.print(servoIndex + 1);
    Serial.print(" moved to ");
    Serial.println(position);
  } else {
    Serial.println("Error: Invalid servo or position");
  }
}


// Check if servo index is valid
bool isValidServo(int servoIndex) {
  return (servoIndex >= 0 && servoIndex < NUM_SERVOS);
}

// Check if position is valid
bool isValidPosition(int position) {
  return (position >= 0 && position <= 180);
}
