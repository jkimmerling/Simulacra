import json
import sys
import pandas as pd
from handlers.dataHandler import dataHandler
from datetime import datetime, timedelta

# load config file
try:
    with open('config.json') as configFile:
        config = json.load(configFile)
    print("Config file loaded")
except:
    print("Failed to load config file")
    sys.exit("Terminating program")

# Initialize the debug object if debugging is enabled
if config['debugMode']:
    debugDict = {}
    debugDict['config'] = config

# Initialize and load the data
data = dataHandler(config)
data.loadData()

def main():    
    if config['serverMode'] == 'flask':
        count = 0
        import interfaces.flaskWebApi as fWA                     
        fWA.api.add_resource(fWA.BaseTime, '/', 
            resource_class_kwargs={'mainConfig': config, 'data': data,
            'debugDict': debugDict, 'count': count})
        fWA.app.run(host=config['hostName'], port=config['port'])
    
if __name__ == "__main__":
    main()