#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import peakutils
import pyaudio
import wave
import socket
from datetime import datetime
import sys
import os
import argparse
from scipy.fftpack import rfft
from scipy.io import wavfile as wav
import matplotlib.pyplot as plt


plt.close('all')

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = socket.gethostname() + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".wav"
Y_AXIS_MAX = 5000


def get_audio_device():
    audio = pyaudio.PyAudio()
    print("----------------------record device list---------------------")
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            if ("UAC 1.0 Microphone" in audio.get_device_info_by_host_api_device_index(0, i).get('name')):
                return i
    return None

def grab_audio(_filename, _device_index, _sample_rate, _record_seconds):
    audio = pyaudio.PyAudio()

    print("recording via device_index "+str(_device_index))

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=_sample_rate, input=True,input_device_index = _device_index,
                    frames_per_buffer=CHUNK)
    print ("recording started")
    Recordframes = []
     
    for i in range(0, int(_sample_rate / CHUNK * _record_seconds)):
        data = stream.read(CHUNK)
        Recordframes.append(data)
    print ("recording stopped")
     
    stream.stop_stream()
    stream.close()
    audio.terminate()
     
    waveFile = wave.open(_filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(_sample_rate)
    waveFile.writeframes(b''.join(Recordframes))
    waveFile.close()

def printAudioDevices():
    audio = pyaudio.PyAudio()
    print("----------------------record device list---------------------")
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
        
def saveToImage(freq, s_mag, s_db, _upper_cutoff, _filename, _title="FFT"):
    
    plt.figure(num=None, figsize=(20, 12), dpi=100)
#    plt.title (_title)
    
    ax1 = plt.subplot(211, xlabel='Frequency [Hz]', ylabel='Amplitude [scaled]', title=_title, xlim=(0,_upper_cutoff), ylim=(0,1.1))
    ax1.plot(freq, s_mag, 'r')
    ax1.grid(True)
    peaks = peakutils.indexes(s_mag, thres=0.1, min_dist=10)    # find the peaks
    print ('s_mag peaks:', peaks)
    for peak in peaks:
        s = str(round(freq[peak]))[:-2]
        ax1.annotate(s, [freq[peak], s_mag[peak]], xytext=[freq[peak]-45, s_mag[peak]+0.025])
        print (freq[peak], s_db[peak])

    ax2 = plt.subplot(212, xlabel='Frequency [Hz]', ylabel='Amplitude [dB]', xlim= (0,_upper_cutoff), ylim=(-60,100))
    ax2.plot(freq, s_db, 'b')
    ax2.grid(True)
    peaks = peakutils.indexes(s_db, thres=0, min_dist=50)    # find the peaks
    peaks=peaks[:3]
    print ('s_db peaks:', peaks)
    for peak in peaks:
        s = str(round(freq[peak]))[:-2]
        ax2.annotate(s, [freq[peak], s_db[peak]], xytext=[freq[peak]-45, s_db[peak]+5])
        print (freq[peak], s_db[peak])

#    plt.show()
    plt.savefig(_filename)



def sendToFTPServer(_outputdir, _filename):
    import pysftp
    with pysftp.Connection (host='45.76.113.79', username='ftpuser') as sftp:
        print ("Sending %s to FTP server" % _filename)
        sftp.put (_outputdir + _filename, '/home/ftpuser/ftp/files/' + _filename)
        print ("FTP transfer complete")



def dbfft(x, fs, win=None, ref=32768):
    """
    Calculate spectrum in dB scale
    Args:
        x: input signal
        fs: sampling frequency
        win: vector containing window samples (same length as x).
             If not provided, then rectangular window is used by default.
        ref: reference value used for dBFS scale. 32768 for int16 and 1 for float

    Returns:
        freq: frequency vector
        s_db: spectrum in dB scale
    """

    N = len(x)  # Length of input sequence

    if win is None:
        win = np.ones(N)
    if len(x) != len(win):
            raise ValueError('Signal and window must be of the same length')
    x = x * win

    # Calculate real FFT and frequency vector
    sp = np.fft.rfft(x)
    freq = np.arange((N / 2) + 1) / (float(N) / fs)

    # Scale the magnitude of FFT by window and factor of 2,
    # because we are using half of FFT spectrum.
    s_mag = np.abs(sp) * 2 / np.sum(win)    

    # Convert to dBFS
    s_dbfs = 20 * np.log10(s_mag / ref)

    return freq, s_mag/max(s_mag), s_dbfs


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-s", "--sample", help="set the audio sample rate")
    parser.add_argument("-d", "--device", help="audio device index (default 2)")
    parser.add_argument("-t", "--time", help="sample time in seconds (default 5)")
    parser.add_argument("-o", "--outputdir", help="output directory (default is current)")
    parser.add_argument("-r", "--removewav", help="delete the wav file when finished (default is true)", action="store_true")
    parser.add_argument("-f", "--ftp", help="send file to server via FTP (default is false)", action="store_true")
    parser.add_argument("-ll", "--list", help="list available audio devices", action="store_true")
    
    args = parser.parse_args()

    # Check for --version or -V
    if args.version:
        logger.debug("Mic -> FFT -> Image - version 0.1")
        
    # set defaults
    sample_rate = int(args.sample if args.sample else 44100)
    audio_index = int(args.device if args.device else get_audio_device())
    record_seconds = int(args.time if args.time else 5)
    outputdir = args.outputdir if args.outputdir else './'
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    removewav = True if args.removewav else False
    sendWithFTP = True if args.ftp else False
    if args.list:
        printAudioDevices()
        sys.exit(0)
    

    ######################################
    # start processing
    ######################################
    
    # grab the audio
    grab_audio(outputdir + WAVE_OUTPUT_FILENAME, audio_index, sample_rate, record_seconds)
    fs, signal = wav.read(outputdir + WAVE_OUTPUT_FILENAME)
    #fs, signal = wav.read('Sine_440hz_0dB_10seconds_44.1khz_16bit_mono.wav')

    print ('Data type          :', signal.dtype)
    print ('Sampling frequency :', fs, 'Hz')
    print ('Sample length      :', len(signal), 'samples')
    print ('Audio channels     :', CHANNELS)
    print ('Audio length       :', '{:0.3f}'.format(len(signal) / fs), 'seconds')


    # Take slice
    N = 8192
    win = np.hamming(N)
    freq, s_mag, s_dbfs = dbfft(signal[0:N], fs, win)

    # Scale from dBFS to dB
    K = 78  # from microphone datasheet
    s_db = s_dbfs + K
       
    # create an image and save to disk
    # get the next available image sequence
    i=1
    while os.path.exists(outputdir + socket.gethostname() + "_" + "img%s.png" % i):
        i += 1
    filename = socket.gethostname() + "_" + "img%s.png" % i
    title = WAVE_OUTPUT_FILENAME.split('.')[0][:-2]     # remove .wav & seconds
    saveToImage(freq, s_mag, s_db, Y_AXIS_MAX, outputdir + filename, title)

    # send the file to the server if needed
    if sendWithFTP:
        sendToFTPServer(outputdir, WAVE_OUTPUT_FILENAME)
        sendToFTPServer(outputdir, filename)

    # delete the wav if not needed
    if removewav:
        os.remove(outputdir + WAVE_OUTPUT_FILENAME)    
    
    
if __name__ == "__main__":
   main()