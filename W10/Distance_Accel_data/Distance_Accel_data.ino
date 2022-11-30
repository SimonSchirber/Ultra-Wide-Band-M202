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

const float pi = 3.14159267;
const float gravity = 9.81;

long int t1 = 0;
long int last_print = 0;
long int last_print_time = 0;
long int prev_time = 0;

float ax_offset;
float ay_offset;
float az_offset;

float alpha = 0;
float beta = 0;
float Gamma = 0;

float ax = 0;
float ay = 0;
float az = 0;
///Translated Accelerations
float ax_x = 0;
float ax_y = 0;
float ax_z = 0;

float ay_x = 0;
float ay_y = 0;
float ay_z = 0;

float az_x = 0;
float az_y = 0;
float az_z = 0;
//Translated onto real axis acceleration
float axT = 0;
float ayT = 0;
float azT = 0;

float vel_x = 0;
float vel_y = 0;
float vel_z = 0;

float pos_dx = 0;
float pos_dy = 0;
float pos_dz = 0;

float pos_x = 0;
float pos_y = 0;
float pos_z = 0;


void setup(void) {
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

float radian(float degrees) {
  float radians = degrees * pi / 180.0;
  return radians;
}

void TranslateAccel(){
  ax_x = ax * cos(radian(alpha)) * cos(radian(beta));
  ax_y = ax * sin(radian(alpha)) * cos(radian(beta));
  ax_z = -ax * sin(radian(beta));

  ay_x = ay * cos(radian(alpha))* sin(radian(beta))* cos(radian(Gamma)) + sin(radian(alpha))*cos(radian(Gamma));
  ay_y = ay * sin(radian(alpha))* sin(radian(beta))* sin(radian(Gamma)) + cos(radian(alpha))*cos(radian(Gamma));
  ay_z = ay * cos(radian(beta)) * sin(radian(Gamma));

  az_x = az * cos(radian(alpha)) * sin(radian(beta))* cos(radian(Gamma)) + sin(radian(alpha)) * sin(radian(Gamma));
  az_y = az * sin(radian(alpha)) * sin(radian(beta))* cos(radian(Gamma)) - cos(radian(alpha)) * sin(radian(Gamma));
  az_z = az * cos(radian(beta)) * cos(radian(Gamma));

  axT = ax_x + ay_x + az_x;
  ayT = ax_y + ay_y + az_y;
  azT = ax_z + ay_z + az_z;
}

void loop(void) 
{
  but_val = digitalRead(BUTTON);
  //Get Offset values once calibrated
  if (but_val == 1){
    Serial.println("Calibrating");
    calib = true;
    delay(500);
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax_offset = euler.x();
    ay_offset = euler.y();
    az_offset = euler.z() - gravity;
    vel_x = 0;
    vel_y = 0;
    vel_z = 0;
    pos_x = 0;
    pos_y = 0;
    pos_z = 0;
    t1 = millis();
  }
  if (calib){
    //Time since last call
    long int t2 = millis();
    float dt = (t2 - prev_time)/1000.00;

     ///Euler Oreintation
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    alpha = euler.x();
    beta = euler.y();
    Gamma = euler.z();
    ///Euler Accelerometer
    euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax = euler.x() - ax_offset;
    ay = euler.y() - ay_offset;
    az = euler.z() - az_offset;

    TranslateAccel();

    vel_x += axT * dt;
    vel_y += ayT * dt;
    vel_z += (azT - gravity) * dt;
    //Absolute Position Move
    pos_x += vel_x * dt;
    pos_y += vel_y * dt;
    pos_z += vel_z * dt;
    //Position Move since last Read
    pos_dx += 0;
    pos_dy += 0;
    pos_dz += 0;



    //Print/send updates over com Every Quarter Second
    if (t2 - last_print_time > 100){
      Serial.print((t2-t1)/1000);
      Serial.print(", ");
      Serial.print(alpha, 3);
      Serial.print(", ");
      Serial.print(beta, 3);
      Serial.print(", ");
      Serial.print(Gamma, 3);
      Serial.print(", ");
      Serial.print(axT, 3);
      Serial.print(", ");
      Serial.print(ayT, 3);
      Serial.print(", ");
      Serial.println(azT, 3);

      Serial.print(ax, 3);
      Serial.print(", ");
      Serial.print(ay, 3);
      Serial.print(", ");
      Serial.println(az, 3);

      last_print_time = t2;

      pos_dx = 0;
      pos_dy = 0;
      pos_dz = 0;
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