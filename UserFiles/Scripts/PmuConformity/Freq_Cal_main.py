# -*- coding: utf-8 -*-
import time
from lta import Lta
import sys
from lta_err import Lta_Error
from collections import OrderedDict
import numpy as np


class StdTests(object):
    """This object is intended to be a set of standard tests that shall follow the test suit specification, 
    whose methods are capable of setting parameters and sending messages to actually run them through a 
    Labview framework
    
    Attributes:  
    
    Duration = Analysis Duration in seconds
    Config = Analysis Configuration
        Config[F0]
        Config[SettlingTime]
        Config[AnalysisCycles]
        Config[SampleRate] = Analysys Digitizer SampleRate
        Config[NumChannels]
    
    Fs = PMU Reporting Rate 
    Vnom  = Nominal voltage level (defaults to RMS 70 VAC )
    Inom = Nominal current level (defaults to RMS 5 A )
    PMUclass  = M or P class
    lta   - object to connect Labview host
    ntries - Number of running tries
    secwait - Seconds to wait before next try
    ecode - error code for trying again
    Dur - test duration (default 5 seconds)
    """
    
    @staticmethod
    def getParamIdx():
        #useful indices# 
        Xm=0;Fin=1;Pin=2;Fh=3;Ph=4;Kh=5;Fa=6;Ka=7;Fx=8;Kx=9;Rf=10;KaS=11;KxS=12;KfS=13;KrS=14;
        return Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS
        
    @staticmethod
    def getPhaseIdx():
        VA=0;VB=1;VC=2;IA=3;IB=4;IC=5;
        return VA,VB,VC,IA,IB,IC
        
    
      #constructor
    #def __init__(self,Fs,F0,Fsamp,Vnom,Inom,Duration,PMUclass,lta,ntries,secwait,ecode):
    def __init__(self,Duration,Fs,Config,Vnom,Inom,PMUclass):
        try: 
            if PMUclass != "M" and PMUclass != "P":
                raise Exception('Error: Unrecognizable PMU class')

        #Would be good to limit these to safe values 
            self.Duration = float(Duration)
            self.Fs = float(Fs)
            self.Config = Config

 
            self.Vnom = Vnom
            self.Inom = Inom            
            self.PMUclass = PMUclass
            
            self.ntries = 30
            self.secwait = 60
            self.ecode = {5605}  #set of error codes under which we need to try again

        except Exception as ex:
            raise ex   
  
 # Initialize framework to default values 
    def set_init(self):
                    #useful indices
        Xm,Fin,Pin,Fh,Ph,kh,Fa,ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS=self.getParamIdx()
        VA,VB,VC,IA,IB,IC=self.getPhaseIdx()

        try:
            """ Sets initial default values to the framework"""
            print("Setting default params")
            #Setting Duration
        
        
            #Analysis.Duration
            Error=lta.__set__('Analysis.Duration',{None: self.Duration})
            
            #Analysis.Config
            Error=lta.__set__('Analysis.Config',{None: self.Config})
            
            #Setting Waveform Params
            WfrmParams = lta.__get__('FGen.FunctionParams')
                        
            # default values
            WfrmParams[None][Xm][VA:VC+1] = float(self.Vnom)
            WfrmParams[None][Xm][IA:IC+1] = float(self.Inom)
            WfrmParams[None][Fin][:] = self.Config['F0']
            WfrmParams[None][Pin][VA] = WfrmParams[None][Pin][IA] = float(0.)
            WfrmParams[None][Pin][VB] = WfrmParams[None][Pin][IB] = float(-120.)
            WfrmParams[None][Pin][VC] = WfrmParams[None][Pin][IC] = float(120.)
            WfrmParams[None][Fh:][:] = float(0.) #all remaining parameters are null
            Error = lta.__set__('FGen.FunctionParams',WfrmParams)

            print("Initial Values have been set")

        except Exception as ex:
            print Error
            raise ex


