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
        self.keyPoints = {}
        self.t = 0
        self.frames = None
    def setWindow(self,name):
        self.keyPoints[name]=[[]]
    def setKeyFrame(self,name,t,data):
        if name not in self.keyPoints.keys():
            self.setWindow(name)
        self.keyPoints[name][0].append([t,np.asarray(data,dtype=np.float)])
    def setupKeyFrame(self):
        self.keyPointsOri = {}
        for name in self.keyPoints.keys():
            self.keyPointsOri[name] = copy.copy(self.keyPoints[name])
    def initKeyFrame(self):
        for name in self.keyPoints.keys():
            self.keyPoints[name] = copy.copy(self.keyPointsOri[name])
        self.t = 0
    def setFramePos(self,t):
        self.t = t
    def update(self):
        self.t += 1
        self.frames = self.getFrames()
        return self.frames
    def draw(self):
        self.canvas *= 0
        if self.frames is not None:
            for i,j in enumerate(self.frames.keys()):
                d = self.frames[j].astype(np.int)
                cv2.rectangle(self.canvas, (d[0],d[1]), (d[0]+d[2],d[1]+d[3]), (i*10, 255, 255), -1)
        return self.canvas
    def getFrames(self):
        out = {}
        for key in self.keyPoints.keys():
            out[key] = self.scale(self.getFrame(key))
        return out
    def getFrame(self,name):
        return getFrame(self.t,self.keyPoints[name])
    def scale(self,d):
        return np.asarray([self.w*d[0], self.h*d[1], self.w*d[2], self.h*d[3]])

def getFrame(t,timeline):
    #print len(timeline[0])
    if len(timeline[0]) <= 1:
        if len(timeline[0]) == 1:
            return timeline[0][0][1]
        else:
            return None
    t0 = timeline[0][0][0]
    t1 = timeline[0][1][0]
    if t <= t0:
        return timeline[0][0][1]
    elif t == t1:
        timeline[0] = timeline[0][1:]
        return timeline[0][0][1]
    else:
        return merge(t,t0,t1,timeline[0][0][1],timeline[0][1][1])

def merge(t,t0,t1,d0,d1):
    return (d0 * (t1-t) + d1 * (t-t0)) / (t1-t0)

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
