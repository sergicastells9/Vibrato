#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import p398dlp_read_audio_function as RA
import numpy as np

try:
    fname = sys.argv[1]
except IndexError:
    fname = "audio00.bin"

def rms(fname, convert=True):
    if convert == True:
        sname = "{0}_adc.csv".format(fname)
        audio_data = readADC(fname)
    if convert == False:
        max_buffers = 50000000
        audio_data = RA.read_audio(fname, max_buffers)
    
    x = 0.0
    x2 = 0.0
    n = len(audio_data)
    
    for i in audio_data:
        x += i
        x2 += i**2
    
    x = x/n
    x2 = x2/n
    
    rms = sqrt(x2 - x**2)
    return "RMS in ADC counts: " + str(rms)

def saveADC(fname):
    max_buffers = 50000000
    
    audio_data = RA.read_audio(fname, max_buffers)
    audio_data = np.asarray(audio_data, dtype=float)
    
    sname = "{0}_adc.csv".format(fname)
    np.savetxt(sname, audio_data, delimiter=",")
    print("{0} saved as csv file.".format(sname))
    
    return

def readADC(fname):
    sname = "{0}_adc.csv".format(fname)
    audio_data = np.genfromtxt(sname, dtype=float, delimiter=",")
    
    return audio_data