# Frequency Range tests
    def FreqRange(self):
        print ("Performing Frequency Range Tests")
        
        # Start ans stop frequencies dependi on PMU Class 
        range = 5
        if self.PMUclass != 'M':
            range = 2
            
        incr = 0.5  #frequency increment
        Fin = 1     # index to the frequency parameters
        
        #freq = self.Config['F0'] - range
        #fStop = freq + 2 * range + incr     # stop before ine step aftr the last
        freq = 55.5        
        fStop = 75.5        
        
        try:          
            try:
                self.set_init()     # set up the initial parameters
                WfrmParams = lta.__get__('FGen.FunctionParams')
                    
            except Exception as ex:
                raise ex
                                
            while freq<fStop: 
                tic =time.clock()
                time.sleep(5.0)
                print 'freq = ',freq
                WfrmParams[None][Fin][:] = float(freq)
                try:
                    Error = lta.__set__('FGen.FunctionParams',WfrmParams)
                    lta.s.settimeout(200)   
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(freq)+ex.message) 
                    
                # wait for the calibrator calibration system,    
                toc = time.clock()    
                while (toc - tic)<30:
                    time.sleep(0.1)
                    toc = time.clock()    
                
                
                print('Duration = ',(toc - tic))
    
                freq += incr
                             
        except Exception as ex:
            raise type(ex) ("Frequency Range Test Failure:"+ex.message)
            
            
    def MagRange(self):
        print ("Performing Magnitude Range Tests") 
        Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS=self.getParamIdx()
        incr = 0.1
        iMag = 0.1  
        vMag = 0.1
        if self.PMUclass != 'M':
            vMag = 0.8
            

        try:   
            try:
                self.set_init()
                WfrmParams = lta.__get__('FGen.FunctionParams')
                A = WfrmParams[None][Xm].copy()
            
            except Exception as ex:
                raise ex
                
            #while iMag < 2.1:
            while iMag < 1.5:
                
                #print ('iMag = ',iMag, 'VMag = ',vMag)                
                WfrmParams[None][Xm][0:3] = float(vMag)*A[0:3]
                WfrmParams[None][Xm][3:7] = float(iMag)*A[3:7]
                #print A
                print 'Magnitudes: ',WfrmParams[None][Xm]
                iMag += incr
                if vMag < 1.2:
                    vMag += incr
                    
                try:
                    Error = lta.__set__('FGen.FunctionParams',WfrmParams)
                    lta.s.settimeout(200)   
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                       
                except Exception as ex:
                    print (Error)
                    raise type(ex)(ex.message)                     
                 
        except Exception as ex:
            raise type(ex) ("Magnitude Range Test Failure:"+ex.message)
                 
            
