#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import copy
import numpy as np
import cv2
from obswebsocket import obsws, requests

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
    def updateScene(self,sceneId):
        currentScene = self.ws.call(requests.GetCurrentScene())
        currentSceneName = currentScene.getName()
        currentSceneData = currentScene.datain
        print(currentSceneName)
        if currentSceneName in self.keyScenes:
            destSceneName = getSceneName(currentSceneName,sceneId)
            destScene = getSceneFromName(self.scenes,destSceneName)
            #print(destScene)
            self.setDest(currentSceneData,destScene)
            self.updateToEnd()
        return

    def setDest(self,currentScene,destScene):
        #print("=========================")
        #print currentScene
        #print("=========================")
        #print destScene
        #print("=========================")
        self.route = makeRoute(currentScene,destScene,{"divNum":100})

    def updateToEnd(self):
        for i in range(100):
            print(i)
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
                routeData[i["name"]] = makeRouteSource(j,i,info["divNum"])
    return routeData

def makeRouteSource(cur,dst,divNum):
    out = {}
    params = [u'cx',u'cy',u'source_cx',u'source_cy',u'x',u'y']
    for param in params:
        out[param] = makeDiv(cur[param],dst[param],divNum)
    return out

def makeDiv(st,en,divNum):
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


def isKeyScene(name):
    return name[-2:] == "_0"

def getSceneName(name,sceneId):
    return name.replace("_0","_"+str(sceneId))

def main():
    m = OBS_MANAGER()
    m.getScenes()
    for i in range(3):
        m.updateScene(1)
        m.updateScene(2)
        m.updateScene(3)
    pass

if __name__ == "__main__":
    main()
