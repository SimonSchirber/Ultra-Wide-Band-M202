#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include "dw3000.h"
#define APP_NAME "SS TWR INIT v1.0"

///////////////DW3000: IO 18 not avaiable on DW3000, potential IO = 5 = LED, 35 = BUTTON CALIB, 26
///GPIO for flash 6,7,8,9,10,11/16,17 GPIO UWB = 4, 34, 27, other used  0, 2, 4, 12-15, 18, 19, 23, 27, 32, 33, 34,
//not working 26,5  being used (36, 39 not avaialble)
//BUTTON_CALIB 1
#define BUTTON_CALIB 35
int calib_but_val = 0;

//LED
#define LED 5
//IMU Sensor
#define I2C_SDA 25
#define I2C_SCL 19
TwoWire I2CBNO = TwoWire(0);
Adafruit_BNO055 bno;
//UWB SPI PINS
const uint8_t PIN_RST = 27; // reset pin
const uint8_t PIN_IRQ = 34; // irq pin
const uint8_t PIN_SS = 4; // spi select pin

////////////////IMU Measurements///////////
bool calib = false;
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


////////////////UWB Anchors (Responders) Declarations///////////////
//Anchor to Read
int anchor_num = 1;
//Low Pass Filter to Smooth Readings of UWB over samples
const int numReadings = 9;
///Anchor 1 Filter
double readings1[numReadings];  // the readings from the analog input
int readIndex1 = 0;          // the index of the current reading
double total1 = 0;              // the running total
double average1_dis = 0;            // the average
//Anchor 2 Filter
double readings2[numReadings];  // the readings from the analog input
int readIndex2 = 0;          // the index of the current reading
double total2 = 0;              // the running total
double average2_dis = 0;            // the average 

/* Default communication configuration. We use default non-STS DW mode. */
static dwt_config_t config = {
  5,               /* Channel number. */
  DWT_PLEN_128,    /* Preamble length. Used in TX only. */
  DWT_PAC8,        /* Preamble acquisition chunk size. Used in RX only. */
  9,               /* TX preamble code. Used in TX only. */
  9,               /* RX preamble code. Used in RX only. */
  1,               /* 0 to use standard 8 symbol SFD, 1 to use non-standard 8 symbol, 2 for non-standard 16 symbol SFD and 3 for 4z 8 symbol SDF type */
  DWT_BR_6M8,      /* Data rate. */
  DWT_PHRMODE_STD, /* PHY header mode. */
  DWT_PHRRATE_STD, /* PHY header rate. */
  (129 + 8 - 8),   /* SFD timeout (preamble length + 1 + SFD length - PAC size). Used in RX only. */
  DWT_STS_MODE_OFF, /* STS disabled */
  DWT_STS_LEN_64,/* STS length see allowed values in Enum dwt_sts_lengths_e */
  DWT_PDOA_M0      /* PDOA mode off */
};

/* Inter-ranging delay period, in milliseconds. */
#define RNG_DELAY_MS 50

/* Default antenna delay values for 64 MHz PRF. See NOTE 2 below. */
#define TX_ANT_DLY 16400
#define RX_ANT_DLY 16400

