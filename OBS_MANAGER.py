#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import copy
import numpy as np
import cv2
from obswebsocket import obsws, requests
#pip install obs-websocket-py
#conda install -c conda-forge kivy

host = "localhost"
port = 4444
password = "secret"

class PROPERTIES:
    def __init__(self,d):
        self.sourceHeight = d["sourceHeight"]
        self.sourceWidth = d["sourceWidth"]
        print(self.sourceHeight,self.sourceWidth)
    def getScale(self,drawHeight):
        return 1.0 * drawHeight / self.sourceHeight

class OBS_MANAGER:
    def __init__(self):
        self.ws = obsws(host, port, password)
        self.ws.connect()
        self.data = None
        self.scenes = None
        self.messageid = 0
        self.controlCount = {}
        return
    def getScenes(self):
        ret = self.ws.call(requests.GetCurrentScene())
        #print("current scene : ",ret.getName())
        ret = self.ws.call(requests.GetSceneList())
        #print("scene list : ",ret.datain)
        self.data = ret.datain
        self.scenes = self.data["scenes"]
        self.keyScenes = getKeyScenes(self.scenes)
        return
    def switchScene(self,sceneName):
        self.ws.call(requests.SetCurrentScene(sceneName))
    def updateScene(self,sceneName,sceneId,speed = 50):
        self.speed = speed
        currentScene = self.ws.call(requests.GetCurrentScene())
        currentSceneName = currentScene.getName()
        self.currentSceneName = currentSceneName
        currentSceneData = currentScene.datain
        print(currentSceneName)
        if currentSceneName in self.keyScenes and sceneName == currentSceneName:
            destSceneName = getSceneName(currentSceneName,sceneId)
            destScene = getSceneFromName(self.scenes,destSceneName)
            #print(destScene)
            if destScene is not None:
                self.setDest(currentSceneData,destScene,speed)
            
            #self.updateToEnd()
            
        return
    
    def update(self):
        #bUpdate = False
        for srcName in self.controlCount.keys():
            if self.controlCount[srcName] > 0 and srcName in self.route.keys():
                #bUpdate = True
                i = self.speed - self.controlCount[srcName]
                self.controlCount[srcName] -= 1
                scale = 1.0 * self.route[srcName]["cx"][i] / self.route[srcName]["source_cx"][i]
                data = requests.SetSceneItemTransform(srcName,scale,scale,0).data()
                data["message-id"] = self.messageid
                self.messageid += 1
                self.ws.ws.send(json.dumps(data))
                data = requests.SetSceneItemPosition(srcName,self.route[srcName]["x"][i],self.route[srcName]["y"][i]).data()
                data["message-id"] = self.messageid
                self.messageid += 1
                self.ws.ws.send(json.dumps(data))
                data = requests.SetCurrentScene(self.currentSceneName).data()
                data["message-id"] = self.messageid
                self.messageid += 1
                self.ws.ws.send(json.dumps(data))
        time.sleep(0.02)
        return

    def setDest(self,currentScene,destScene,speed):
        #print("=========================")
        #print currentScene
        #print("=========================")
        #print destScene
        #print("=========================")
        self.route = makeRoute(currentScene,destScene,{"divNum":speed})
        for i in self.route.keys():
            self.controlCount[i] = speed

    def updateToEnd(self):
        for i in range(50):
            for srcName in self.route.keys():
                scale = 1.0 * self.route[srcName]["cx"][i] / self.route[srcName]["source_cx"][i]
                data = requests.SetSceneItemTransform(srcName,scale,scale,0).data()
                data["message-id"] = self.messageid
                self.messageid += 1
                self.ws.ws.send(json.dumps(data))
                data = requests.SetSceneItemPosition(srcName,self.route[srcName]["x"][i],self.route[srcName]["y"][i]).data()
                data["message-id"] = self.messageid
                self.messageid += 1
                self.ws.ws.send(json.dumps(data))
            time.sleep(0.01)
        return


def makeRoute(currentScene,destScene,info):
    destSources = destScene["sources"]
    currentSources = currentScene["sources"]
    routeData = {}
    for i in destSources:
        for j in currentSources:
            if i["name"] == j["name"]:
                ret, value = makeRouteSource(j,i,info["divNum"])
                if ret:
                    routeData[i["name"]] = value
    return routeData

def makeRouteSource(cur,dst,divNum):
    out = {}
    params = [u'cx',u'cy',u'source_cx',u'source_cy',u'x',u'y']
    diff = False
    for param in params:
        if cur[param] != dst[param]:
            diff = True
        out[param] = makeDiv(cur[param],dst[param],divNum,2.0)
    return diff, out

def makeDiv(st,en,divNum,ease=2.0):
    if ease != 1.0:
        return np.arange(divNum) ** (1./ease) * (divNum**(1./ease)) * (en - st) / (divNum-1) + st
    else:
        return np.arange(divNum) * 1.0 * (en - st) / (divNum-1) + st


def getKeyScenes(scenes):
    KeyScenes = []
    for i in scenes:
        if isKeyScene(i["name"]):
            KeyScenes.append(i["name"])
    return KeyScenes

def getSceneFromName(scenes,name):
    for i in scenes:
        if name == i["name"]:
            return i
    return None


def isKeyScene(name):
    return name[-2:] == "_0"

def getSceneName(name,sceneId):
    return name.replace("_0","_"+str(sceneId))

def main():
    m = OBS_MANAGER()
    m.getScenes()
    for i in range(3):
        #m.updateScene(1)
        #m.updateScene(2)
        #m.updateScene(3)
        pass
    pass

if __name__ == "__main__":
    main()
