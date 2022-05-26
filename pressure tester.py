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
    

#Initialize the stacks
n=20
zero2=2044
scale2=.4
adc2valuebuffer=deque(int(np.floor(n/2))*[zero2],int(np.floor(n/2)))

try:
    ADC = ADS1256.ADS1256()
    ADC.ADS1256_init()
    ADC_Value = ADC.ADS1256_GetAll()

    while(1):
        ADC_Value = ADC.ADS1256_GetAll()
        #
        adc2valuebuffer.appendleft(round(ADC_Value[2]/1000,0))
        print("\n2 ADC Buffered = %.0f"%(round(mean(list(adc2valuebuffer)),0)))
        print("Millibars = %.3f"%round((mean(list(adc2valuebuffer))-zero2)/scale2,3))
        

        
except :
    GPIO.cleanup()
    print ("\r\nProgram end     ")
    exit()
    
        

