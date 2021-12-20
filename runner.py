import json
import pandas as pd
from datetime import datetime, timedelta


with open('config.json') as configFile:
    config = json.load(configFile)

if config['debugMode']:
    debugDict = {}
    debugDict['config'] = config

def main():    
    if config['serverMode'] == 'flask':
        count = 0
        import flaskWebApi as fWA   
        dataFrame = pd.read_csv(config['csvFilePath'])            
        fWA.api.add_resource(fWA.BaseTime, '/', 
            resource_class_kwargs={'mainConfig': config, 'dataFrame': dataFrame,
            'debugDict': debugDict, 'count': count})
        fWA.app.run(host=config['hostName'], port=config['port'])
    else:
        print("nope")

if __name__ == "__main__":
    main()