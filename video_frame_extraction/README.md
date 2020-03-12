Shoot videos, extract frames, train your Machine Learning model.

###Install
- Download FFMPEG (https://ffmpeg.org/download.html)
- Extract /bin/ffmpeg.exe (you don't need the rest)

###Run
- Open cmd prompt where you extracted ffmpeg.exe
- > .\ffmpeg -i IMG_0066.MOV -r 60/1 $filename%04d.jpg
    - IMG_0066.MOV: name of video file
    - 60/1: 1 second of video = 60 images
    - %04d: uses 4 numbers for file name, appends 0s in front
