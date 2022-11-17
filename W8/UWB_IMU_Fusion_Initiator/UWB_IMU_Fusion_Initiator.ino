#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

//IO 18 not avaiable, potential IO = 5, 35, 26
#define I2C_SDA 25
#define I2C_SCL 19
//IO 18 not avaiable, potential IO = 5, 35, 26
#define BUTTON 35
#define LED 5
int but_val = 0;

TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;
//Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);


void setup(void) 
{
  Serial.begin(9600);
  pinMode(BUTTON, INPUT);
  pinMode(LED, OUTPUT);
  Serial.println("Orientation Sensor Test"); 
  /* Initialise the sensor */
  I2CBNO.begin(I2C_SDA, I2C_SCL, 100000);
  bno = Adafruit_BNO055(55, 0x28, &I2CBNO);
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  
  delay(1000);
    
  bno.setExtCrystalUse(true);
}
void loop(){
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  /* Display the floating point data */
  Serial.print("");
  Serial.print(euler.x());
  Serial.print(", ");
  Serial.print(euler.y());
  Serial.print(", ");
  Serial.println(euler.z());
  but_val = digitalRead(BUTTON);
  if (but_val == 1){
    digitalWrite(LED, HIGH);
  }
  else{
    digitalWrite(LED, LOW);
  }
  

  
  


}
