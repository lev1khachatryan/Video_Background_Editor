# A small video background editor that allows to substitute background of one video to another

The program allows to specify video files (local paths to the data) through the config.INI configuration file.

Please notice that the videos should have non-moving backgrounds, meaning that the camera used to shoot the videos is fixed on the wall or somewhere else.

The program consists of the following steps:

    1. Background subtraction from video.
    2. Moving objects subtraction from video.
    3. Change background in video.

## Background subtraction from video

We can assume most of the time, every pixel sees the same piece of the background because the camera is not moving. Occasionally, moving object comes in the front and obscure the background. For a video sequence, we can randomly sample a few frames (say 25 frames) per second. So, for every pixel, we now have 25 values of the background. As long as a pixel is not covered by a moving object more than 50% of the time, the median of the pixel over these frames will give a good estimate of the background at that pixel.

