import csv
import json
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_restful import Resource, Api

with open('config.json') as configFile:
    config = json.load(configFile)
    
hostName = config['hostName']
serverPort = config['port']
csvFilePath = config['csvFilePath']
interval = config['interval']
debugMode = config['debugMode']
debugDict = {}
if debugMode:
    debugDict['config'] = config

startTime = datetime.now().replace(second=0, microsecond=0)

dataFrame = pd.read_csv(csvFilePath)

# create the base flask app
app = Flask(__name__)
# create the api object to allow class creation
api = Api(app)

class BaseTime(Resource):
    
    def getTimeDelta(self):
        timeNow = datetime.now()
        tDeltaSeconds = timeNow - startTime
        tDeltaMinutes = tDeltaSeconds.total_seconds() // 60
        return tDeltaMinutes
    
    def intervalHandler(self):
        timeAtRun = datetime.now().replace(second=0, microsecond=0)
        timeDeltaS = timeAtRun - startTime
        timeDeltaM = self.getTimeDelta()
        remainder = int(timeDeltaM) % interval
        publishTime = str(timeAtRun - timedelta(seconds=remainder*60))
        offset = int(timeDeltaM) - remainder
        if debugMode:
            debugDict['startTime'] = str(startTime)
            debugDict['timeAtRun'] = str(timeAtRun)
            debugDict['timeDeltaMinutes'] = int(timeDeltaM)
            debugDict['offset'] = offset
        return {"publishTime": publishTime, "offset": offset}
    
    def formatTime(self, jsonRow, publishTime):
        row = jsonRow
        row['Datetime'] = publishTime
        return row
        
    def getJsonRow(self, offset):
        singleRow = dataFrame.iloc[offset].to_dict()
        return singleRow
    
    def get(self):
        intervalDict = self.intervalHandler()
        jsonRow = self.getJsonRow(intervalDict["offset"])
        if debugMode:
            jsonRow["DEBUG"] = debugDict
        formattedJsonRow = self.formatTime(jsonRow, intervalDict["publishTime"])
        response = formattedJsonRow
        return response, 200

api.add_resource(BaseTime, '/')

app.run()