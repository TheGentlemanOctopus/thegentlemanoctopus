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
    Serial.write("I read:");
    Serial.write(incomingByte);
    
    switch (incomingByte) {
    case 'a': 
      statusA = !statusA;   
      digitalWrite(2, statusA);
      Serial.write(statusA);
      break;
    case 'b': 
      statusB = !statusB;   
      digitalWrite(3, statusB);
      break;
    case 'c':  
      statusC = !statusC;  
      digitalWrite(4, statusC);
      break;
    case 'd':  
      statusD = !statusD; 
      digitalWrite(5, statusD);
      break;
    case 'e': 
      statusE = !statusE;  
      digitalWrite(6, statusE);
      break;
    case 'f':   
      statusF = !statusF; 
      digitalWrite(7, statusF);
      break;
    case 'g':   
      statusG = !statusG; 
      digitalWrite(8, statusG);
      break;
    case 'h':  
      statusH = !statusH;  
      digitalWrite(9, statusH);
      break;
    default:
      break;
    }

  }  

}

