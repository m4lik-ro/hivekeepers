ffmpeg -r 5 -start_number 1 -i fftimages/img%d.png -c:v libx264 -vf "fps=25,format=yuv420p" ./out.mp4 -y
