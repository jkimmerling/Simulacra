import json
import pandas as pd
from handlers.dataHandler import dataHandler
from datetime import datetime, timedelta


with open('config.json') as configFile:
    config = json.load(configFile)

if config['debugMode']:
    debugDict = {}
    debugDict['config'] = config

data = dataHandler(config)
data.loadData()

def main():    
    if config['serverMode'] == 'flask':
        count = 0
        import flaskWebApi as fWA                     
        fWA.api.add_resource(fWA.BaseTime, '/', 
            resource_class_kwargs={'mainConfig': config, 'dataBlob': data,
            'debugDict': debugDict, 'count': count})
        fWA.app.run(host=config['hostName'], port=config['port'])
    
if __name__ == "__main__":
    main()