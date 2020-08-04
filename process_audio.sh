if [ $(date +%M) = 00 ] || [ $(date +%M) = 15 ] || [ $(date +%M) = 30 ] || [ $(date +%M) = 45 ]
then
python3 /home/pi/hivekeepers/wav2fft2img.py -t 50 -o /home/pi/hivekeepers/fftimages/ -r -f
exit
fi
python3 /home/pi/hivekeepers/wav2fft2img.py -t 50 -o /home/pi/hivekeepers/fftimages/ -r