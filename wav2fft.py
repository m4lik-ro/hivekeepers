import pyaudio
import wave
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recordedFile.wav"
device_index = 2
audio = pyaudio.PyAudio()

print("----------------------record device list---------------------")
info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

print("-------------------------------------------------------------")

index = int(input())
print("recording via index "+str(index))

stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index = index,
                frames_per_buffer=CHUNK)
print ("recording started")
Recordframes = []
 
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    Recordframes.append(data)
print ("recording stopped")
 
stream.stop_stream()
stream.close()
audio.terminate()
 
waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(Recordframes))
waveFile.close()



from scipy.fftpack import rfft
import numpy as np
from scipy.io import wavfile as wav

Fs, data = wav.read(WAVE_OUTPUT_FILENAME)
upper_freq = 4000


#data = data[:2000]

#N = 1000               # Number of sample points
#T = 1.0 / 1000.0       # sample spacing

N = len(data)           # Number of sample points
T = 1.0 / Fs            # sample spacing
upper_cutoff = int(upper_freq / (Fs / N) * 2)
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


#x = np.linspace(0.0, N*T, N//2)
#y = np.sin(50.0 * 2.0*np.pi*x) + 0.5*np.sin(80.0 * 2.0*np.pi*x)

# set up graphics screen to plots
import matplotlib.pyplot as plt
fig, (ax1, ax2, ax3) = plt.subplots(3)
fig.suptitle ('FFT testing')


# x,y data of the input file
y = data
x = np.linspace (0.0, N*T, len(y))
ax1.plot(x, y)
ax1.grid()



# FFT plot
xf = np.linspace(0.0, 1.0/(2.0*T), N)
yf = 2*abs(rfft(data))/N
ax2.plot(xf[:upper_cutoff], yf[:upper_cutoff])
ax2.grid()

# dft plot
xf = np.linspace(0.0, 1.0/(2.0*T), N)
yf = 10.*np.log10(yf)   # scale to dB
ax3.plot(xf[:upper_cutoff], yf[:upper_cutoff])
ax3.grid()

#x = np.linspace (1, 10, 100, True)
#y = x
#ax3.bar(x, y)

plt.show()