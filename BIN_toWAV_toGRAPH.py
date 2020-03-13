
# coding: utf-8

# In[32]:


"""
################################################################################

This file is p398dlp_read_audio.py. It will call a function in the file
p398dlp_read_audio_function.py. 

Read an audio binary file written by an Arduino Mega 2560 using the Arduino 
program sound_record.io. If desired, write a wav formatted version of the file.

George Gollin, University of Illinois, September 19, 2018

The binary audio file format written by the Arduino for 10-bit ADC data follows.
An unsigned long is 4 bytes, while an unsigned short is 2 bytes. The following 
is from AnalogBinLogger.h:

*** First block of file (512 bytes) ***

  unsigned long  adcFrequency;     // ADC clock frequency
  unsigned long  cpuFrequency;     // CPU clock frequency
  unsigned long  sampleInterval;   // Sample interval in CPU cycles.
  unsigned long  recordEightBits;  // Size of ADC values, nonzero for 8-bits.
  unsigned long  pinCount;         // Number of analog pins in a sample.
  unsigned long  pinNumber[123];   // List of pin numbers in a sample.

*** Subsequent blocks (also 512 bytes each) ***

  unsigned short count;      // count of data values (should be 254)
  unsigned short overrun;    // count of overruns since last block (0, one hopes)
  unsigned short data[254];  // ADC data, low byte comes before by high byte.
                             // For example, 511 (= 255 + 256) will have
                             // data[0] = 255 (= 0xFF) and data[1] = 1 (= 0x01)
                             // This is "little endian" format.
                             
The program takes a minute or two on a Macbook Air to read and unpack 2,000,000 
# buffers, or about 508 million ADC samples. This would correspond to about 4 
# hours, 24 minutes of recording at 32 kHz.

The program can also write a WAV format audio file that can be played on most 
laptops. It takes about half as long to write the WAV file as to do the read
and unpack of that 508 million sample binary file.

There is good, clear information on wav format here: 
http://soundfile.sapp.org/doc/WaveFormat/. 

################################################################################    
"""


"""All you need to do is create a file called bins, put your .bin files in it and run the code"""
############################## initialize stuff ################################

# time and clock routines
import time    
# a library of stuff about US vs European text conventions
import locale
# numerical routines
import numpy as np
# import the wav library
import wave 

#import sys
#sys.path.append('/LeDoctorWhom/Downloads/')
# here is my audio file reader
import p398dlp_read_audio_function as RA
import os as os

# set the locale so we can put commas as thousands separators into our
# print statements.
locale.setlocale(locale.LC_ALL, 'en_US')    

##############################################################
##############################################################

# change the file names to suit your needs.

# Here's the name of the audio file.

if not os.path.exists("WAVs/"):
    os.mkdir("WAVs")

if os.path.exists("WAVs"):
    for _, _, old in os.walk("WAVs"):
        for file in old:
            os.remove("WAVs/" + str(file))
            
typechoice=input("Type 'f' for frequency and 'a' for amplitude: ")