# Harmonic Interfereing Signals test
    def Harm(self):
        print ("Performing Harmonic Intefering Signal Tests")

        range = 50      # number of harmonics to test
        fund = self.Config['F0'] 
        Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS=self.getParamIdx()
        incr = 2
        hFreq = fund * incr;

        try:
            try:
                self.set_init();
                WfrmParams = lta.__get__('FGen.FunctionParams')
                WfrmParams[None][Ph][:] = [0, -120, 120, 0, -120, 120 ]
                WfrmParams[None][Kh][:] = float(0.1)
                
            except Exception as ex:
                raise ex
                
            while hFreq<=fund*range:
                print 'harmonic number =', incr, ' frequency = ',hFreq
                WfrmParams[None][Fh][:] = float(hFreq)
                try:
                    Error = lta.__set__('FGen.FunctionParams',WfrmParams)
                    lta.s.settimeout(200)                       
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                            
                                                                           
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(hFreq)+ex.message) 
                    
                incr += 1;
                hFreq = incr*fund                                    
                
        except Exception as ex:
            raise type(ex) ("Harmonic Test Failure:"+ex.message)
        
  # Interharmonic Intefering Signals test
    def IHarm(self):
        print("Performing Interharmonic Intefering Signals Tests")

        Xm,Fin,Pin,Fh,Ph,Kh,Fa,Ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS=self.getParamIdx()
        
        try:
            try:
                self.set_init();
                WfrmParams = lta.__get__('FGen.FunctionParams')
            except Exception as ex:
                raise ex
                
            WfrmParams[None][Ph][:] = [0, -120, 120, 0, -120, 120 ]
            WfrmParams[None][Kh][:] = float(0.1)
            iFreq = self.Config['F0']
            iFreqList = []
            incr = 0
            
            # create a list of frequencies IAW 60255-118-1 table 2            
            while iFreq > 10:
                
                # PMU Standard increments
                #iFreq = self.Config['F0'] - self.Fs/2 - (0.1 * 2**incr)
                # IEC frequency TR increments: 0.5 Hz
                iFreq = self.Config['F0'] - 5 - (0.5*incr)
                
                if iFreq < 10:
                    iFreq = 10
                #print '# ',incr,'Interharmonic Frequency = ', iFreq
                iFreqList.append(iFreq)
                incr += 1
                
            iFreqList.reverse()
            incr = 0
            
            while iFreq < 2 * self.Config['F0']:
                
                # PMU Standard increments
                #iFreq = self.Config['F0'] + self.Fs/2 + (0.1 * 2**incr)
                # IEC frequency TR increments: 0.5 Hz
                iFreq = self.Config['F0'] + 5 + (0.5*incr)
                
                if iFreq > 2 * self.Config['F0']:
                    iFreq = 2 * self.Config['F0']
                #print '# ',incr,'Interharmonic Frequency = ',iFreq                    
                iFreqList.append(iFreq)
                incr +=1
                
            #iterate over the list of iterharmonic frequencies
            for iFreq in iFreqList:
                print 'Interharmonic Frequency = ', iFreq
                WfrmParams[None][Fh][:] = float(iFreq)
                try:
                    Error = lta.__set__('FGen.FunctionParams',WfrmParams)
                    lta.s.settimeout(200)                       
                    Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                    lta.s.settimeout(10)                            
                                                                           
                except Exception as ex:
                    print (Error)
                    raise type(ex)(str(iFreq)+ex.message) 
                                     
        except Exception as ex:
            raise type(ex) ("Interharmonic Test Failure:"+ex.message)
                

# Measurement bandwidth (modulation)
#
#   Modfication of the PMU test to test the operating range of frequency instruments
# First ask the user for the maximum operating range frequency and the maximum ROCOF and compute 
# fmax and kmax. 
# then hold fm = fmax and vary km logarithmically (with more values near the top.) 
# finally, hold km = kmax and vary fm logarithmically (with more values near the top.)
# 
    def MeasBand(self):
        from math import pi
        from math import log10        
        
        FreqMax = input("Input the maximum of the frequency operating range: ")
        RocofMax = input("Input the maximum ROCOF allowed by the instrument: ")
        
        Fmax = RocofMax/((2*pi)*(FreqMax - 50))
        Kmax = ((2*pi)*(FreqMax - 50)**2)/RocofMax
        print "Fmax = %2.2f, Kmax = %2.2f" % (Fmax,Kmax)
                   
        # get the parameter indices        
        _,_,_,_,_,_,Fa,Ka,Fx,Kx,_,_,_,_,_=self.getParamIdx()
        #VA,VB,VC,IA,IB,IC=self.getPhaseIdx()               
        
        
        try:
            self.set_init()
            WfrmParams = lta.__get__('FGen.FunctionParams')
        except Exception as ex:
            raise type(ex)("Measurement Bandwidth Test - unable to get Waveform Parameters . " +ex.message)
            
        # Amplitude Modulation
        WfrmParams[None][Kx][:] = float(0.1)
        WfrmParams[None][Ka][:] = float(0)
        fmod = range(1,int(Fmax*10),2)+[int(Fmax*10)]
        
        # loop through the range of frequencies        
