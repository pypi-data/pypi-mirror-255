#from curses.ascii import NUL
#from datetime import timedelta
#from distutils.command.build_scripts import first_line_re
#from doctest import testfile
#from http.client import NOT_MODIFIED
#from os import device_encoding
#from pickle import TRUE
#from re import L
import sys
import numpy as np
import math
import nidmm
import nidaqmx
import nidaqmx.system
import niswitch
from threading import Thread
from nidmm.enums import AutoZero
from nidmm.enums import MeasurementCompleteDest
import  nidaqmx.stream_writers
from nidaqmx import stream_readers
from nidaqmx import stream_writers
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType
import nidaqmx.constants
from nidaqmx._task_modules.export_signals import ExportSignals
from nidaqmx._task_modules.triggering import start_trigger
import matplotlib.pyplot as plt
import time
from enum import Enum
 

class PXIControll(Thread):
    dmmList = []
    __analogList = []
    __switchSlotName = ""

    dmmSession = []
    main_dmmSession = 0
    __analogOutTask = 0
    __analogInTask = 0
    __digitalOutTask = 0
    __samples_to_read_Analog_In = []
    __daqmxReader = 0
    __daqmxWriter = 0
    __switchSession = 0
    analogInResults = []
    __analogInDict= []

    dmmRequirements = ["slotName", "range", "sampleFreq", "wavepoints"]

    aoRequirements = ["slotName", "channel", "minVal", "maxVal", "rate", "exportTrigger", "digitalSignal"]

    aiRequirements = ["slotName", "channel", "minVal", "maxVal", "rate", "wavepoints","aoTrigger"]


    hardwareType_ = Enum('hardwareType', ['DMM', 'AI', 'AO'])


    def __init__(self):
       
        print("PXI Controll called!")
       
    def createZeroArray(self, num_of_elements):
        
        array = []

        for i in range(num_of_elements):
            array.append(0.0)
        return array

    def printConnectedPXIDevs(self):
        system = nidaqmx.system.System.local()

        print("Connected PXI devices:")
        try:
            for device in system.devices:
                print(device)
        except:
            return
    
    def checkDictionaryRequirements(self, to_check:dict, hardwareType):
        valid_key_found = False
        requirements = {}
        if hardwareType == self.hardwareType_.DMM:
            for requirement in self.dmmRequirements:
                valid_key_found = False
                for key in to_check:
                    if key == requirement:
                        valid_key_found = True
                        break
                if valid_key_found == False:
                    return False
                
        if hardwareType == self.hardwareType_.AI:
           for requirement in self.aiRequirements:
                valid_key_found = False
                for key in to_check:
                    if key == requirement:
                        valid_key_found = True
                        break
                if valid_key_found == False:
                    return False ,
        if hardwareType == self.hardwareType_.AO:
           for requirement in self.aoRequirements:
                valid_key_found = False
                for key in to_check:
                    if key == requirement:
                        valid_key_found = True
                        break

                if valid_key_found == False:
                    return False
            

        return True


    def connectHardware(self, dmmDict = 0, analogOutDict = 0, anlaogInDict = 0, switchSlotName = 0):
    
        if dmmDict != 0:
            for key in dmmDict:
                if self.checkDictionaryRequirements(dmmDict[key], self.hardwareType_.DMM) == False:
                    print("Your DMM dictionary does not include required keys!")
                    return False
            self.createdmmSession(dmmDict)
        if analogOutDict != 0:
            for key in analogOutDict:
                if self.checkDictionaryRequirements(analogOutDict[key], self.hardwareType_.AO) == False:
                    print("Your anlaog-out dictionary does not include required keys!")
                    return False
            self.createAnalogOutputTask(analogOutDict)
        if anlaogInDict != 0:
            for key in anlaogInDict:
                if self.checkDictionaryRequirements(anlaogInDict[key], self.hardwareType_.AI) == False:
                    print("Your analog-in dictionary does not include required keys!")
                    return False
            self.createAnalogInputTask(anlaogInDict) 
        if switchSlotName != 0:
            self.configureSwitch(switchSlotName)
        
        


    def createdmmSession(self, dmmDict):
        for key in dmmDict:
            self.dmmList.append(dmmDict[key])        
            self.dmmSession.append(self.configureDMM(dmmDict[key]["slotName"], dmmDict[key]["range"], dmmDict[key]["sampleFreq"],dmmDict[key]["wavepoints"]))
        
     

    def configureDMM(self,slotName,range,sF,wavePoints):
        try:
                nidmm.Session(slotName).reset()
                session = nidmm.Session(slotName) 
                print("Connencted: " + slotName + " | " + session.instrument_model)
                
                if session.instrument_model == "NI PXIe-4081":
                    session.configure_waveform_acquisition(nidmm.Function.WAVEFORM_VOLTAGE, range, int(sF), 0)
                else:
                    session.configure_waveform_acquisition(nidmm.Function.WAVEFORM_VOLTAGE, range, int(sF), wavePoints)
    
                session.configure_trigger(trigger_source= nidmm.TriggerSource.PXI_TRIG5, trigger_delay=0)
                session.powerline_freq = 50
                session.auto_zero = AutoZero.OFF
                session.adc_calibration = nidmm.ADCCalibration.OFF
                session.settle_time = 0

                session.initiate()
                return session
                
        except Exception as e:
                print("Problem trying to configure DMM on '" + slotName +"'!")        
                print(e)      
                return -1
                

    def createAnalogOutputTask(self, analogOutDict):
        for key, value in analogOutDict.items():
            first_key_out = key
            break

        try:
            self.__analogOutTask = nidaqmx.Task("outputTask")
            
            self.__daqmxWriter = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.__analogOutTask.out_stream)
  
        except Exception as e:
            print("Problem trying to configure '"+ analogOutDict[first_key_out]["slotName"] + "'!")
            return -1
            
        for key in analogOutDict:
            self.addAnalogOutputChannel(analogOutDict[key]["slotName"], analogOutDict[key]["channel"], analogOutDict[key]["minVal"], analogOutDict[key]["maxVal"])

        if analogOutDict[first_key_out]["exportTrigger"] == True:
            self.__analogOutTask.export_signals.export_signal(nidaqmx.constants.Signal.START_TRIGGER, "/"+analogOutDict[first_key_out]["slotName"]+"/PXI_Trig5")

        if analogOutDict[first_key_out]["digitalSignal"] == True:
            self.__digitalOutTask = nidaqmx.Task("digitalTask")
            self.__digitalOutTask._do_channels.add_do_chan(analogOutDict[key]["slotName"] + "/port0/line0")
        
        self.__analogOutTask.timing.cfg_samp_clk_timing(rate = analogOutDict[first_key_out]["rate"],sample_mode= AcquisitionType.CONTINUOUS)      
        self.__analogOutTask.timing.samp_timing_type = nidaqmx.constants.SampleTimingType.SAMPLE_CLOCK
        
        print("Connected: "+ analogOutDict[first_key_out]["slotName"] + " | AnalogOutput")



    def createAnalogInputTask(self, analogInDict):
 
        for key, value in analogInDict.items():
            first_key_in = key
            break
        try:
            self.__analogInTask = nidaqmx.Task("inputTask")
            self.__daqmxReader = AnalogMultiChannelReader(self.__analogInTask.in_stream)
        except Exception as e:
            print("Problem trying to configure '"+ analogInDict[first_key_in]["slotName"] + "'!")
            print(e)
        


        self.__analogInDict = analogInDict
       
        for key in analogInDict:    
            self.addAnalogInputChannel(analogInDict[key]["slotName"], analogInDict[key]["channel"], analogInDict[key]["minVal"], analogInDict[key]["maxVal"])
            self.__samples_to_read_Analog_In.append(analogInDict[key]["wavepoints"])
        
        self.__analogInTask.timing.cfg_samp_clk_timing(rate = analogInDict[first_key_in]["rate"],sample_mode= AcquisitionType.CONTINUOUS) 

        if analogInDict[first_key_in]["aoTrigger"] == True:
            self.__analogInTask.triggers.start_trigger.cfg_dig_edge_start_trig("ao/StartTrigger", trigger_edge=nidaqmx.constants.Edge.RISING)
            self.__analogInTask.input_buf_size = analogInDict[first_key_in]["wavepoints"]   
            self.__analogInTask.register_every_n_samples_acquired_into_buffer_event(analogInDict[first_key_in]["wavepoints"], self.callBackStartAnalogInputTask)
        print("Connected: "+ analogInDict[first_key_in]["slotName"] + " | AnalogInput")

    def addAnalogOutputChannel(self, slotName, channel, minVal, maxVal):
        try:
            self.__analogOutTask._ao_channels.add_ao_voltage_chan(slotName+"/"+ channel, min_val=minVal, max_val=maxVal) 
        except Exception as e:
      
            print("Problem trying to add Analog output channel '"+ slotName +"/"+ channel + "'!")
            return -1

    def addAnalogInputChannel(self , slotName, channel, minVal, maxVal):
        try:
            self.__analogInTask._ai_channels.add_ai_voltage_chan(slotName + "/" + channel, min_val=minVal, max_val= maxVal)
        except Exception as e:
            print(e)
            print("Problem trying to add Analog input channel '"+ slotName +"/"+ channel + "'!")
            return -1
    def analog_output_callback(self,task_handle, every_n_samples_event_type, number_of_samples, callback_data = None):

        self.__digitalOutTask.start()
      
        return 0 

     

    def configureSwitch(self, slotName):
        try:
            self.__switchSession = niswitch.Session(slotName)
            print("Connected: Switch |" + self.__switchSession.instrument_model)
        
            self.__switchSession.scan_advanced_output = niswitch.ScanAdvancedOutput.TTL5
            self.__switchSession.trigger_input = niswitch.TriggerInput.SOFTWARE_TRIG
            self.__switchSession.scan_list = "com0->ch0;"
          
          
            self.__switchSlotName = slotName
            
        except Exception as e:
            print("Problem trying to configure Switch on '"+ slotName + "'!")
       
            self.printConnectedPXIDevs()
            return -1

    


    def startAnalogOutputTask(self, outputSignal):
        try:

            if self.__analogOutTask == 0:
                print("No Tasks for Analogoutput have been created yet! Please create Tasks with 'connectHardware' before calling this Method!")
                return -1
            if len(self.__analogInDict) != 0:
                for key, value in self.__analogInDict.items():
                    first_key_in = key
                    break
                
                if self.__analogInDict[first_key_in]["aoTrigger"] == True:
                    self.__analogInTask.start()
            if self.__digitalOutTask != 0:            
                self.__digitalOutTask.write(np.asarray([True]))
                self.__digitalOutTask.start()

            print("Start analog output!")
            self.__analogOutTask.write(outputSignal)
            self.__analogOutTask.start()
            if self.__digitalOutTask != 0:
                time.sleep(1)
                self.__digitalOutTask.stop()
                self.__digitalOutTask.write(np.asarray([False]))
                self.__digitalOutTask.start
                self.__digitalOutTask.close()
        
        except KeyboardInterrupt as e:
            print("Measurement interrupted closeing analog output task!")
            self.closeAnalogOutputTask()
        
        except Exception as e:
            print("Could not start analog output task! Please create Tasks with 'connectHardware' before calling this Method!")
           
        

 
        

    def startAnalogInputTask(self):
        if self.__analogInTask == 0:
            print("No Tasks for AnalogInput have been created yet! Please create Tasks with 'connectHardware' before calling this Method!")
            return -1
        results = []
        for num_of_samples in self.__samples_to_read_Analog_In:
            results.append(self.createZeroArray(self.__samples_to_read_Analog_In[0]))
        results = np.asarray(results)        

        

        self.__analogInTask.start()

        print("Analog input started!")
        
        self.__daqmxReader.read_many_sample(results , self.__samples_to_read_Analog_In[0],nidaqmx.constants.WAIT_INFINITELY)

        self.closeAnalogInputTask()
        
        return results
  
    
    def callBackStartAnalogInputTask(self,task_idx, event_type, num_samples, callback_data=None):
        if self.__analogInTask == 0:
            print("No Tasks for AnalogInput have been created yet! Please create Tasks with 'connectHardware' before calling this Method!")
            return -1
        results = []
        for num_of_samples in self.__samples_to_read_Analog_In:
            results.append(self.createZeroArray(self.__samples_to_read_Analog_In[0]))
        results = np.asarray(results)

        
        print("Analog input started!")
        self.__daqmxReader.read_many_sample(results , self.__samples_to_read_Analog_In[0],nidaqmx.constants.WAIT_INFINITELY)
      

        self.analogInResults = results

        self.closeAnalogInputTask()
      
        return 0
        
        
        
    def closeAnalogOutputTask(self):   
        try:    
            self.__analogOutTask.close()
            self.__analogOutTask = 0
       
            self.__daqmxWriter = 0
        except Exception as e:
            print("Could not close Analog output task!")

    def closeAnalogInputTask(self):
        try:
            self.__analogInTask.close()
            self.__analogInTask = 0
            self.__daqmxReader = 0

            self.__samples_to_read_Analog_In.clear()
        except Exception as e:
            print("Could not close Analog input task!")
    def startMeasurement(self):       
        if len(self.dmmSession) == 0:
             print("No DMM Sessions have been created yet! Please create Sessions with 'connectHardware' before calling this Method!")
             return -1 
        if self.__switchSession == 0:
             print("No Switch Sessions have been created yet! Please create Sessions with 'connectHardware' before calling this Method!")
             return -1

     
        try:
            self.__switchSession.initiate()
            self.__switchSession.send_software_trigger()
            print("Measurement in Progress")
        except Exception as e:
            print("Could not send trigger to start Measurement")
            print(e)
       
      
  
   
    def getMeasResults(self):
        allInputs = []

        try:
        
            for i, session in enumerate(self.dmmSession):
                    
                allInputs.append(session.fetch_waveform(self.dmmList[i]["wavepoints"]))
                
                session.close()
           
        except Exception as e:
            print("Could not fetch results!")
            #print(e)
          
      
        self.allInputs = allInputs
        self.dmmSession.clear()
    
        return allInputs


    
