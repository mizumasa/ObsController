#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import copy
import numpy as np
import cv2

class WINDOW_EASER:
    def __init__(self,w,h):
        self.canvas = np.zeros((h,w,3),dtype=np.uint8)
        self.w = w
        self.h = h
    def update(self):
        self.t += 1
        self.frames = self.getFrames()
        return self.frames

def main():
    w = WINDOW_EASER(100,100)
    w.setWindow("f1")
    w.setKeyFrame("f1",10,[0,0,1,1])
    w.setKeyFrame("f1",20,[0.25,0.25,0.5,0.5])
    w.setKeyFrame("f1",30,[0.25,0.25,0.5,0.5])
    w.setKeyFrame("f1",40,[0,0,0.5,0.5])
    w.setKeyFrame("f1",50,[0,0,0.5,0.5])
    w.setKeyFrame("f1",60,[0.5,0,0.5,0.5])
    w.setKeyFrame("f1",70,[0,0,1,1])
    w.setupKeyFrame()
    while 1:
        for i in range(80):
            print "=====================",i
            print w.update()
            frame = w.draw()
            cv2.imshow("window",frame)
            cv2.waitKey(1)
        w.initKeyFrame()

if __name__ == "__main__":
    main()