///Anchor 1 Frames See note 3 (Where Anchor Addresses Declared)
static uint8_t tx_poll_msg1[] = {0x41, 0x88, 0, 0xCA, 0xDE, 'S', 'I', 'J', 'A', 0xE0, 0, 0};
static uint8_t rx_resp_msg1[] = {0x41, 0x88, 0, 0xCA, 0xDE, 'J', 'A', 'S', 'I', 0xE1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

///Anchor 2 Frame See note 3 (Where Anchor Addresses Declared)
static uint8_t tx_poll_msg2[] = {0x41, 0x88, 0, 0xCA, 0xDE, 'W', 'A', 'V', 'E', 0xE0, 0, 0};
static uint8_t rx_resp_msg2[] = {0x41, 0x88, 0, 0xCA, 0xDE, 'V', 'E', 'W', 'A', 0xE1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

/* Length of the common part of the message (up to and including the function code, see NOTE 3 below). */
#define ALL_MSG_COMMON_LEN 10
/* Indexes to access some of the fields in the frames defined above. */
#define ALL_MSG_SN_IDX 2
#define RESP_MSG_POLL_RX_TS_IDX 10
#define RESP_MSG_RESP_TX_TS_IDX 14
#define RESP_MSG_TS_LEN 4
/* Frame sequence number, incremented after each transmission. */
static uint8_t frame_seq_nb = 0;
/* Buffer to store received response message. Its size is adjusted to longest frame that this example code is supposed to handle. */
#define RX_BUF_LEN 20
static uint8_t rx_buffer[RX_BUF_LEN];
/* Hold copy of status register state here for reference so that it can be examined at a debug breakpoint. */
static uint32_t status_reg = 0;
#define POLL_TX_TO_RESP_RX_DLY_UUS 240
#define RESP_RX_TIMEOUT_UUS 400

/* Hold copies of computed time of flight and distance here for reference so that it can be examined at a debug breakpoint. */
static double tof;
static double distance;

/* Values for the PG_DELAY and TX_POWER registers reflect the bandwidth and power of the spectrum at the current
 * temperature. These values can be calibrated prior to taking reference measurements. See NOTE 2 below. */
extern dwt_txconfig_t txconfig_options;
//To Change the tx_power and range, go to the DW300 library and change the tx_power register

void setup(void) {
  //Start Serial
  UART_init();

  //////Initialize UWB DWM300///////
  test_run_info((unsigned char *)APP_NAME);
  spiBegin(PIN_IRQ, PIN_RST);
  spiSelect(PIN_SS);
  delay(2); 
  // Need to make sure DW IC is in IDLE_RC before proceeding 
  while (!dwt_checkidlerc()){
    UART_puts("IDLE FAILED\r\n");
    while (1);
  }
  if (dwt_initialise(DWT_DW_INIT) == DWT_ERROR){
    UART_puts("INIT FAILED: Error\r\n");
    while (1);
  }
  //Enabling LEDs here for debug so that for each TX the D1 LED will flash on DW3000 red eval-shield boards.
  dwt_setleds(DWT_LEDS_ENABLE | DWT_LEDS_INIT_BLINK);
  // Configure DW IC. // if the dwt_configure returns DWT_ERROR either the PLL or RX calibration has failed the host should reset the device. See NOTE 6 below.
  if(dwt_configure(&config)) {
    UART_puts("CONFIG FAILED\r\n");
    while (1) ;
  }
  /* Configure the TX spectrum parameters (power, PG delay and PG count) */
  dwt_configuretxrf(&txconfig_options);
  /* Apply default antenna delay value. See NOTE 2 below. */
  dwt_setrxantennadelay(RX_ANT_DLY);
  dwt_settxantennadelay(TX_ANT_DLY);

  /* Set expected response's delay and timeout. See NOTE 1 and 5 below. As this example only handles one incoming frame with always the same delay and timeout, those values can be set here once for all. */
  dwt_setrxaftertxdelay(POLL_TX_TO_RESP_RX_DLY_UUS);
  dwt_setrxtimeout(RESP_RX_TIMEOUT_UUS);

  /* Next can enable TX/RX states output on GPIOs 5 and 6 to help debug, and also TX/RX LEDs* Note, in real low power applications the LEDs should not be used. */
  dwt_setlnapamode(DWT_LNA_ENABLE | DWT_PA_ENABLE);
  
  //Declare Pins, Caution these initializations need to be after UWB initializations or the UWB will fail
  pinMode(BUTTON_CALIB, INPUT);
  pinMode(LED, OUTPUT);
  
  //Initialize IMU, Caution these initializations need to be after UWB initializations or the UWB will fail
  Serial.println("Orientation Sensor Test"); 
  I2CBNO.begin(I2C_SDA, I2C_SCL, 100000);
  bno = Adafruit_BNO055(55, 0x28, &I2CBNO);
  if(!bno.begin()){
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }
  bno.setExtCrystalUse(true);
  delay(1000);
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

void Sample_IMU(){
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
    if (t2 - last_print_time > .250){
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
      
      // Serial.print(vel_x, 3); Serial.print(", ");
      // Serial.print(vel_y, 3); Serial.print(", ");
      // Serial.print(vel_z, 3); Serial.print(", ");

      // Serial.print(pos_x, 3); Serial.print(", ");
      // Serial.print(pos_y, 3); Serial.print(", ");
      // Serial.print(pos_z, 3); Serial.print(", ");

      // Serial.print(pos_dx, 3); Serial.print(", ");
      // Serial.print(pos_dy, 3); Serial.print(", ");
      // Serial.print(pos_dz, 3); Serial.print(", ");

      last_print_time = t2;
      //Changes after every print accumulated
      pos_dx = 0; pos_dy = 0; pos_dz = 0;
      vel_dx = 0; vel_dy = 0; vel_dz = 0;
    }
    prev_time = t2;
}

void loop(){
  calib_but_val = digitalRead(BUTTON_CALIB);
  //Calibrate IMU
  if (calib_but_val == 1){
    digitalWrite(LED, HIGH);
    Serial.println("Calibrating");
    calib = true;
    delay(500);
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    ax_offset = euler.x();
    ay_offset = euler.y();
    az_offset = euler.z() - gravity;
    Serial.println("Offsets (ax ay az): ");
    Serial.print(ax_offset); Serial.print(", "); Serial.print(ay_offset); Serial.print(", "); Serial.print(az_offset ); Serial.print(", ");
    euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    alpha_offset = euler.x(); 
    Serial.println(alpha_offset);
    vel_x = 0; vel_y = 0; vel_z = 0;
    pos_x = 0; pos_y = 0; pos_z = 0;
    t1 = millis();
  }
  else{
    digitalWrite(LED, LOW);
  }

  //////////Check if IMU data is Calibrated, if so stream data////////////////
  if (calib){
    Sample_IMU();
  }
  else{
    Serial.println("Press BUTTON_CALIB to Calibrate...");
  }

  //////////Transmit UWB Data///////////////
  if (anchor_num == 1){
    tx_poll_msg1[ALL_MSG_SN_IDX] = frame_seq_nb;
    dwt_write32bitreg(SYS_STATUS_ID, SYS_STATUS_TXFRS_BIT_MASK);
    dwt_writetxdata(sizeof(tx_poll_msg1), tx_poll_msg1, 0); /* Zero offset in TX buffer. */
    dwt_writetxfctrl(sizeof(tx_poll_msg1), 0, 1); /* Zero offset in TX buffer, ranging. */
    anchor_num = 2;
  }
  else if (anchor_num == 2){
    tx_poll_msg2[ALL_MSG_SN_IDX] = frame_seq_nb;
    dwt_write32bitreg(SYS_STATUS_ID, SYS_STATUS_TXFRS_BIT_MASK);
    dwt_writetxdata(sizeof(tx_poll_msg2), tx_poll_msg2, 0); /* Zero offset in TX buffer. */
    dwt_writetxfctrl(sizeof(tx_poll_msg2), 0, 1); /* Zero offset in TX buffer, ranging. */
    anchor_num = 1;
  }

  /* Start transmission, indicating that a response is expected so that reception is enabled automatically after the frame is sent and the delay
    * set by dwt_setrxaftertxdelay() has elapsed. */
  dwt_starttx(DWT_START_TX_IMMEDIATE | DWT_RESPONSE_EXPECTED);

  /* We assume that the transmission is achieved correctly, poll for reception of a frame or error/timeout. See NOTE 8 below. */
  while (!((status_reg = dwt_read32bitreg(SYS_STATUS_ID)) & (SYS_STATUS_RXFCG_BIT_MASK | SYS_STATUS_ALL_RX_TO | SYS_STATUS_ALL_RX_ERR))){ };
  
  /* Increment frame sequence number after transmission of the poll message (modulo 256). */
  frame_seq_nb++;
  
  if (status_reg & SYS_STATUS_RXFCG_BIT_MASK) {
    uint32_t frame_len;
    /* Clear good RX frame event in the DW IC status register. */
    dwt_write32bitreg(SYS_STATUS_ID, SYS_STATUS_RXFCG_BIT_MASK);
    /* A frame has been received, read it into the local buffer. */
    frame_len = dwt_read32bitreg(RX_FINFO_ID) & RXFLEN_MASK;
    if (frame_len <= sizeof(rx_buffer)){
      dwt_readrxdata(rx_buffer, frame_len, 0);
      /* Check that the frame is the expected response from the companion "SS TWR responder" example.
        * As the sequence number field of the frame is not relevant, it is cleared to simplify the validation of the frame. */
      rx_buffer[ALL_MSG_SN_IDX] = 0;
      if ((memcmp(rx_buffer, rx_resp_msg1, ALL_MSG_COMMON_LEN) == 0) || (memcmp(rx_buffer, rx_resp_msg2, ALL_MSG_COMMON_LEN) == 0)){
        uint32_t poll_tx_ts, resp_rx_ts, poll_rx_ts, resp_tx_ts;
        int32_t rtd_init, rtd_resp;
        float clockOffsetRatio ;

        /* Retrieve poll transmission and response reception timestamps. See NOTE 9 below. */
        poll_tx_ts = dwt_readtxtimestamplo32();
        resp_rx_ts = dwt_readrxtimestamplo32();

        /* Read carrier integrator value and calculate clock offset ratio. See NOTE 11 below. */
        clockOffsetRatio = ((float)dwt_readclockoffset()) / (uint32_t)(1<<26);

        /* Get timestamps embedded in response message. */
        resp_msg_get_ts(&rx_buffer[RESP_MSG_POLL_RX_TS_IDX], &poll_rx_ts);
        resp_msg_get_ts(&rx_buffer[RESP_MSG_RESP_TX_TS_IDX], &resp_tx_ts);

        /* Compute time of flight and distance, using clock offset ratio to correct for differing local and remote clock rates */
        rtd_init = resp_rx_ts - poll_tx_ts;
        rtd_resp = resp_tx_ts - poll_rx_ts;

        tof = ((rtd_init - rtd_resp * (1 - clockOffsetRatio)) / 2.0) * DWT_TIME_UNITS;
        distance = tof * SPEED_OF_LIGHT;
        //Convert to inches
        distance = distance * 39.37;

        if (anchor_num == 1){
          total1 = total1 - readings1[readIndex1];
          readings1[readIndex1] = distance;
          total1 = total1 + readings1[readIndex1];
          readIndex1 = readIndex1 + 1;
          if (readIndex1 >= numReadings) {
            readIndex1 = 0;
          }
          average1_dis = total1 / numReadings;
          distance =  average1_dis; 
          // Serial.print("Anchor ");
          // Serial.print(anchor_num);
          // Serial.print(" Distance: ");
          // Serial.print(distance);             
        }
        else if (anchor_num == 2){
          total2 = total2 - readings2[readIndex2];
          readings2[readIndex2] = distance;
          total2 = total2 + readings2[readIndex2];
          readIndex2 = readIndex2 + 1;
          if (readIndex2 >= numReadings) {
            readIndex2 = 0;
          }
          average2_dis = total2 / numReadings;
          distance =  average2_dis; 
          // Serial.print("Anchor ");
          // Serial.print(anchor_num);
          // Serial.print(" Distance: ");
          // Serial.print(distance);        
        }
        Serial.print(average1_dis);
        Serial.print(", ");
        Serial.print(average2_dis);
        test_run_info((unsigned char *)dist_str);
      }
    }
  }
  else{
    dwt_write32bitreg(SYS_STATUS_ID, SYS_STATUS_ALL_RX_TO | SYS_STATUS_ALL_RX_ERR);
  }
  Sleep(RNG_DELAY_MS);
}
