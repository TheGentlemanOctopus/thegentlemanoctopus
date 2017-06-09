// Test sketch for El Escudo Dos
// Turn each EL channel (A-H) on in sequence and repeat
// Mike Grusin, SparkFun Electronics
boolean del = 100;
boolean statusA = false;
boolean statusB = false;
boolean statusC = false;
boolean statusD = false;
boolean statusE = false;
boolean statusF = false;
boolean statusG = false;
boolean statusH = false;

void setup() {        
  Serial.begin(57600);  
  // The EL channels are on pins 2 through 9
  // Initialize the pins as outputs
  pinMode(2, OUTPUT);  // channel A  
  pinMode(3, OUTPUT);  // channel B   
  pinMode(4, OUTPUT);  // channel C
  pinMode(5, OUTPUT);  // channel D    
  pinMode(6, OUTPUT);  // channel E
  pinMode(7, OUTPUT);  // channel F
  pinMode(8, OUTPUT);  // channel G
  pinMode(9, OUTPUT);  // channel H
  // We also have two status LEDs, pin 10 on the Escudo, 
  // and pin 13 on the Arduino itself
  pinMode(10, OUTPUT);     
  pinMode(13, OUTPUT);   
  
  int x;
  for (x=2; x<=9; x++)
  {
    digitalWrite(x, false);    // turn the EL channel off
  }
}

void loop() 
{
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    int incomingByte = Serial.read();
    
    switch (incomingByte) {
    case 'A': 
      digitalWrite(2, true);
      break;
    case 'a': 
      digitalWrite(2, false);
      break;
    case 'B': 
      digitalWrite(3, true);
      break;
    case 'b': 
      digitalWrite(3, false);
      break;
    case 'C':  
      digitalWrite(4, true);
      break;
    case 'c':  
      digitalWrite(4, false);
      break;
    case 'D':  
      digitalWrite(5, true);
      break;
    case 'd':  
      digitalWrite(5, false);
      break;      
    case 'E':  
      digitalWrite(6, true);
      break;
    case 'e': 
      digitalWrite(6, false);
      break;
    case 'F': 
      digitalWrite(7, false);
      break;
    case 'f': 
      digitalWrite(7, false);
      break;
    case 'G': 
      digitalWrite(8, false);
      break;
    case 'g': 
      digitalWrite(8, false);
      break;
    default:
      break;
    }

  }  

}