#        for f in fmod:
#            print "Fmod = ", float(f)/10
#            WfrmParams[None][Fx][:] = float(f)/10
#            
#            # set the waveform params            
#            try:
#                Error = lta.__set__('FGen.FunctionParams',WfrmParams)
#            except Exception as ex:
#                print Error
#                raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
#            
#            # run one test
#            try:
#                lta.s.settimeout(200)                       
#                Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
#                lta.s.settimeout(10)                            
#                                                                           
#            except Exception as ex:
#                print (Error)
#                raise type(ex)("Kx="+str(WfrmParams[None][Kx][1]) 
#                                    +", fmod="+ str(f)+"Hz, Fs="+str(self.Fs)+". "+ex.message+ex.message) 
                                    
                                    
        WfrmParams[None][Fx][:] = float(0)
        WfrmParams[None][Kx][:] = float(0)
        
        # Frequency Modulation Tests
        # two phases of this test:
        #   Phase 1:  Hold the fm constant at Fmax and vary Km
        #   Phase 2: Hold the km constant at Kmax and vary fm
        mults = list(log10(0.5*(i+2)) for i in range(1,19))   # we are going to iterate over this twice    
        
        
        print "Frequency Modulation Tests, Phase 1, Km constant and vary Fm"
        WfrmParams[None][Ka][:] = float(Kmax)
        for m in mults:
            print "Fmod = ", float(Fmax)*m
            WfrmParams[None][Fa][:] = float(Fmax)*m
            
            # set the waveform params            
            try:
                Error = lta.__set__('FGen.FunctionParams',WfrmParams)
            except Exception as ex:
                print Error
                raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
            
            # run one test
            try:
                lta.s.settimeout(200)                       
                Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                lta.s.settimeout(10)                            
                                                                           
            except Exception as ex:
                print (Error)
                raise type(ex)("Ka="+str(WfrmParams[None][Ka][1]) 
                                    +", fmod="+ str(Fmax*m)+"Hz, Fs="+str(self.Fs)+". "+ex.message+ex.message) 
           
        print "Frequency Modulation Tests, Phase 2, Fm constant and vary Km"
        WfrmParams[None][Fa][:] = float(Fmax)
        for m in mults:
            print "Kmod = ", float(Kmax)*m
            WfrmParams[None][Ka][:] = float(Kmax)*m
            
            # set the waveform params            
            try:
                Error = lta.__set__('FGen.FunctionParams',WfrmParams)
            except Exception as ex:
                print Error
                raise type(ex)("Measurement Bandwidth Test - unable to set Waveform Parameters . " +ex.message)
            
            # run one test
            try:
                lta.s.settimeout(200)                       
                Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
                lta.s.settimeout(10)                            
                                                                           
            except Exception as ex:
                print (Error)
                raise type(ex)("Fa="+str(WfrmParams[None][Fa][1]) 
                                    +", kmod="+ str(Kmax*m)+"Hz, Fs="+str(self.Fs)+". "+ex.message+ex.message) 
           
           

# Step Changes
    def Step(self):
        print("Performing Step Change Tests")
        
        #stepTime = .002;
        numSteps = 10;
        stepTime = .1/self.Config['F0']
        magAmpl = 0.1
        angleAmpl = 10
        #freqStep = 1
        self.Duration = float(2)
        
        Xm,Fin,Pin,Fh,Ph,kh,Fa,ka,Fx,Kx,Rf,KaS,KxS,KfS,KrS=self.getParamIdx()
        VA,VB,VC,IA,IB,IC=self.getPhaseIdx()
        

        try:        
            try: 
                #self.set_init()     # default function parameters
                
                # Step index                    
                params = lta.__get__('FGen.FunctionParams')
                params[None][KxS][:] = float(magAmpl)
                Error = lta.__set__('FGen.FunctionParams',params)
                
                arbs = lta.__get__('FGen.FunctionArbs')  
                
            except Exception as ex:
                raise type(ex) ("Step Change Test Failure:"+ex.message)
                
            iteration = numSteps
            while iteration > 0:
                print 'mag step iterations remaining = ', iteration 
                self.__iterStep__(arbs)
                iteration += -1
                
            try:            
                params[None][KxS][:] = float(0)
                params[None][KaS][:] = float(angleAmpl) 
                Error = lta.__set__('FGen.FunctionParams',params)
                arbs['FunctionConfig']['T0'] = float(0.5*stepTime*numSteps)
                Error = lta.__set__('FGen.FunctionArbs',arbs)
            except Exception as ex:
                print(Error)
                raise type(ex)(ex.message) 
           
            iteration = 10            
            while iteration > 0:
                print 'angle step iterations remaining = ', iteration 
                self.__iterStep__(arbs)  
                iteration += -1
                
        except Exception as ex:
            raise type(ex) ("Step Change Test Failure:"+ex.message)
            
            
            # frequency step            
