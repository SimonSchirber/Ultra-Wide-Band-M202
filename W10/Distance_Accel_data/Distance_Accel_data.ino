#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define I2C_SDA 25
#define I2C_SCL 19  
TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;

#define BUTTON 35
bool calib = false;
int but_val = 0;

float ax_offset;
float ay_offset;
float az_offset;

long int t1 = 0;
long int last_print = 0;
long int last_print_time = 0;
long int prev_time = 0;

float ax = 0;
float ay = 0;
float az = 0;

float vel_x = 0;
float vel_y = 0;
float vel_z = 0;

float pos_x = 0;
float pos_y = 0;
float pos_z = 0;

void setup(void) 
{
  Serial.begin(115200);
  pinMode(BUTTON, INPUT);
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
  // ///Euler Oreintation
  // imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  // Serial.print(euler.x());
  // Serial.print(", ");
  // Serial.print(euler.y());
  // Serial.print(", ");
  // Serial.print(euler.z());
  // Serial.print(", ");
  but_val = digitalRead(BUTTON);
  if (but_val == 1){
    calib = true;
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax_offset = euler.x();
    ay_offset = euler.y();
    az_offset = euler.z();
    vel_x = 0;
    vel_y = 0;
    vel_z = 0;
    pos_x = 0;
    pos_y = 0;
    pos_z = 0;
    t1 = millis();
  }
  if (calib){
    ///Euler Accelerometer
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    float ax = euler.x() - ax_offset;
    float ay = euler.y() - ay_offset;
    float az = euler.z() - az_offset;
    long int t2 = millis();
  
  
    float dt = (t2 - prev_time)/1000.00;
    //Serial.println(dt, 4);

    vel_x += ax * dt;
    vel_y += ay * dt;
    vel_z += az * dt;

    pos_x += vel_x * dt;
    pos_y += vel_y * dt;
    pos_z += vel_z * dt;
    //Print Every Second
    if (t2 - last_print_time > 1000){
      Serial.print((t2-t1)/1000);
      Serial.print(", ");
      Serial.print(ax, 3);
      Serial.print(", ");
      Serial.print(ay, 3);
      Serial.print(", ");
      Serial.print(az, 3);
      Serial.print(", ");
      Serial.print(vel_x, 3);
      Serial.print(", ");
      Serial.print(vel_y, 3);
      Serial.print(", ");
      Serial.print(vel_z, 3);
      Serial.print(", ");
      Serial.print(pos_x, 3);
      Serial.print(", ");
      Serial.print(pos_y, 3);
      Serial.print(", ");
      Serial.println(pos_z, 3);
      last_print_time = t2;
    }
    prev_time = t2;
  }
  else{
    delay(1000);
    Serial.print("Press Button when Calibrated: ");
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    Serial.print(euler.x());
    Serial.print(", ");
    Serial.print(euler.y());
    Serial.print(", ");
    Serial.println(euler.z());
  }
}