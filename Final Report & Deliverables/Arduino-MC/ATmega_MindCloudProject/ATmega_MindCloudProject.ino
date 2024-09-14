#include <Keypad.h>

#define BUZZ 12
#define LED 13
#define motionPin A5
#define servoPin 10
#define LDRPin A0
#define TempPin A1
  
#define LED_R A2
#define LED_G A4
#define LED_B A3

#define EN 11
bool doorOpen=0;
bool sysUnlock=0;
  
void setup(){
  
  pinMode(BUZZ, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(motionPin, INPUT);
  pinMode(servoPin, OUTPUT);
  pinMode(LDRPin, INPUT);
  
  pinMode(LED_R, OUTPUT);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_B, OUTPUT);

  pinMode(EN, OUTPUT);
  
  Serial.begin(9600);
}

//Door/

void openDoor(int start=0){
  for (int i=start; i<=200; i++){ //turn the servo motor
    analogWrite(servoPin, i);
    delay(10);
  }  
}

void closeDoor(int end=200){
  for (int i=end; i>=0; i--){ //turn the servo motor
    //if (digitalRead(motionPin) == HIGH) return i; //if the door needs to open while it's closing, return with the value to start at opening
    analogWrite(servoPin, i);
    delay(10);
  }
  
  //return 60;
}


//KEYPAD Initials//
const byte ROWS = 4;
const byte COLS = 4;
char keys[ROWS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

//byte rowPins[ROWS] = {2, 3, 4, 5}; //connect to the row pinouts of the keypad
//byte colPins[COLS] = {6, 7, 8, 9}; //connect to the column pinouts of the keypad

byte rowPins[ROWS] = {9, 8, 7, 6}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {5, 4, 3, 2}; //connect to the column pinouts of the keypad

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );
int PW_Len = 6;
const int maxPW_Len = 32;
char Data[maxPW_Len]; //The incoming input password
char Master[maxPW_Len] = "123A45"; //The already set password
byte data_count = 0;
//bool CorrectPW;
//bool ChangePW;
////

//LDR//

void ldr(){

  const int threshold = 500;
  int sensor = analogRead(LDRPin);
  if(sensor<threshold){ //low light
    digitalWrite(LED,HIGH);  //turn LED on
  }  
  else{
    digitalWrite(LED,LOW);  //turn LED off
  }
}

//TEMP//
//NOTE: The temp doesn't work because tinkercad doesn't have NTC sensors.
// The code below is for NTC Sensor (replace 500 with the comment line)

float temp;

void tempSense(){
  
  float v_ntc = 5.0/1023 * analogRead(TempPin); //* 500;//
  float current = (5.0-v_ntc)/10000.0;
  float r_ntc = v_ntc/current;
  temp = 1 / ( log(r_ntc/10000.0)/3950 + 1/(25.0+273.15)  ) -273.15;
  //temp=80;
  Serial.print("Temp: ");
  Serial.print(temp);
  Serial.print("\n");
  //delay(1500);
  
  
}

//RGB Light//

void setLED(char c){
  
  if (c=='G') digitalWrite(LED_G, HIGH); 
  else digitalWrite(LED_G, LOW);
  if (c=='B') digitalWrite(LED_B, HIGH); 
  else digitalWrite(LED_B, LOW);
  if (c=='R') digitalWrite(LED_R, HIGH); 
  else digitalWrite(LED_R, LOW);

}

void RGB(float temp1){
  if (temp1<20){
  	setLED('B');
  }
  else if (temp1>=20 && temp1<=30){
  	setLED('G');
  }
  else {
  	setLED('R');
  }

}

//Motor Fan//

void motor(float temp1){
  
  //DC Motor R280 3-12V 13750RPM
  //analogWrite(EN, 255);
   
  if (temp1<20){
  	analogWrite(EN, 0);
  }
  else if (temp1>=20 && temp1<=30){
    int RMPtoAnalog = (temp*100/13750.0)*255;
  	analogWrite(EN, RMPtoAnalog);
  }
  else {
    int RMPtoAnalog = (3500/13750.0)*255;
  	analogWrite(EN, RMPtoAnalog);
  }
}

//System Functions//
void openCloseDoor(){
  startSys();
      
  sysUnlock=1;
  doorOpen=1;
  openDoor();
  delay(7000);
  closeDoor();
  doorOpen=0;
}

void startSys(){
  ldr();
  tempSense();
  RGB(temp);
  motor(temp);
}

//KEYPAD//
void kp(){
  
  delay(70);
  char key = keypad.getKey();
  
  if (key){
    Serial.print(key);
  	Serial.print("\n");
    Data[data_count]=key;
    data_count++;
  } 
  
  if (data_count==PW_Len){
  
    if(!strcmp(Data, Master)){
      Serial.print("Correct Password\n");
      Serial.print("Opening Door\n");
      openCloseDoor();
      
      delay(1000);
      }
    else{
      //
      //SEND To Control Interface Too//
      //
      Serial.print("Incorrect Password\n");
      tone(BUZZ, 300, 500);
      
      delay(1000);
      }
  
  	//Clearing the data array
    data_count=0;
    for (int i=0; i<PW_Len; i++){
      Data[i]=0;
    }
  }
  

}


//Control Interface//

void ctrl(){

  if (Serial.available() > 0) {
    char msg[32] = "";
    int len = Serial.readBytes(msg, sizeof(msg) - 1); //msg buffer
    msg[len] = '\0'; 

    if (strcmp(msg, "open") == 0 && !doorOpen) {
      Serial.print("Opening Door\n");
      openCloseDoor();
      
    } 
    else if (strcmp(msg, "change") == 0) {
        delay(5000);
        if (Serial.available() > 0) {
            len = Serial.readBytes(msg, sizeof(msg) - 1); 
            msg[len] = '\0'; 
            
            if (strlen(msg) <30) {
              strcpy(Master, msg); //Copy new password to Master
              PW_Len = strlen(msg);  
              Serial.print("Password Changed!\n");
            }
          else {
            Serial.print("Password Too Long!\n");
          }
        }
    }

    else if (strcmp(msg, "lock")==0) {
      sysUnlock=0;
      digitalWrite(LED,LOW);
      analogWrite(EN, 0);
      setLED('0');
      Serial.print("System Locked!\n");
    }
  
  }
  
}


//LOOP//

void loop(){
  //sysUnlock=1;
  
  //KEYPAD//
  if (!doorOpen) kp();
  
  //Control Interface//
  ctrl();
  //Serial.write(Master);
  //Serial.write("\n");
  //delay(1000);
  
  //PIR//
  if (!sysUnlock){
  	byte motionStatus = digitalRead(motionPin);
    if (motionStatus){
      	//
      	//SEND To Control Interface Too//
      	//
    	Serial.print("WARNING: Intruder\n");		
    }
  }
  
  //Starting The System Functions//
  if (sysUnlock){
    
    startSys();
  
  }
}
