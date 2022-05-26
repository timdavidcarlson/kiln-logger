#!/usr/bin/python
# -*- coding:utf-8 -*-


import time
import datetime
import math
import csv
import bisect
import ADS1256
import RPi.GPIO as GPIO
import numpy as np

from collections import deque
from statistics import mean

from tkinter import *
#Create an instance of the canvas
#win = Tk()

#Select the title of the window
#win.title("Thermocouple Data")

#Define the geometry of the window
#win.geometry("800x450+50+50")


def writeline(txt,fn):
    f = open(fn,'a+')
    f.write(txt+'\n')
    f.close()
    

def lookup_k(aval):
    where = bisect.bisect_left(datakeys_k, aval)
    lo = datakeys_k[where-1]
    hi = datakeys_k[where]
    if lo==hi: return data_k[lo]
    delta = float(aval-lo)/(hi-lo)
    return round(delta*data_k[hi] + (1-delta)*data_k[lo],3)

def lookup_s(aval):
    where = bisect.bisect_left(datakeys_s, aval)
    lo = datakeys_s[where-1]
    hi = datakeys_s[where]
    if lo==hi: return data_s[lo]
    delta = float(aval-lo)/(hi-lo)
    return round(delta*data_s[hi] + (1-delta)*data_s[lo],3)

def lookup_afr(aval):
    where = bisect.bisect_left(volt_key, aval)
    lo = volt_key[where-1]
    hi = volt_key[where]
    if lo==hi: return data_afr[lo]
    delta = float(aval-lo)/(hi-lo)
    return round(delta*data_afr[hi] + (1-delta)*data_afr[lo],3) 

   
#Initialize the Dictionary
data_k={}
data_s={}
data_afr={}

with open('/home/pi/Desktop/Data logger/type_k_lookup_table.csv', 'r') as csvfile:
        table = csv.reader(csvfile)
        for row in table:
            data_k.update({float(row[0]):float(row[1])})
            
with open('/home/pi/Desktop/Data logger/type_s_lookup_table.csv', 'r') as csvfile:
        table = csv.reader(csvfile)
        for row in table:
            data_s.update({float(row[0]):float(row[1])})
            
with open('/home/pi/Desktop/Data logger/AFR_lookup.csv', 'r') as csvfile:
        table = csv.reader(csvfile)
        for row in table:
            data_afr.update({float(row[0]):float(row[1])})


datakeys_k=sorted(data_k)
datakeys_s=sorted(data_s)
volt_key=sorted(data_afr)
    

#Initialize the stacks
n=20
zero0=5
zero1=172.6
zero2=2031
#zero7=16273
scale0=1300   #1340  5/12/2022
scale1=16.2   #17.2  5/12/2022
scale2=100
#scale7=1700
#timetable=deque(11*n*[float(1)], 11*n)
#for x in range(11*n):
#    timetable.appendleft(float(time.time())-100*x)  
#temptable1=deque(7*n*[9*zero1/5-32], 7*n)
#temptable7=deque(2*n*[24], 2*n)
#adc0valuebuffer=deque(5*n*[zero0],5*n)
#adc1valuebuffer=deque(11*n*[zero1],11*n)
#adc2valuebuffer=deque(int(np.floor(n/2))*[zero2],int(np.floor(n/2)))
#adc7valuebuffer=deque(23*n*[zero7],23*n)



writeline("Time"+","
#          +"Scaled ADC 1 value"+","
#          +"Temp ADC 1 Celcius"+","
          +"Temp ADC 1 F"+","
          +"Rate of Temp increase ADC 1 (F/hr)"+","
#          +"Temp ADC 7 Celcius"+","
#          +"Temp ADC 7 F"+","
#          +"Rate of Temp increase ADC 7 (F/hr)"+","
#          +"ADC 1 Value"+","
#          +"ADC 7 Value"+","
          +"Propane Pressure (PSI) ADC 2"+","
          +"O2 Sensor (AFR Value) ADC 0"+","
          ,"/home/pi/Desktop/temp_data_values.csv")

