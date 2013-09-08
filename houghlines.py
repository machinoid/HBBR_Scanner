#!/usr/bin/python
# This is a standalone program. Pass an image name as a first parameter of the program.

import sys
from math import sin, cos, sqrt, pi
import cv2.cv as cv

import scan_settings

# picks green?
#RED_MIN = cv.Scalar(10,  50, 50)
#RED_MAX = cv.Scalar(30, 255, 255)

# these work but do not make sense
RED_MIN = cv.Scalar(110,  50, 50)
RED_MAX = cv.Scalar(140, 255, 255)

#http://stackoverflow.com/questions/12204522/efficiently-threshold-red-using-hsv-in-opencv
#You can calculate Hue channel in range 0..255 with CV_BGR2HSV_FULL. Your original hue difference of 10 #will become 14 (10/180*256), i.e. the hue must be in range 128-14..128+14:

#cvCvtColor(imageBgr, imageHsv, CV_BGR2HSV_FULL);
#int rotation = 128 - 255; // 255 = red
#cvAddS(imageHsv, cvScalar(rotation, 0, 0), imageHsv);
#cvInRangeS(imageHsv, cvScalar(114, 135, 135), cvScalar(142, 255, 255), dst);



# toggle between CV_HOUGH_STANDARD and CV_HOUGH_PROBABILISTIC
USE_STANDARD = False
#USE_STANDARD = True

show = False
#show = True

settings={}
laser_lines=[]



if __name__ == "__main__":
    if len(sys.argv) > 1:
      filename = sys.argv[1]
    else:
     filename = "image"

    try:
       src1 = cv.LoadImage(filename+"_laser_on.png", cv.CV_LOAD_IMAGE_GRAYSCALE)
       src2 = cv.LoadImage(filename+"_laser_on.png", cv.CV_LOAD_IMAGE_COLOR)
       src3 = cv.LoadImage(filename+"_laser_off.png", cv.CV_LOAD_IMAGE_GRAYSCALE)
       src4 = cv.LoadImage(filename+"_laser_off.png", cv.CV_LOAD_IMAGE_COLOR)
    except:
        print("need some file!");
        sys.exit(-1);

    print("before load")    
    print(str(settings))
    settings = scan_settings.load(filename)
    print("after load")    
    print(str(settings['laser']))
    print(str(settings))

    print("get lines")
    try:
        print(str(settings))
        laser_lines = settings['laser']['lines']
        del settings['laser']['lines']
    except:
        print("except")
        print(str(settings))
        settings['laser']['lines']=[]
        laser_lines = settings['laser']['lines']
        print("no laser lines not found in settings!");

    print(str(settings))


    # do color thresholding
    src_hsv = cv.CreateImage(cv.GetSize(src2), 8, 3)
    src_diff = cv.CreateImage(cv.GetSize(src2), 8, 3)
    src     = cv.CreateImage(cv.GetSize(src2), 8, 1)
#    red     = cv.CreateImage(cv.GetSize(src2), 8, 1)
#    redT    = cv.CreateImage(cv.GetSize(src2), 8, 1)
#    green   = cv.CreateImage(cv.GetSize(src2), 8, 1)
#    blue    = cv.CreateImage(cv.GetSize(src2), 8, 1)
#    cv.Split(src2, red, green, blue, None);
#    cv.Threshold(red, redT, 20, 255, cv.CV_THRESH_BINARY);

    cv.Sub(src2,src4,src_diff);
    cv.CvtColor(src_diff, src_hsv, cv.CV_RGB2HSV); #CV_BGR2HSV_FULL
    cv.InRangeS(src_hsv, RED_MIN, RED_MAX, src);

#    cv.NamedWindow("Red", 1)
#    cv.NamedWindow("Green", 1)
#    cv.NamedWindow("Blue", 1)
#    cv.NamedWindow("RedT", 1)

#    cv.ShowImage("RedT", redT)
#    cv.ShowImage("Red", red)
#    cv.ShowImage("Green", green)
#    cv.ShowImage("Blue", blue)

#    k = cv.WaitKey(0) % 0x100
#    if k == 27:
#        cv.DestroyAllWindows()
#        sys.exit(-1)


    if show:
       cv.NamedWindow("Diff", 1)
       cv.NamedWindow("Hsv", 1)
       cv.NamedWindow("Thr", 1)

       cv.ShowImage("Diff", src_diff)
       cv.ShowImage("Hsv", src_hsv)
       cv.ShowImage("Thr", src)

       k = cv.WaitKey(0) % 0x100
       if k == 27:
           cv.DestroyAllWindows()
           sys.exit(-1)

       cv.NamedWindow("Source", 1)
       cv.NamedWindow("Hough", 1)

    while True:
        dst = cv.CreateImage(cv.GetSize(src), 8, 1)
        color_dst = cv.CreateImage(cv.GetSize(src), 8, 3)
        storage = cv.CreateMemStorage(0)
        lines = 0
        cv.Canny(src, dst, 50, 200, 3)
        cv.CvtColor(dst, color_dst, cv.CV_GRAY2BGR)

        if USE_STANDARD:
            lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_STANDARD, 1, pi / 180, 100, 0, 0)
            for (rho, theta) in lines[:100]:
                a = cos(theta)
                b = sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (cv.Round(x0 + 1000*(-b)), cv.Round(y0 + 1000*(a)))
                pt2 = (cv.Round(x0 - 1000*(-b)), cv.Round(y0 - 1000*(a)))
                cv.Line(color_dst, pt1, pt2, cv.RGB(255, 0, 0), 3, 8)
                print('detected line at('+str(x0)+','+str(y0)+')')
                print('('+str(pt1)+','+str(pt2)+')')
        else:
            deltaRho = float(1)
            deltaTheta = float(pi/2)
            minVote = 20
            minLength = 50
            maxGap = 10
            settings['laser']['lines']=[]

            lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_PROBABILISTIC, deltaRho, deltaTheta, minVote, minLength, maxGap)
#            lines = cv.HoughLines2(dst, storage, cv.CV_HOUGH_PROBABILISTIC, 1, pi / 180, 50, 50, 10)
            for line in lines:
                cv.Line(color_dst, line[0], line[1], cv.CV_RGB(255, 0, 0), 3, 8)
                print('detected line at('+str(line[0])+','+str(line[1])+')')
                settings['laser']['lines'].append([line[0], line[1]])
        if show:
           cv.ShowImage("Source", src)
           cv.ShowImage("Hough", color_dst)

           k = cv.WaitKey(0) % 0x100
           if k == ord(' '):
              USE_STANDARD = not USE_STANDARD
           if k == 27:
              break
        else:
            break

    cv.ShowImage("Source", src)
    cv.ShowImage("Hough", color_dst)

    k = cv.WaitKey(0) % 0x100
#    if k == 27:
#        break

    print(str(settings))
    scan_settings.store(filename, settings)
    cv.SaveImage(filename+"_diff.png", src_diff)
    cv.SaveImage(filename+"_thresh.png", src)
    cv.SaveImage(filename+"_hough.png", color_dst)
    cv.DestroyAllWindows()
