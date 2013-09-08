HBBR_Scanner
============

3D Laser Scanner software with Kivy based multi-platform GUI in python.

### Supported Platforms
+ Linux - PC Ubuntu, Raspberry Pi
+ Windows
+ OS X

### Depends on:
+ Kivy
+ OpenCV with python bindings

### Supported hardware
+ FabScan100 style turntable
+ USB webcam


Scan methods
------------

### Single Laser Scan with Background Subtraction

Scan files produced for a full or partial scan with laser detection and a sequnce of images with laser on and off.


    image.json
    image_laser_on.png
    image_laser_off.png
    image_diff.png
    image_thresh.png
    image_hough.png
    image_00000_laser_on.png
    image_00000_laser_off.png
    image_00001_laser_on.png
    image_00002_laser_off.png
    image_00003_laser_on.png
    image_00003_laser_off.png
    ...
    image_NNNNN_laser_on.png
    image_NNNNN_laser_off.png


