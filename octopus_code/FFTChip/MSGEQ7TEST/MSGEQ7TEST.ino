
/*
 * Board:   ChipKIT Max32
 * Target:  BADASS Display
 * File:    badass_v1_01.ino
 * Version: 1.01
 * Author:  Clive "Max" Maxfield (max@clivemaxfield.com) 
 * Modified By: Ben Holden (benholden7@gmail.com)
 * License: The MIT License (See full license at the bottom of this file)
 *
 * Notes:   Cheap-and-cheerful spectrum analyzer using MSGEQ7 chips
 *          V1.01 First experiments with the MSGEQ7s (read from chips, use serial display)
 */

// MSGEQ7 bands = 63Hz, 160Hz, 400Hz, 1,000Hz, 2,500Hz, 6,250Hz, 16,000Hz



#include <SPI.h>         // needed for Arduino versions later than 0018
#include <Ethernet.h>
#include <EthernetUdp.h>         // UDP library from: bjoern@cs.stanford.edu 12/30/2008

#include <Adafruit_NeoPixel.h>

#define NEOPIXEL_PIN 6
#define NUM_NEOPIXELS 7
#define PIX_BRIGHTNESS 255

#define INCOMINGPORT 5003 // local port to listen on
#define DATAPORT 5009  // Local port to send the data over

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUM_NEOPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);


// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0xDE, 0xAD, 0xBE, 0xEF, 0x12, 0x34
};
// IP address of arduino 
IPAddress ip(192, 168, 1, 177);

//variable for ip of master
IPAddress masterIP;

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE];  //buffer to hold incoming packet,
char  ReplyBuffer[] = "acknowledged";       // a string to send back

//Connection variable
bool Connection = false;

// An EthernetUDP instance to let us send and receive packets over UDP
EthernetUDP Udp;

int ctrlReset    = 9;                   // Digital pin 23 = signal to reset MSGEQ7s
int ctrlStrobe   = 8;                   // Digital pin 22 = signal to strobe (read data from) MSGEQ7s
int channelLeft  =  0;                   // Analog pin 0 = spectrum data from left channel
//int channelRight =  1;                   // Analog pin 1 = spectrum data from right channel

int spectrumLeft[7];                     // Array to store 7 bands of spectrum data from left channel 
int spectrumLeftMap[7];                     // Array to store 7 bands of spectrum data from left channel mapped
int bufferLength = 0;

char UDPBuffer[100];

int LEDOutput = 0x00;
//int spectrumRight[7];                    // Array to store 7 bands of spectrum data from right channel
int LEDIntensity[7] = {0,0,0,0,0,0,0};

void setup()
{

  // start the Ethernet and UDP:
  Ethernet.begin(mac, ip);
  // Start a udp on the incoming port to listen for messages from main board
  Udp.begin(INCOMINGPORT);
  
  //begin serial
  Serial.begin(9600);
  pinMode(ctrlReset,OUTPUT);             // Define reset as output
  pinMode(ctrlStrobe,OUTPUT);            // Define strobe as output
  digitalWrite(ctrlReset,LOW);           // Pull the reset signal low
  digitalWrite(ctrlStrobe,HIGH);         // Drive the strobe signal high
  pixels.begin();                       //init neopixel library
}


void loop()
{
  int ethernetStatus = Ethernet.maintain();
  Serial.println(ethernetStatus);
  //Waits for connection and initial start signal from main board
  if(Connection == false)
  { 
    readUDP();
  } else {
    
    readMSGEQ7();

    bufferLength = 0;
    // Display values from the left channel into the buffer
    for (int i = 0; i < 7; i++)
    { 
      if (i < 6)
      {
        bufferLength += sprintf(UDPBuffer + bufferLength, "%d,", spectrumLeft[i]);
      } else {
        bufferLength += sprintf(UDPBuffer + bufferLength, "%d", spectrumLeft[i]);
      }
    }

    //print into serial
    Serial.print(UDPBuffer);
    // write to the remote ip that sent the start signal on the data port
    // todo make this work 
    //Checks for connection success. if fails then the connection has dropped so wait for start on incoming port
    
    Udp.beginPacket(masterIP, DATAPORT);
    Udp.write(UDPBuffer);
    if(Udp.endPacket() == 1)
    { 
      Serial.print("ConnectionGood");
    } else {
      
      Serial.print("ConnectionFucked");
      Connection = false;
    }
    
    Serial.println("");   
     
 // Neopixel stuff commented out because not needed
 /*   
    if (Serial.available() > 0) 
    {
        LEDOutput = Serial.read();   
  
        for (int a = 0; a<7; a++)
        {
                  
          if (LEDOutput & 0x01)
          {
            LEDIntensity[a] = 128;
            //pixels.setPixelColor(a, pixels.Color(0,0,128));
          } else {
            if (LEDIntensity[a] > 0)
            {
              LEDIntensity[a] = 0;
              //LEDIntensity[a] -= 8;
            }
            //pixels.setPixelColor(a, pixels.Color(0,0,0));
          }
          pixels.setPixelColor(a, pixels.Color(0,0,LEDIntensity[a]));
          LEDOutput = LEDOutput >> 1;
        }
    }
    
    pixels.show();

    */
    delay(100);
    //delayMicroseconds(1000); 
  }
  
}


void readUDP()
{
    int packetSize = Udp.parsePacket();
    if (packetSize)
    {
      masterIP = Udp.remoteIP();
      // read the packet into packetBufffer
      Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
      //packetBuffer.trim()
      Serial.println(packetBuffer);
      if(strcmp(packetBuffer, "Start") == 0)
      {
        Connection = true;
        Serial.println("Connection made");
      } else if(strcmp(packetBuffer, "Stop") == 0)
      {
        Connection = false;
      }
    }
}

void readMSGEQ7()
// Read the seven spectrum bands from the MSGEQ7 chips
{
  digitalWrite(ctrlReset, HIGH);                     // Pulse the reset signal, which causes
  digitalWrite(ctrlReset, LOW);                      // the MSGEQ7s to latch the spectrum values
  delayMicroseconds(75);                             // Delay to meet minimum reset-to-strobe time

  for(int i=0; i <7; i++)                            // Cycle through the 7 spectrum bands
  {
    digitalWrite(ctrlStrobe,LOW);                    // Read current band (then increment to next band)
    delayMicroseconds(40);                           // Wait for outputs to settle

    spectrumLeft[i] = analogRead(channelLeft);   // Store current values from left & right channels 



    
    //spectrumRight[i] = analogRead(channelRight) / 4; // Divide 0-1023 by 4 to give 0-255

    digitalWrite(ctrlStrobe,HIGH);
    delayMicroseconds(40);                           // Delay to meet minimum strobe-to-strobe time
  }
}


/*
 * Copyright (c) 2014 Clive "Max" Maxfield
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHOR(S) OR COPYRIGHT HOLDER(S) BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
