# -*- coding: utf-8 -*-
# Performs ETS of the PRS swept from a delaytime of +.2 us to -.6 us
# Configuration as follows:
# Sync Plugin: AbsPhase:
#       PPS: Slot 7, PFI0
#       PRS: Slot 7, PFI1
# FGen Plugin: AbsPhase_Voltage_Direct:
#       Test Function .ini file: AbsPhase_Voltage_10V_Direct
#       SampleRate: 50000
# Digitizer Plugin:
#       Sample Rate 100000 (may be changed)
#       Record Size (same as sample rate)
#       NumRecords 1
# Sensor Plugin:
#       C37.118 PMU (this may not matter at all but "none is throwing a error right now)
#
# Analysis Plugin: AbsPhase_10s (SaveWaveforms class)
#       Duration: 1




from lta import Lta
import sys
from lta_err import Lta_Error
import time
#import math

#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object
try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------
    UsrTimeout = lta.s.gettimeout()

    # index offsets to function params
    amplitude = 0
    dcOffset = 1
    dutyCycle = 2
    frequency = 3
    phase = 4
    waveform = 5


    freq_list = [5000, 2500, 1000, 500, 200, 100, 50, 40] 
#    freq_list = [5000, 2500, 1000, 500, 200, 100, 40]
#    freq_list = [200, 180, 160, 140, 120, 100, 80, 70, 60, 50, 40] 
#    freq_list = [200, 160, 100, 80, 50, 40] 
#    freq_list = [1000]

    for freq in freq_list:    
        dlyTime = .6    # microseconds
        #dlyTime =  -.05   # microseconds
        
        while (dlyTime > -1):
              
#            sleepTime = 5
#            while (sleepTime > 0):
#                print sleepTime            
#                time.sleep(1)
#                sleepTime = sleepTime-1
            

            
            print 'freq:',freq,'hz' ,'delay:',dlyTime,'us'
            
            time.sleep(2.5) 
            
            
            ClkProperties=lta.__get__('Sync.ClockProperties')
            for element in ClkProperties[None]:
 
               # For Equivalent Time Sampling, move the digitizer trigger
                if element['clClocks']['Name'] == "PRS":
                    element['clClocks']['Delay'] = float(dlyTime)          #Set initial Pgm_Pps delay time
 
                 # set the PRS frequency:
                if element['clClocks']['Name'] == 'PRS':
                    element['clClocks']['Frequency'] = float(freq)
    
            lta.__set__('Sync.ClockProperties',ClkProperties)

 
            timeout = 5        
            while(timeout > 0): 
                time.sleep(10)
                locked = lta.__get__('Sync.LockStatus')
                if locked[None] == True:
                    lta.s.settimeout(90)               
                    lta.__run__() 
                    lta.s.settimeout(UsrTimeout)
                    break
                timeout = timeout - 1
                
            dlyTime = dlyTime - 0.05
#            if (dlyTime == .04):
#                dlyTime = 0
#            elif (dlyTime == -0.1):
#               dlyTime = -0.05
                                
            if locked[None] != True:
                raise Exception ('Sync module is not locked')
                
            #dlyTime = dlyTime - 0.05
 
                
                 

#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err

