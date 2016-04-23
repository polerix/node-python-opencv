#!/usr/bin/env python

"""face-detection.py: Face detection using openCV."""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2015 Aldux.net"

__license__ = "GPL"
__version__ = "1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"

import sys
import cv, os, csv
import numpy as np
min_size = (20, 20)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0
lastcascadefile = ''
loaded = False
cascade = None

from os.path import isfile
lastCSVFile = ''
trained = False
recognizer = None
names = None

class FaceDetection:
    @staticmethod
    def findFrame(img, haarcascade, scaleFactor = 1.2, minNeighbors = 2):
        global loaded, lastcascadefile, cascade

        if (haarcascade <> lastcascadefile):
            loaded = False

        if (loaded == False):
                loaded = True
                print haarcascade
                cascade = cv.Load(haarcascade)
                lastcascadefile = haarcascade


        # allocate temporary images
        gray = cv.CreateImage((img.width,img.height), 8, 1)
        small_img = cv.CreateImage((cv.Round(img.width / image_scale),
                               cv.Round (img.height / image_scale)), 8, 1)

        # convert color input image to grayscale
        cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

        # scale input image for faster processing
        cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

        cv.EqualizeHist(small_img, small_img)
        faces = None
        if(cascade):
            t = cv.GetTickCount()
            faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),
                                     haar_scale, min_neighbors, haar_flags, min_size)
            t = cv.GetTickCount() - t
            print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
            if faces:
                    print "found faces"
                    for ((x, y, w, h), n) in faces:
                            # the input to cv.HaarDetectObjects was resized, so scale the
                            # bounding box of each face and convert it to two CvPoints
                            pt1 = (int(x * image_scale), int(y * image_scale))
                            pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                            cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
                            print "x= "+str(x)+" y= "+str(y)+" w= "+str(w)+" h= "+str(h)
        cv.ShowImage("Face detection", img)
        return faces