try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    ADC_Value = ADC.ADS1256_GetAll()
    #
    adc0valuebuffer=deque(11*n*[round(ADC_Value[0]/1000,0)],11*n)
    adc1valuebuffer=deque(11*n*[round(ADC_Value[1]/100,2)],11*n)
    adc2valuebuffer=deque(int(np.floor(n/2))*[round(ADC_Value[2]/1000,0)],int(np.floor(n/2)))
    #adc7valuebuffer=deque(23*n*[round(ADC_Value[7]/100,2)],23*n)
    #adc1valuebuffer.appendleft(0)
    timetable=deque(11*n*[float(1)], 11*n)
    celsius1=lookup_s(round((mean(list(adc1valuebuffer))-zero1)/scale1,3)) 
    temptable1=deque(11*n*[9*celsius1/5-32], 11*n)
    #for x in range(11*n):
    #    timetable.appendleft(float(time.time())-100*x) 
    #
    while(1):
        ADC_Value = ADC.ADS1256_GetAll()
        #
        print("\n"+str(datetime.datetime.now().strftime("%c")))
        timetable.appendleft(float(time.time()))
        deltatime=np.subtract(list(timetable)[1:2*n-1],list(timetable)[2:2*n])
        probesignal1=round(ADC_Value[1]/100,2)
        adc1valuebuffer.appendleft(probesignal1)
#        print ("\n1 ADC = " "%.3f" %((probesignal1-zero1)/scale1))
        celsius1=lookup_s(round((mean(list(adc1valuebuffer))-zero1)/scale1,3))
#        print("Degrees C = " "%.1f" %(celsius1))
        print("Degrees F = " "%.1f" %(9*celsius1/5+32))
        temptable1.appendleft(9*celsius1/5+32)
        deltatemp1=np.round(mean(list(temptable1)[1:n])-mean(list(temptable1)[n+1:2*n]),3)
        deltatemprate1=((deltatemp1)*3600/(np.round(mean(deltatime),3))/n)
        print("Rate of Temperature Increase per Hour (F/hr) = " "%.1f" %(deltatemprate1))
        
        OXsignal=round(ADC_Value[0]/1000,0)
        adc0valuebuffer.appendleft(OXsignal)
#        print("\n0 ADC scaled = %.3f"%((OXsignal-zero0)/scale0))
        afr=lookup_afr(round((mean(list(adc0valuebuffer))-zero0)/scale0,3))
        print("\nvolts = %.3f"%round(round((mean(list(adc0valuebuffer))-zero0)/scale0,3),3))
        print("AFR = %.3f"%afr)
        
        bars=round(ADC_Value[2]/1000,0)
        adc2valuebuffer.appendleft(bars)
#        print("\n2 ADC Buffered = %.0f"%(round(mean(list(adc2valuebuffer)),0)))
        print("\nPropane PSI = %.2f"%round((mean(list(adc2valuebuffer))-zero2)/scale2,3))
#        print ("3 ADC = %lf"%(ADC_Value[3]*5.0/0x7fffff))
#        print ("4 ADC = %lf"%(ADC_Value[4]*5.0/0x7fffff))
#        print ("5 ADC = %lf"%(ADC_Value[5]*5.0/0x7fffff))
#        print ("6 ADC = %lf"%(ADC_Value[6]*5.0/0x7fffff))
#        print ("\n7 ADC = " "%.3f" %((ADC_Value[7]-zero7)/scale7))
#        adc7valuebuffer.appendleft(ADC_Value[7])
#        celsius7=lookup_k(round((mean(list(adc7valuebuffer))-zero7)/scale7,3))
#        print("Degrees C = " "%.3f" %(celsius7))
#        print("Degrees F = " "%.3f" %(9*celsius7/5+32))
#        temptable7.appendleft(9*celsius7/5+32)
#        deltatemp7=np.round(mean(list(temptable7)[1:n])-mean(list(temptable7)[n+1:2*n]),3)
#        deltatemprate7=((deltatemp7)*3600/(np.round(mean(deltatime),3))/n)
#        print("Rate of Temperature Increase per Hour (F/hr) = " "%.3f" %(deltatemprate7))
        #
        writeline(str(time.time())+","
#                  +str((round((ADC_Value[1]-zero1)/scale1,3)))+","
#                  +str("%.3f" %(celsius1))+","
                  +str("%.3f" %(9*celsius1/5+32))+","
                  +str("%.3f" %(deltatemprate1))+","
#                  +str("%.3f" %(celsius7))+","
#                  +str("%.3f" %(9*celsius7/5+32))+","
#                  +str("%.3f" %(deltatemprate7))+","
#                  +str(ADC_Value[1])+","
#                  +str(ADC_Value[7])+","
#                  +str("%.3f" %(ADC_Value[2]))+","
                  +str("%.3f" %(round((mean(list(adc2valuebuffer))-zero2)/scale2,3)))+","
                  +str("%.3f" %(afr))+","
                  ,"/home/pi/Desktop/temp_data_values.csv")

        
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
    
