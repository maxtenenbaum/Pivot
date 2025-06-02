#include <Servo.h>

/*
This code is for mapping the potentiometer to the switch
Via serial communicaiton, characters 'a' and 'd' are used to move the servo forward and backward in pulsed steps and the potentiometer value is printed to the serial monitor.
Characters 'q' and 'e' are used to move the servo to the left and right at full speed. 's' is used to stop the servo.
*/

// Pin definitions
const int potPin = A2;
const int servoPin = 6;
const int relayPin = A1;
Servo myServo;

// Function definitions
void pulseForward() {
  myServo.writeMicroseconds(1400);
  delay(10);
  myServo.writeMicroseconds(1500);
}

void pulseBackward() {
  myServo.writeMicroseconds(1570);
  delay(10);
  myServo.writeMicroseconds(1500);
}

void setup() {
  myServo.attach(servoPin);
  Serial.begin(9600);
  
  pinMode(relayPin, OUTPUT);  
  digitalWrite(relayPin, HIGH);  
  
  delay(200); 
}

void loop() {
  if (Serial.available() > 0) {
    char input = Serial.read();

    if (input == 'a') {
      pulseBackward();
      delay(100);
      Serial.println(analogRead(potPin)); 
    } else if (input == 'd') {
      pulseForward();
      delay(100);
      Serial.println(analogRead(potPin)); 
    } else if (input == 'q') {
      myServo.writeMicroseconds(1430);
    } else if (input == 'e') {
      myServo.writeMicroseconds(1550);
    } else if (input == 's') {
      myServo.writeMicroseconds(1500);
    }
  }
}
