#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define I2C_SDA 25
#define I2C_SCL 19  
TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;

float a_low = .98; //EMA alpha value where high a = more dependant on current sample
float a_high = .9;

float ay_EMA_low = 0.0;
float ay_EMA_high = 0.0;
float ay_highpass;
float ay_bandpass;

float vely_EMA_low = 0.0;
float vely_EMA_high = 0.0;
float vely_highpass;
float vely_bandpass;

float y_accel = 0.0;
float y_vel = 0.0;
float y_pos = 0.0;

//Low Pass Filter to Smooth Readings of UWB over samples
const int numReadings = 80;
///Anchor 1 Filter
double readings1[numReadings];  // the readings from the analog input
int readIndex1 = 0;          // the index of the current reading
double total1 = 0;              // the running total
double average1_accel = 0;            // the average

float accel_diff = 0;
float vel_diff = 0;

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
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  ay_EMA_high = euler.y();
  ay_EMA_low = euler.y();

  average1_accel = euler.y();

  vely_EMA_low = 0;
  vely_EMA_high = 0;

}

void bandpassfilter(float sensor_val, float EMA_low, float EMA_high, float* EMA_low_address, float* EMA_high_address, float* bandpass, float* highpass){
  EMA_low = (a_low * sensor_val) + ((1 - a_low) * EMA_low);
  EMA_high = (a_high * sensor_val) + ((1 - a_high)* EMA_high);
  
  *highpass = sensor_val - EMA_low;
  *bandpass = EMA_high - EMA_low;

  *EMA_low_address = EMA_low;
  *EMA_high_address = EMA_high;
}


void loop(void) 
{

  float dt = 50/1000.00;
  

  ///Euler Accelerometer
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bandpassfilter(euler.y(), ay_EMA_low, ay_EMA_high, &ay_EMA_low, &ay_EMA_high, &ay_bandpass, &ay_highpass);
  y_vel +=  dt*euler.y();
  y_pos += dt*y_vel;

  bandpassfilter(y_vel, vely_EMA_low, vely_EMA_high, &vely_EMA_low, &vely_EMA_high, &vely_bandpass, &vely_highpass);
  y_pos += 100* vely_highpass*dt;

  // Serial.print("Lowpass:"); Serial.print(y_EMA_low); Serial.print(", ");
  // Serial.print("Highpass:");Serial.print(y_highpass); Serial.print(", ");
  // Serial.print("Bandpass:");Serial.println(y_bandpass);
  // Serial.print("AverageAccel:");Serial.print(average1_accel, 3); Serial.print(", ");
  // Serial.print("upper:");Serial.print(.3); Serial.print(", ");
  // Serial.print("lowerthresh:");Serial.println(-.3);

  // Serial.print("Ayhighpass:");Serial.print(ay_EMA_high); Serial.print(", ");
  Serial.print("Ay:");Serial.print(euler.y()); Serial.print(", ");
  // Serial.print("BandpassAy:");Serial.print(ay_bandpass); Serial.print(", ");
  Serial.print("Vely:");Serial.print(y_vel); Serial.print(", ");
  // Serial.print("BandpassVely:");Serial.print(vely_bandpass, 3); Serial.print(", ");
  Serial.print("Ypos:"); Serial.println(y_pos, 5); 

  //Moving Average Offstt
  total1 = total1 - readings1[readIndex1];
  readings1[readIndex1] = euler.y();
  total1 = total1 + readings1[readIndex1];
  readIndex1 = readIndex1 + 1;
  if (readIndex1 >= numReadings) {
    readIndex1 = 0;
  }
  average1_accel = total1 / numReadings;
  average1_accel = -.144;
  accel_diff =  euler.y() - average1_accel ;
  vel_diff += accel_diff * 1000;
  Serial.print("Average_Accel:");Serial.print(average1_accel); Serial.print(", ");
  Serial.print("Accel_diff:");Serial.print(accel_diff); Serial.print(", ");
  Serial.print("Vel_Diff:");Serial.println(vel_diff);



  delay(50);
}