#            try:            
#                params[None][KxS][:] = float(0)
#                params[None][KaS][:] = float(0) 
#                params[None][KfS][:] = float(freqStep)
#                Error = lta.__set__('FGen.FunctionParams',params)
#                arbs['FunctionConfig']['T0'] = float(0.5*stepTime*numSteps)
#                Error = lta.__set__('FGen.FunctionArbs',arbs)
#            except Exception as ex:
#                print(Error)
#                raise type(ex)(ex.message) 
#           
#            iteration = 10            
#            while iteration > 0:
#                print 'angle step iterations remaining = ', iteration 
#                self.__iterStep__(arbs)  
#                iteration += -1
#                
#        except Exception as ex:
#            raise type(ex) ("Step Change Test Failure:"+ex.message)
                    
    # this is here so the last actual test in the main.funcList can have a comma aster it
    # used for commenting out tests
    def Pass(self):
       pass

   # one iteration of the step test
    def __iterStep__(self,arbs):
        stepTime = .1/self.Fs

        try: 
           lta.s.settimeout(200)
           Error = lta.__multirun__(self.ntries,self.secwait,self.ecode)
           lta.s.settimeout(10)                       
           print 'T0 = ',arbs['FunctionConfig']['T0']
           arbs['FunctionConfig']['T0'] = float(arbs['FunctionConfig']['T0']-(stepTime))
           Error = lta.__set__('FGen.FunctionArbs',arbs)                    
        except Exception as ex:
           print (Error)
           raise type(ex)(ex.message) 
           
# ------------------ MAIN SCRIPT ---------------------------------------------
#------------------- following code must be in all scripts--------------------
lta = Lta("127.0.0.1",60100)    # all scripts must create  an Lta object

try:
    lta.connect()                   # connect to the Labview Host
#---------------------Script code goes here------------------------------------

    print lta

    UsrTimeout = lta.s.gettimeout()
    
    Duration = 6    # Analysis.Duration
    
    # Analysis.Config
    Config = OrderedDict()      
    Config['F0'] = np.uint32(50) 
    Config['SettlingTime']= 1.0
    Config['AnalysisCycles'] = float(6.0)
    Config['SampleRate'] = float(48000)
    Config['NumChannels']= np.uint32(6)   
    
   
    Fs_ini = 60.  #doesnt matter this default value, to be changed later
    #Fs_list = {60:[10,12,15,20,30,60],50:[10,25,50], 63:[10]} #63 inserted for testing
    FSamp = 48000.
    Vnom = 70.
    Inom = 5.
    PMUclass = "M"
    #PMUclass = 'P'
    Fs = 50
    
    #list of exceptions             
    ex_list = []


    # StdTests instance
    t = StdTests(Duration,Fs,Config,Vnom,Inom,PMUclass)
    
    
    
    #list of tests to be performed
    func_list = [
                 #t.FreqRange,
                 #t.MagRange, 
                 #t.Harm, 
                 #t.IHarm,
                 t.MeasBand, 
                 #t.RampFreq, 
                 #t.Step ,
                 #t.RepLatency
                 t.Pass]     



    #execution of tests for each Fs
    for my_func in func_list:
        try:
            lta.s.settimeout(10)   
            my_func()
            lta.s.settimeout(UsrTimeout)
        except Exception as ex:
            print "Exception going to LV in the end:"
            print ex
            ex_list.append(ex)
            err = Lta_Error(ex,sys.exc_info())  #format a labview error
            lta.send_error(err,3,'log')       #send the error to labview for log
    
    print "FINAL ERROR LIST::"
    print ex_list
    for ex in ex_list:
        err = Lta_Error(ex,sys.exc_info())  #format a labview error
        lta.send_error(err,3,'log')       #send the error to labview for log

#------------------all scripts should send their errors to labview------------
except Exception as ex:
    err = Lta_Error(ex,sys.exc_info())  #format a labview error
    lta.send_error(err,3,'Abort')       #send the error to labview for display
    lta.close()
    print err
