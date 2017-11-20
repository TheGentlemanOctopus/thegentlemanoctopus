import serial
import time
from collections import deque
import numpy as np 
from detect_peaks import detect_peaks

# There are 7 FFT channels being read from the MSGEQ7
numFFTChan = 7
# Length of the buffer for each FFT channel, Buffer is used for peak detection
BufLength = 200
# Serial port of Arduino
ser = serial.Serial('/dev/tty.usbmodemFD121', 115200)

# Create a list of rolling buffers for the FFT data.
EQData = []
for row in range(0,numFFTChan):
    # Each FFT channel has a rolling deque that will be used for peak detection
    EQData.append(deque([0 for i in range(BufLength)], maxlen = BufLength))
    
# Start main loop
while True:
    try:
        # Clear serial buffer
        ser.flushInput()
        # Dummy read to get rid of crap data
        FFTData = ser.readline()
        # Read read, strip off the carriage return
        FFTData = ser.readline().strip('\r\n')
        # Parse the data csv style
        parsedData = FFTData.split(",", numFFTChan)

        # Add the latest data from the FFT to their respective buffers
        EQi = 0
        for r in parsedData:
            EQData[EQi].appendleft(int(r))
            EQi += 1
        # LEDData is a byte used for indicating if there was a 
        # peak found this loop iteration. Starts as 0.


        FFTPeaks = []
        for row in range(0,numFFTChan):
            FFTPeaks.append([0,0])

        LEDData = 0
        FFTIndex = 0   
        for FFTBuffer in EQData:
            # Auto thresholding for the peaks
            FFTThreshold = np.mean(FFTBuffer) + 200
            if FFTThreshold > 700:
                FFTThreshold = 700

            #print FFTThreshold

            indexes = detect_peaks(FFTBuffer, mph = FFTThreshold, mpd = (BufLength / 2))
            #print ("the index is %d", FFTIndex)
            
            if len(indexes > 0):
                #print indexes
                if indexes[0] == 1: 
                    FFTPeaks[FFTIndex][0] = 1
                    FFTPeaks[FFTIndex][1] = FFTBuffer[indexes[0]]


                    LEDData = LEDData ^ 0x01

            FFTIndex += 1

            if FFTIndex < len(EQData):    
                LEDData = LEDData << 1

        #print FFTPeaks

        
            
                
            

            

        #print LEDData
        #print hex(LEDData)
        
        #send to the Arduino for protptyping display
        ser.write(chr(LEDData))                         

        time.sleep(0.00001)
    except KeyboardInterrupt:
        ser.close()
        pass
