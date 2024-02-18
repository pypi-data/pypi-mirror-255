#include <Arduino.h>
#include <AS5600_AS.h>

const int potPin = A3;
const int motorPin = 5;

const int RUN = 1;
const int STOP = 2;

const int inSize = 2;
// unsigned int inBuffer[inSize];
byte inBuffer[inSize];

const int outSize = 3;
// unsigned int outBuffer[outSize];
byte outBuffer[outSize];

AS5600 as5600;


void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  Wire.begin();
  as5600.setWirePtr(&Wire);
  as5600.begin();
}


// void receive_ascii() {
//   static char del = ',';
//   int i0 = 0;
//   int ival = 0;
//   String in = Serial.readStringUntil('\r');
//   for (unsigned int i = 0; i < in.length(); i++)
//   {
//     if (in[i] == del) {
//       inBuffer[ival] = in.substring(i0, i).toInt();
//       i0 = i + 1;
//       ival++;
//     }
//   }
// }


// void send_ascii() {
//   static char del = ',';
//   String out = "";
//   for (int i = 0; i < outSize; i++)
//   {
//     out += String(outBuffer[i]) + del;
//   }
//   Serial.println(out);
// }


void receive_bytes() {
  Serial.readBytes(inBuffer, inSize);
}


void send_bytes() {
  Serial.write(outBuffer, outSize);
}


void receive(){
  receive_bytes();
}


void send(){
  send_bytes();
}


void loop() {
  if (Serial.available() > 0){
    receive();
    switch(inBuffer[0]) {
      case RUN:
        {
          analogWrite(motorPin, inBuffer[1]);

          int pot = analogRead(potPin);
          uint16_t angle = as5600.rawAngle();

          outBuffer[0] = ((pot >> 4) & 0xF0) + (angle >> 8);
          outBuffer[1] = pot & 0xFF;
          outBuffer[2] = angle & 0xFF;

          // outBuffer[0] = pot;
          // outBuffer[1] = angle;

          break;
        }

      case STOP:
        analogWrite(motorPin, 0);

        break;
    }
    send();
  }
}
