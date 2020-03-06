"""
################################################################################

This file is p398dlp_read_audio_function.py. 

Read an audio binary file written by an Arduino Mega 2560 using the Arduino 
program sound_record.io.

George Gollin, University of Illinois, September 16, 2018

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
                             
The program takes about 80 seconds on a Macbook Air to read and unpack 2,000,000 
# buffers, or about 508 million ADC samples. This would correspond to about 4 
# hours, 24 minutes of recording at 32 kHz.

################################################################################    
"""

def read_audio(audio_filename, max_buffers_to_read):
    
    ############################## initialize stuff ################################
    
    # get a structure-handling library.
    import struct    
    # also the ubiquitous numpy
    import numpy as np    
    # a library of stuff about US vs European text conventions
    import locale 
    
    # open this binary file in read mode
    audio_file = open(audio_filename, 'rb')
    print("reading from file ", audio_filename)
    
    # file's block size
    file_block_size = 512
    
    # maximum number of ADC words in the buffer
    max_ADC_words_per_buffer = 254
    
    # create arrays to hold the data buffer's ADC data.
    # bytes...
    ADC_data_array_bytes = np.empty(2 * max_ADC_words_per_buffer, dtype=int)
    # two-byte words...
    ADC_data_array = np.empty(max_ADC_words_per_buffer, dtype=int)
    
    #create an array to hold all the data we read for the user
    ADC_all_the_data_array = \
    np.empty(max_buffers_to_read * max_ADC_words_per_buffer, dtype=int)
    
    # initialize the number of ADC digitizations read so far
    ADC_digitizations_read_so_far = 0
     
    ######################### read the file's header block #########################
    
    # read the four-byte ADC clock frequency from the header.
    ADC_clock_frequency_bytes = audio_file.read(4)
    
    # unpack the bytes: "<" means "little endian" (low byte comes before high byte)
    # and "I" means four bytes. Note that struct.unpack always returns an array, 
    # even if it is of unit length, so I need to put [0] at the end to get an 
    # integer from the unit-length array.
    ADC_clock_frequency = struct.unpack("<I", ADC_clock_frequency_bytes)[0]
    
    # inform the user...
    print("ADC clock frequency (kHz) ", ADC_clock_frequency / 1000)
    
    # read the four-byte CPU clock frequency from the header. Arduino Mega 2560 
    # has a 16 MHz clock.
    CPU_clock_frequency_bytes = audio_file.read(4)
    CPU_clock_frequency = struct.unpack("<I", CPU_clock_frequency_bytes)[0]
    print("CPU clock frequency (kHz) ", CPU_clock_frequency / 1000)
    
    # read the sample interval in CPU cycles. Should be about 16 MHz / 32 kHz = 500.
    sample_interval_bytes = audio_file.read(4)
    sample_interval = struct.unpack("<I", sample_interval_bytes)[0]
    print("ADC sample interval in CPU cycles ", sample_interval)
    
    # read (and ignore) the ADC data word size (2 bytes) and number of pins used (1).
    audio_file.read(8)
    
    #read the first pin number. (Should be 7!)
    ADC_pin_bytes = audio_file.read(4)
    ADC_pin = struct.unpack("<I", ADC_pin_bytes)[0]
    print("Arduino ADC analog pin recorded ", ADC_pin)
    
    # now read (and ignore) the remaining 488 bytes of the header.
    audio_file.read(file_block_size - 24)
    
    ############################ read blocks of ADC data ###########################
    
    for buffer_index in range(0, max_buffers_to_read):
    
        ########################### read an ADC data block #########################
        
        # read the number of ADC data words in this block
        ADC_words_this_block_bytes = audio_file.read(2)
        
        # check that we got something that wasn't of zero length, which indicates
        # the end of the file
        if len(ADC_words_this_block_bytes) <= 0:
            print("Hit end of file, so exit the ADC data reading loop")
            break
        
        # convert (little endian) bytes to an integer
        ADC_words_this_block = struct.unpack("<H", ADC_words_this_block_bytes)[0]
    
        # print, if we want to...
        # print("ADC words this block: ", ADC_words_this_block)
    
        # do the same for the data buffer overrun count (whatever that means!)
        # data_overruns_bytes = audio_file.read(2)
        # data_overruns = struct.unpack("<H", data_overruns_bytes)[0]
        audio_file.read(2)
        
        # now read from the file, loading the ADC data in the rest of this block
        # into an array.
        ADC_data_array_bytes = audio_file.read(2 * ADC_words_this_block)
    
        # check that we got something that wasn't of zero length, which would 
        # indicate the end of the file
        if len(ADC_data_array_bytes) <= 0:
            print("Premature end of this data block, so look for the next block")
            break
        
        # unpack into a two-byte integer array. See //stackoverflow.com/questions/
        # 45187101/converting-bytearray-to-short-int-in-python
        ADC_data_array = \
        struct.unpack('<'+'H'*(len(ADC_data_array_bytes)//2), ADC_data_array_bytes)
        
        # inject this array into the big array ADC_all_the_data_array
        i_first = int(ADC_digitizations_read_so_far)
        i_last = i_first + len(ADC_data_array)
        
        # np.copyto(destination, source). Note that index range does NOT include
        # the upper end point.
        np.copyto(ADC_all_the_data_array[i_first : i_last], ADC_data_array[:])
    
        # increment the samples-read count
        ADC_digitizations_read_so_far += len(ADC_data_array_bytes)/2
        
        # print, if we want to...
        # print("ADC_data_array\n", ADC_data_array)
    
        ######################## done with this data block #########################
    
    ########################### all done reading ADC data ##########################
        
    # for improved readability, get versions of a few BIG numbers formatted to 
    # include commas separating thousands.
    buffer_index_string = locale.format("%d", buffer_index, grouping=True)
    
    ADC_digitizations_read_so_far_string = \
    locale.format("%d", ADC_digitizations_read_so_far, grouping=True)
    
    print("\nAll done. ADC data buffers read: ", buffer_index_string)
    print("ADC digitizations read: ", ADC_digitizations_read_so_far_string)
    
    print("this corresponds to ", ADC_digitizations_read_so_far / 32000. / 60., \
    " minutes of recording")

    # now close the audio file.
    audio_file.close()

    # return ADC_all_the_data_array[0 : int(ADC_digitizations_read_so_far - 1)]
    return ADC_all_the_data_array[0 : int(ADC_digitizations_read_so_far)]
    
