Shoot videos, extract frames, train your Machine Learning model.

###Install

- Download FFMPEG (https://ffmpeg.org/download.html)
- Extract /bin/ffmpeg.exe (you don't need the rest) to the same folder as extractor.bat

###Run

- Drag & drop video files on extractor.bat file
    - The script will create a folder named after the video
    - The folder will be in the same location as the video
    - The images will be extracted to that folder

###Config

- The script can not be configured, so it must be edited instead
- Look for the line that contains "ffmpeg"
    - -r: framerate
        - 60/1 -> 1 second of video produces 60 frames
    - %%04d: How the frames will be named -> 4 numbers with leading zeroes
