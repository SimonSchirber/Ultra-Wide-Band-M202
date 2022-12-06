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
#define LED 5

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
float ax_offset = 0, ay_offset = 0, az_offset = 0;
//Acceleration Translated summations
float ax_x = 0, ax_y = 0, ax_z = 0;
float ay_x = 0, ay_y = 0, ay_z = 0;
float az_x = 0, az_y = 0, az_z = 0;
//Translated axis accelerations
float axT = 0, ayT = 0, azT = 0;

void setup(void) {
  Serial.begin(115200);
  pinMode(BUTTON, INPUT);
  pinMode(LED, OUTPUT);
  I2CBNO.begin(I2C_SDA, I2C_SCL, 100000);
  bno = Adafruit_BNO055(55, 0x28, &I2CBNO);
  if(!bno.begin())
  {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  Serial.println("BNO started");
  Serial.println("Spin to calibrate, then press buutton to start");
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
    digitalWrite(LED, HIGH);
    delay(500);
    for (int i=0; i<30; i++) {
      imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
      ax_offset += euler.x();
      ay_offset += euler.y();
      az_offset += euler.z() - gravity;
      euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
      alpha_offset += euler.x();
    } 
    // ax_offset /= 30.0;
    // ay_offset /= 30.0;
    // az_offset /= 30.0;
    alpha_offset /= 30.0;
    ax_offset = -.025;
    ay_offset = -0.15;
    az_offset = -0.84;
    alpha_offset = 269.56; 
    Serial.print(ax_offset); Serial.print(", "); Serial.print(ay_offset); Serial.print(", "); Serial.print(az_offset ); Serial.print(", "); Serial.println(alpha_offset);
    t1 = millis();
  }
  else{
    digitalWrite(LED, LOW);
     
  }
  if (calib){
    //Time since last call
    long int t2 = millis();
    float dt = (t2 - prev_time)/1000.00;
    //Euler Oreintation
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    alpha = euler.x() - alpha_offset;
    alphaT = euler.x() - alpha_offset;
    if (alpha < 0){
      alpha += 360;}
    //alpha = alpha_offset;
    beta = euler.y();
    Gamma = euler.z();
    ///Euler Accelerometer
    euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax = euler.x() - ax_offset;
    ay = euler.y() - ay_offset;
    az = -(euler.z() - az_offset);
    //Do translation accel calculations
    TranslateAccel();
    
    //Print/send updates over com Every Quarter Second
    if (t2 - last_print_time > 10000){
      digitalWrite(LED, HIGH);
      delay(5000);
      digitalWrite(LED, LOW);

      Serial.print((t2-t1)/1000.0); Serial.print(", ");
    
      Serial.print(alpha, 3); Serial.print(", ");
      Serial.print(beta, 3); Serial.print(", ");
      Serial.print(Gamma, 3); Serial.print(", ");
      
      Serial.print(ax, 3); Serial.print(", ");
      Serial.print(ay, 3); Serial.print(", ");
      Serial.print(az, 3); Serial.print(", ");
      
      Serial.print(axT, 3); Serial.print(", ");   
      Serial.print(ayT, 3); Serial.print(", ");
      Serial.println(azT, 3);

      last_print_time = t2;
    }
    prev_time = t2;
  }
  else{
    Serial.println("Spin to calibrate, then press buutton to start");
    delay(500);
  }
  
}
