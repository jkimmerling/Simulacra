import csv
import json
import os, psutil
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import handlers.dataHandler as dh
import handlers.timeHandler as th

# create the base flask app
app = Flask(__name__)
# create the api object to allow class creation
api = Api(app)

class BaseTime(Resource):
    count = 0
    timeAtStart = datetime.now()
    def __init__(self, data, mainConfig, debugDict, count):
        self.config = mainConfig
        self.data = data 
        self.debugDict = debugDict       
        self.timeAtRun = datetime.now()          
    
    def formatTime(self, rows):        
        for i in range(len(rows)):
            rows[i]['Datetime'] = self.publishTime
        return rows
        
    def get(self):
        if self.config['postMode'] == 'perCallBased':
            self.timeAtRun = datetime.now()
        elif self.config['postMode'] == 'intervalBased':
            self.timeAtRun = datetime.now().replace(second=0, microsecond=0)      
        self.publishTime = th.getPublishTime(self.config['postMode'], 
                self.config['interval'], BaseTime.timeAtStart, self.timeAtRun)       
        offsetList = th.getOffset(self.config['postMode'], BaseTime.count, 
                self.timeAtStart, self.timeAtRun, self.config['interval'])
        if len(offsetList) > 1:
            BaseTime.count += 1
        response = self.data.fetchRows(offsetList[0])
        response = self.formatTime(response)
        if self.config['debugMode'] == True:
            self.debugDict['offsetList'] = offsetList
            self.debugDict['memoryUsage'] = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            response.append(self.debugDict)
        return response, 200