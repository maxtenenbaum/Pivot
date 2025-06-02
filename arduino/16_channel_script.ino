#include <Servo.h>

/*
This code is used for control of the 16 channel switchboard. 
After mapping the potentiometer values to channels, the middle of the channel range is added to the potVals array.
Upon starting the code, the servo is moved to the first channel and the user is prompted to enter the channel number.
This can be done directly via serial communication or though an automation script.
Upon reaching the desired channel, the relay is deactivated and an 'ok' message is printed to the serial monitor.
*/

// Pin definitions
const int potPin = A1;
const int servoPin = 6;
const int relayPin = A0;
Servo myServo;

int potVals[] = {10, 50, 125, 190, 275, 345, 400, 475, 540, 620, 685, 745, 815, 880, 950, 995};

int currentChannel = -1;

void pulseForward() {
  myServo.writeMicroseconds(1430);
  delay(20);
  myServo.writeMicroseconds(1500);
  delay(50);
}

void pulseBackward() {
  myServo.writeMicroseconds(1550);
  delay(20);
  myServo.writeMicroseconds(1500);
  delay(50);
}

int findIndex(int value) {
  for (int i = 0; i < 16; i++) {
    if (abs(value - potVals[i]) <= 5) { // Check if the value is within ±5 of the number
      return i + 1; // Return the index + 1 (1-based index)
    }
  }
  return -1; // Return -1 if no match is found
}

void findChannel() {
  while (findIndex(analogRead(potPin)) == -1) {
    pulseForward();
  }
  currentChannel = findIndex(analogRead(potPin));
}

void getChannel(int channelNumber) {
  digitalWrite(relayPin, HIGH);
  if (channelNumber < currentChannel) {
    while (currentChannel != channelNumber) {
      pulseBackward();
      currentChannel = findIndex(analogRead(potPin));
      Serial.println(currentChannel);
    }
  } else if (channelNumber > currentChannel) {
    while (currentChannel != channelNumber) {
      pulseForward();
      currentChannel = findIndex(analogRead(potPin));
      Serial.println(currentChannel);
    }
  }
  digitalWrite(relayPin, LOW);
  Serial.println("ok");
}

void initializeSwitch() {
  findChannel();
  if (currentChannel != 1) {
    getChannel(1);
  }
}

void setup() {
  myServo.attach(servoPin);
  Serial.begin(9600);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
  initializeSwitch();
  Serial.println("enter channel number");
}

const byte bufferSize = 10;
char inputBuffer[bufferSize];
byte index = 0;

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      inputBuffer[index] = '\0'; // null-terminate
      int channel = atoi(inputBuffer);
      getChannel(channel);
      index = 0; // reset buffer
    } else if (index < bufferSize - 1) {
      inputBuffer[index++] = c;
    }
  }
}
