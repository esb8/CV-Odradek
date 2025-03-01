servo s1;
int servoPin = 4;
String incoming = Serial.read()

bool ledState = false; 

void setup() {
  Serial.begin(9600); 

  s1.attach(servoPin);
}

void loop() {
  switch incoming {
    // incoming == "Manual"
    // incoming == "Standby"
    incoming == "ON":
    s1.write(10)
    Serial.print(s1.read)
    incoming == "OFF"
    s1.write(180)
    Serial.print(s1.read)
  }
}
