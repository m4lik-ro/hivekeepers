import pyaudio
import wave
import socket
from datetime import datetime
import sys
import os
import argparse
from scipy.fftpack import rfft
import numpy as np
from scipy.io import wavfile as wav


FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = socket.gethostname() + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".wav"

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

def perform_FFT(_filename, _upper_freq = 4000):

    Fs, data = wav.read(_filename)
    N = len(data)           # Number of sample points
    T = 1.0 / Fs            # sample spacing
    upper_cutoff = int(_upper_freq / (Fs / N) * 2)
    channels = len(data.shape)

    print ('Data type          :', data.dtype)
    if data.dtype == 'int16':
        data = data / 32767     # 16bit int to -1,1    

    print ('Sampling frequency :', Fs, 'Hz')
    print ('Sample length      :', len(data), 'seconds')
    print ('Audio channels     :', channels)

    if channels == 2:
        data = data.sum(axis=1) / 2

    print ('Audio length       :', '{:0.3f}'.format(N / Fs), 'seconds')

    # perform FFT
    xf = np.linspace(0.0, 1.0/(2.0*T), N)
    yf = 2*abs(rfft(data))/N

    return (xf, yf, upper_cutoff)

def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
        
def saveToImage(_xf, _yf, _upper_cutoff, _filename, _title="FFT"):
    # set up graphics screen to plots
    import matplotlib.pyplot as plt
    
    plt.figure(num=None, figsize=(16, 6), dpi=100)
    plt.title (_title)
    plt.ylim(0, 0.1)
    plt.plot(_xf[:_upper_cutoff], _yf[:_upper_cutoff])
    plt.grid()
    plt.savefig(_filename)
#    plt.show()

def sendWavViaFTP(_outputdir, _filename):
    import pysftp
    with pysftp.Connection (host='45.76.113.79', username='ftpuser') as sftp:
       sftp.put (_outputdir + _filename, '/home/ftpuser/ftp/files/' + _filename)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-s", "--sample", help="set the audio sample rate")
    parser.add_argument("-d", "--device", help="audio device index (default 2)")
    parser.add_argument("-t", "--time", help="sample time in seconds (default 5)")
    parser.add_argument("-o", "--outputdir", help="output directory (default is current)")
    parser.add_argument("-r", "--removewav", help="delete the wav file when finished (default is true)", action="store_true")
    parser.add_argument("-f", "--ftp", help="send file to server via FTP (default is false)", action="store_true")
    parser.add_argument("-l", "--list", help="list available audio devices", action="store_true")
    
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
    
    # perform thh FFT
    (xf, yf, upper_cutoff) = perform_FFT(outputdir + WAVE_OUTPUT_FILENAME)
    
    # create an image and save to disk
    # get the next available image sequence
    i=1
    while os.path.exists(outputdir + "img%s.png" % i):
        i += 1
    filename = "img%s.png" % i
    title = WAVE_OUTPUT_FILENAME.split('.')[0][:-2]     # remove .wav & seconds
    saveToImage(xf, yf, upper_cutoff, outputdir + filename, title)

    # send the file to the server if needed
    if sendWithFTP:
        sendWavViaFTP(outputdir, WAVE_OUTPUT_FILENAME)

    # delete the wav if not needed
    if removewav:
        os.remove(outputdir + WAVE_OUTPUT_FILENAME)
    
    
    
if __name__ == "__main__":
   main()