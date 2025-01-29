//ต่อ limit switch เเบบ PULL DOWN
#include <AccelStepper.h>
#include <elapsedMillis.h>
#include "preset.h"

elapsedMillis printtime;

AccelStepper stepper1(AccelStepper::FULL2WIRE, step_pin, dir_pin);  // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

void setup() {

  Serial.begin(250000);
  pinMode(limit_switch, INPUT);
  stepper1.setMaxSpeed(max_speed);
  stepper1.setAcceleration(max_acceleration);
  stepper1.setSpeed(3000);
  delay(1000);
  homeing();
}

void homeing() {  //reset ตำเเหน่ง Home

  stepper1.setSpeed(-1200);  //set ความเร็วในการเคลื่อนที่ บอกความเร็วเเต่ไม่บอกระยะ ให้หมุนด้วยความเร็วนั้นไปเรื่อยๆ
                             //ความเร็วติดลบคือทิศทางนึงถ้าต้องการกลับทิศเปล๊่ยนเป็นบวก
  stepper1.runSpeed();       //สั่งทำงาน

  while (digitalRead(limit_switch == HIGH) && (home_state1 == false)) {
    stepper1.setCurrentPosition(0);
    stepper1.moveTo(1200);
    stepper1.runSpeed();

    home_state1 = true;
  }

  if (stepper1.currentPosition() == 1200) {
    stepper1.setSpeed(-500);  //set ความเร็วในการเคลื่อนที่ บอกความเร็วเเต่ไม่บอกระยะ ให้หมุนด้วยความเร็วนั้นไปเรื่อยๆ
                              //ความเร็วติดลบคือทิศทางนึงถ้าต้องการกลับทิศเปล๊่ยนเป็นบวก
    stepper1.runSpeed();      //สั่งทำงาน
    if (digitalRead(limit_switch == HIGH)) {
      home_state2 = true;
    }
  }

  while(home_state2 == true) {
    stepper1.setCurrentPosition(0);
    stepper1.setSpeed(0.00);
    stepper1.runSpeed();
    stepper1.stop();
    home_state2 = false;
    home_state1 = false;
    break;
  }
}

void loop() {
  if (Serial.available() > 0) {      //check serial value
    char incomeing = Serial.read();  //read serial value
    if (incomeing == '1') {
      stepper1.moveTo(400);        //เปลี่ยนเลข                            //ตำเเหน่งที่ต้องการให้เลื่อนไป ตำเเหน่งที่หนึ่ง
      stepper1.run();
    }
     else if (incomeing == '2') {                            //ที่สอง
      stepper1.moveTo(1400);
      stepper1.run();
    }
    else if (incomeing == '3') {                              //ที่สาม
      stepper1.moveTo(2400);
      stepper1.run();
    }

  }
}