if os.path.exists('bins'):
            for _, _, files in os.walk('bins'):
                for file in files:
                    filename = str(file)
                    wav_filename = filename[0:-3]+'wav'
                    print('\nconverting', file,'\n')

                    ##############################################################
                    ##############################################################

                    # number of buffers to read (my code checks for running out of data)
                    max_buffers =   50000000
                    # max_buffers =   5000

                    # write a WAV-format audio file?
                    write_wav = True

                    # maximum amplitude to scale wav values to... (signed 16 bit, so +/- 32,768)
                    wav_maximum_amplitude = 30000

                    # wav sample rate: 32 kHz
                    wav_sample_rate = 32000

                    ############################## read from the file ##############################

                    # away we go! print time information.
                    ##print("\nstart reading file at ", time.ctime())

                    # keep track of running time
                    start_time = time.time()

                    # call routine to read the audio file. 
                    audio_data = RA.read_audio('bins/'+filename, max_buffers)

                    # now all those ADC samples live in the audio_data array. 
                    ##print("ending time is ", time.ctime())

                    # calculate and print elapsed time
                    elapsed_time = time.time() - start_time
                    ##print("elapsed running time = ", elapsed_time, " seconds")

                    # more information...
                    ##print("length (words) of audio_data array ", len(audio_data))

                    # for fun, do some calculations:

                    # median, of course
                    median_audio = np.median(audio_data)

                    # also mean
                    mean_audio = np.mean(audio_data)

                    # max/min signals
                    max_audio = np.max(audio_data)
                    min_audio = np.min(audio_data)

                    # maximum amplitude relative to the median
                    amplitude_audio_wrt_median =                     max(median_audio - min_audio, max_audio - median_audio)

                    # RMS (strictly speaking, it's not a standard deviation if it isn't Gaussian...)
                    RMS_audio = np.std(audio_data)

                    #print some information 
                    ##print("\nmean and RMS of audio signal: ", mean_audio, " and ", RMS_audio)

                    ##print("min and max of audio signal: ", min_audio, max_audio)

                    ##print("median of audio signals: ", median_audio)

                    ##print("amplitude, relative to median: ", amplitude_audio_wrt_median)


                    ############################## write WAV file ##################################

                    if (write_wav):

                        ##print("\nstart writing the wav file at", time.ctime())

                        # calculate (and eventually print) a new elapsed time
                        start_time = time.time()

                        # shift the median of the audio data to be near zero. Handy, that python
                        # can add/subtract one number form all the elements in an array.
                        audio_data = audio_data - int(median_audio)

                        # now scale the amplitudes to make the signal louder. i want to keep 
                        # everything as integers for the sake of wav file writing.
                        scale_factor = int(wav_maximum_amplitude / amplitude_audio_wrt_median)
                        audio_data = audio_data * scale_factor

                        # now convert the array to a 16 bit integer, which is how it came out
                        # of the Arduino
                        audio_data = audio_data.astype(np.int16)
                        ##print("just finished converting the audio file to 16 bits per sample at", \
                              ##time.ctime())

                        ##print("start writing the audio data to the wav file")

                        # now write a binary file.
                        with wave.open("WAVs/"+wav_filename, 'wb') as wavfile:

                            # initialize a few wav parameters here
                            wav_NumChannels = 1
                            wav_BytesPerChannel = 2

                            # see https://docs.python.org/3/library/wave.html.
                            # parameters are (nchannels, sampwidth, framerate, nframes, comptype, compname)
                            # wavfile.setparams((wav_NumChannels, wav_BytesPerChannel, wav_SampleRate, 0, 'NONE', 'NONE'))
                            wavfile.setparams((wav_NumChannels, wav_BytesPerChannel,                                                wav_sample_rate, 0, 'NONE', 'noncompressed'))

                            # now write the file.
                            wavfile.writeframes(audio_data)

                        # all done so...
                        wavfile.close() 

                        # how long did this take?
                        elapsed_time = time.time() - start_time
                        ##print("elapsed time to write wav file = ", elapsed_time, " seconds")
                        ##print("all finished at time ", time.ctime())

                    # all done!
                    
                    
                    
########################################
######         FFT
########################################

import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy.fft as fftnp
def my_fft(wav_dir, amp_or_freq):
    if not os.path.exists("Fourier_Plots/"):
            os.mkdir("Fourier_Plots/")

    if os.path.exists("Fourier_Plots/Amplitude"):
        for _, _, old in os.walk("Fourier_Plots/Amplitude"):
            for file in old:
                os.remove("Fourier_Plots/Amplitude/" + str(file))
    if amp_or_freq == 'a':
        if not os.path.exists("Fourier_Plots/Amplitude/"):
            os.mkdir("Fourier_Plots/Amplitude")

        if os.path.exists("Fourier_Plots/Amplitude"):
            for _, _, old in os.walk("Fourier_Plots/Amplitude"):
                for file in old:
                    os.remove("Fourier_Plots/Amplitude/" + str(file))

        if os.path.exists(wav_dir):
            for _, _, files in os.walk(wav_dir):
                for file in files:
                    rate, data = wav.read(wav_dir + "/" + str(file))
                    fft_out = fft(data)
                    get_ipython().run_line_magic('matplotlib', 'inline')
                    plt.plot(data, np.abs(fft_out))
                    name = 'Fourier_Plots/Amplitude/' + str(file[ : -4])
                    x = name
                    count = 0
                    while os.path.exists(x):
                        count += 1
                        x = name + "(" + str(count) + ")"
                    plt.xlabel("Time [s]")
                    plt.ylabel("Amplitude")
                    plt.savefig(x, bbox_inches="tight")
                    plt.clf()
    elif amp_or_freq == 'f':
            if not os.path.exists("Fourier_Plots/Frequency/"):
                os.mkdir("Fourier_Plots/Frequency")

            if os.path.exists("Fourier_Plots/Frequency"):
                for _, _, old in os.walk("Fourier_Plots/Frequency"):
                    for file in old:
                        os.remove("Fourier_Plots/Frequency/" + str(file))

            if os.path.exists(wav_dir):
                for _, _, files in os.walk(wav_dir):
                    for file in files:
                        rate, data = wav.read(wav_dir + "/" + str(file))
                        fft_out = fftnp.rfft(data)

                        sp = fft_out
                        freq = fftnp.fftfreq(fft_out.shape[-1])
                        plt.plot(freq, sp.real)
                        name = 'Fourier_Plots/Frequency/' + str(file[ : -4])
                        x = name
                        count = 0
                        while os.path.exists(x):
                            count += 1
                            x = name + "(" + str(count) + ")"
                        plt.ylabel("Amplitude")
                        plt.xlabel("Frequency")
                        plt.savefig(x, bbox_inches="tight")
                        plt.clf()


my_fft('WAVs',typechoice)
print('\n''\n''\n', 'FINISHED')
                        
    

