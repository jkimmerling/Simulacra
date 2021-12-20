import csv
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

# startTime = datetime.now().replace(second=0, microsecond=0)

# create the base flask app
app = Flask(__name__)
# create the api object to allow class creation
api = Api(app)
# count = 0

class BaseTime(Resource):
    count = 0
    startTime = datetime.now()
    def __init__(self, dataFrame, mainConfig, debugDict, count):
        self.config = mainConfig
        self.dataFrame = dataFrame
        self.debugDict = debugDict
        # self.count = count
        self.offset = 0        
        self.timeAtRun = datetime.now()          
    
    def getTimeDelta(self):
        timeNow = datetime.now()
        tDeltaSeconds = timeNow - BaseTime.startTime.replace(second=0, microsecond=0)
        tDeltaMinutes = tDeltaSeconds.total_seconds() // 60
        return tDeltaMinutes

    def getPublishTime(self):    
        if self.config['postMode'] == 'perCallBased':
            publishTime = str(self.timeAtRun)
            timeDeltaM = 0
        elif self.config['postMode'] == 'intervalBased':
            timeDeltaM = self.getTimeDelta()
            remainder = int(self.getTimeDelta()) % interval
            publishTime = str(self.timeAtRun - 
                            self.timedelta(seconds=remainder*60))
            BaseTime.startTime = BaseTime.startTime.replace(second=0, microsecond=0)
        if self.config['debugMode']:
            self.debugDict['startTime'] = str(BaseTime.startTime)
            self.debugDict['timeAtRun'] = str(self.timeAtRun)
            self.debugDict['timeDeltaMinutes'] = int(timeDeltaM)
        return publishTime

    def getOffset(self):
        if self.config['postMode'] == 'perCallBased':
            offset = BaseTime.count
            BaseTime.count += 1
        elif self.config['postMode'] == 'intervalBased':
            intTimeDeltaM = int(self.getTimeDelta())
            remainder = intTimeDeltaM % self.config['interval']
            offset = intTimeDeltaM - remainder
        if self.config['debugMode']:
            self.debugDict['offset'] = offset
        return offset

    def formatTime(self):
        row = self.jsonRow
        row['Datetime'] = self.publishTime
        return row

    def getJsonRow(self):
        singleRow = self.dataFrame.iloc[self.offset].to_dict()
        return singleRow

    def get(self):
        if self.config['postMode'] == 'perCallBased':
            self.timeAtRun = datetime.now()
        elif self.config['postMode'] == 'intervalBased':
            self.timeAtRun = datetime.now().replace(second=0, microsecond=0)      
        self.publishTime = self.getPublishTime()        
        self.offset = self.getOffset()
        self.jsonRow = self.getJsonRow()
        if self.config['debugMode']:
            self.jsonRow["DEBUG"] = self.debugDict
        formattedJsonRow = self.formatTime()
        response = formattedJsonRow
        return response, 200