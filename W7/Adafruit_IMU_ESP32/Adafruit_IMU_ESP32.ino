#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define I2C_SDA 25
#define I2C_SCL 19  
TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;

float EMA_a = .3 //EMA alpha value where low pass = 

void setup(void) 
{
  Serial.begin(115200);
  I2CBNO.begin(I2C_SDA, I2C_SCL, 100000);
  bno = Adafruit_BNO055(55, 0x28, &I2CBNO);
  /* Initialise the sensor */
  if(!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  Serial.println("BNO started");
  delay(1000);
  bno.setExtCrystalUse(true);
}


void loop(void) 
{
  ///Euler Oreintation
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  Serial.print(euler.x());
  Serial.print(", ");
  Serial.print(euler.y());
  Serial.print(", ");
  Serial.print(euler.z());
  Serial.print(", ");

  ///Euler Accelerometer
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  Serial.print(euler.x());
  Serial.print(", ");
  Serial.print(euler.y());
  Serial.print(", ");
  Serial.println(euler.z());
  delay(500);
}