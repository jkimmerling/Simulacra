import csv
import json
import os, psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import dataHandler as dh

# create the base flask app
app = Flask(__name__)
# create the api object to allow class creation
api = Api(app)

class BaseTime(Resource):
    count = 0
    startTime = datetime.now()
    def __init__(self, dataBlob, mainConfig, debugDict, count):
        self.config = mainConfig
        self.dataBlob = dataBlob # a list of dictionaries
        self.debugDict = debugDict
        self.offset = 0        
        self.timeAtRun = datetime.now()          
    
    def getTimeDelta(self):
        timeNow = datetime.now()
        tDeltaSeconds = timeNow - BaseTime.startTime.replace(second=0, microsecond=0)
        tDeltaMinutes = tDeltaSeconds.total_seconds() // 60
        return tDeltaMinutes

    def getPublishTime(self):    
        if self.config['postMode'] == 'perCallBased':
            self.publishTime = str(self.timeAtRun)
            timeDeltaM = 0
        elif self.config['postMode'] == 'intervalBased':
            timeDeltaM = self.getTimeDelta()
            remainder = int(self.getTimeDelta()) % self.config['interval']
            self.publishTime = str(self.timeAtRun - timedelta(seconds=remainder*60))
            BaseTime.startTime = BaseTime.startTime.replace(second=0, microsecond=0)
        if self.config['debugMode'] == True:
            self.debugDict['startTime'] = str(BaseTime.startTime)
            self.debugDict['timeAtRun'] = str(self.timeAtRun)
            self.debugDict['timeDeltaMinutes'] = int(timeDeltaM)        

    def getOffset(self):
        if self.config['postMode'] == 'perCallBased':
            self.offset = BaseTime.count
            BaseTime.count += 1
        elif self.config['postMode'] == 'intervalBased':
            intTimeDeltaM = int(self.getTimeDelta())
            remainder = intTimeDeltaM % self.config['interval']
            self.offset = intTimeDeltaM - remainder
        if self.config['debugMode'] == True:
            self.debugDict['offset'] = self.offset        

    def formatTime(self):        
        for i in range(len(self.dataBlob)):
            self.dataBlob[i]['Datetime'] = self.publishTime
        
    def get(self):
        if self.config['postMode'] == 'perCallBased':
            self.timeAtRun = datetime.now()
        elif self.config['postMode'] == 'intervalBased':
            self.timeAtRun = datetime.now().replace(second=0, microsecond=0)      
        self.getPublishTime()        
        self.getOffset()
        self.formatTime()
        response = dh.getSpecificRows(self.dataBlob, self.offset, self.config["numberOfDevices"])
        if self.config['debugMode'] == True:
            self.debugDict['memoryUsage'] = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            response.append(self.debugDict)
        return response, 200