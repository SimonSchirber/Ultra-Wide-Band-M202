#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

///IMU Wire  I2C Initialization 
#define I2C_SDA 25
#define I2C_SCL 19  
TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;
///Button Declaration
#define BUTTON 35

bool calib = false;
int but_val = 0;
const float pi = 3.14159267;
const float gravity = 9.81;
//Time changes to determine relative change in position
long int t1 = 0, last_print = 0, last_print_time = 0, prev_time = 0;

//Sensor Reading: Euler Angles
float alpha = 0, alphaT, alpha_offset = 0, beta = 0, Gamma = 0;
//Sensor Reading: Accelerations
float ax = 0, ay = 0, az = 0;
//Acceleration Drift Offsets
float ax_offset, ay_offset, az_offset;
//Acceleration Translated summations
float ax_x = 0, ax_y = 0, ax_z = 0;
float ay_x = 0, ay_y = 0, ay_z = 0;
float az_x = 0, az_y = 0, az_z = 0;
//Translated axis accelerations
float axT = 0, ayT = 0, azT = 0;
//Accumuluated Velocities
float vel_x = 0, vel_y = 0, vel_z = 0;
//Velocity Changes (Every Print)
float vel_dx = 0, vel_dy = 0, vel_dz = 0;
//Accumulated positions
float pos_x = 0, pos_y = 0, pos_z = 0;
//Position changes (Every Print)
float pos_dx = 0, pos_dy = 0, pos_dz = 0;

void setup(void) {
  Serial.begin(115200);
  pinMode(BUTTON, INPUT);
  I2CBNO.begin(I2C_SDA, I2C_SCL, 100000);
  bno = Adafruit_BNO055(55, 0x28, &I2CBNO);
  if(!bno.begin())
  {
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
  ax_z = - ax * sin(radian(beta));

  ay_x = ay * (cos(radian(alpha))* sin(radian(beta))* cos(radian(Gamma)) + sin(radian(alpha))*cos(radian(Gamma)));
  ay_y = ay * (sin(radian(alpha))* sin(radian(beta))* sin(radian(Gamma)) + cos(radian(alpha))*cos(radian(Gamma)));
  ay_z = ay * cos(radian(beta)) * sin(radian(Gamma));

  az_x = az * (cos(radian(alpha)) * sin(radian(beta))* cos(radian(Gamma)) + sin(radian(alpha)) * sin(radian(Gamma)));
  az_y = az * (sin(radian(alpha)) * sin(radian(beta))* cos(radian(Gamma)) - cos(radian(alpha)) * sin(radian(Gamma)));
  az_z = az * (cos(radian(beta)) * cos(radian(Gamma)));

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
    Serial.println("Offsets (ax ay az): ");
    Serial.print(ax_offset); Serial.print(", "); Serial.print(ay_offset); Serial.print(", "); Serial.println(az_offset ); Serial.println(); Serial.println();
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    alpha_offset = euler.x(); 
    vel_x = 0; vel_y = 0; vel_z = 0;
    pos_x = 0; pos_y = 0; pos_z = 0;
    t1 = millis();
  }
  if (calib){
    //Time since last call
    long int t2 = millis();
    float dt = (t2 - prev_time)/1000.00;
    //Euler Oreintation
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    alpha = euler.x();
    alphaT = euler.x() - alpha_offset;
    if (alpha_offset < 0){
      alpha_offset += 360;}
    //alpha = alpha_offset;
    beta = euler.y();
    Gamma = euler.z();
    ///Euler Accelerometer
    euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax = euler.x() - ax_offset;
    ay = euler.y() - ay_offset;
    az = -(euler.z() - az_offset);
    //Do tranlation accel calculations
    TranslateAccel();
    //Velocity Change (Zeroed at Every Print)
    vel_dx += axT * dt;
    vel_dy += ayT * dt;
    vel_dz += (azT + gravity) * dt;
    //Accumulated velocity
    vel_x += axT * dt;
    vel_y += ayT * dt;
    vel_z += (azT + gravity) * dt;
    //Position Change (Zeroed at Every Print)
    pos_dx = vel_x * dt;
    pos_dy = vel_x * dt;
    pos_dz = vel_x * dt;
    //Position Accumulated 
    pos_x += vel_x * dt;
    pos_y += vel_y * dt;
    pos_z += vel_z * dt;
    
    //Print/send updates over com Every Quarter Second
    if (t2 - last_print_time > 300){
      Serial.print((t2-t1)/1000.0); Serial.print(", ");
    
      Serial.print(alpha, 3); Serial.print(", ");
      Serial.print(beta, 3); Serial.print(", ");
      Serial.print(Gamma, 3); Serial.print(", ");
      
      Serial.print(ax, 3); Serial.print(", ");
      Serial.print(ay, 3); Serial.print(", ");
      Serial.print(az, 3); Serial.print(", ");
      
      Serial.print(axT, 3); Serial.print(", ");   
      Serial.print(ayT, 3); Serial.print(", ");
      Serial.print(azT, 3); Serial.print(", ");
      
      Serial.print(vel_x, 3); Serial.print(", ");
      Serial.print(vel_y, 3); Serial.print(", ");
      Serial.print(vel_z, 3); Serial.print(", ");

      Serial.print(pos_x, 3); Serial.print(", ");
      Serial.print(pos_y, 3); Serial.print(", ");
      Serial.print(pos_z, 3); Serial.print(", ");

      Serial.print(pos_dx, 3); Serial.print(", ");
      Serial.print(pos_dy, 3); Serial.print(", ");
      Serial.print(pos_dz, 3); Serial.print(", ");

      last_print_time = t2;
      //Changes after every print accumulated
      pos_dx = 0; pos_dy = 0; pos_dz = 0;
      vel_dx = 0; vel_dy = 0; vel_dz = 0;
    }
    prev_time = t2;
  }
  else{
    delay(1000);
    Serial.println("Press Button to Calibrate...");
  }
}