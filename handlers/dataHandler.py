import pandas as pd
import redis
import csv

class dataHandler():
    '''
    Class to load/create/return the data
    '''
    def __init__(self, config):
        self.offset = 0
        self.config = config
        self.rows = []
        self.lengthRow = []
        self.lengthDevices = []
        if self.config['dataMode'] == "redis":
            self.redis = redis.Redis(host='localhost', port=6379, db=1, \
                decode_responses=True)

    def initRedis(self):
        '''
        Checks the size of the DB. If the DB is empty it returns True. If the 
        DB is not empty it checks initRedis. If initRedis is true it will 
        flush the DB and return True, otherwise it returns False
        '''
        if self.redis.dbsize() > 0:
            if self.config["initRedis"] == True:
                print("Flushing non-empty DB")
                self.redis.flushdb()
                return True
            else:
                print("The DB is not empty")
                return False
        else:
            return True
            
        
    def createRedisData(self): 
        '''
        It Calls initRedis. If initRedis returns True it loads each of the 
        flat files into the redis DB and stores the number of devices and 
        number of record per device into variables for later use. If
        initRedis returns False it does nothing.
        '''  
        if self.initRedis() == True:
            for n in range(len(self.config['filePaths'])):
                count = 0
                print(f"Starting to load " + self.config['filePaths'][n] + ".")
                with open(self.config['filePaths'][n]) as f:                
                    for row in csv.DictReader(f, skipinitialspace=True):
                        data = {k:v for k, v in row.items()} 
                        redisKeyName = "Device_" + str(n+1) + "_Reading_" + \
                            str(count+1)       
                        self.redis.hset(redisKeyName, mapping=data)
                        count+=1
                self.lengthRow.append(count)
                print(f"Number of Rows loaded: {count}")
                print(f"Finished Loading {self.config['filePaths'][n]}.")
            self.lengthDevices = len(self.config['filePaths'])
            print(f"Number of devices loaded: {self.lengthDevices}")
        else:
            print(f"DB was not empty, and initRedis is false, no new data \
                loaded")


    def getRedisSpecificRows(self):
        if self.config['numberOfDevices'] > 0:
            for i in range(self.config['numberOfDevices']):                
                index = i + 1
                if index > self.lengthDevices-1:
                    index =  (i % self.lengthDevices) + 1
                offset = self.offset + 1
                if self.offset > self.lengthRow[index-1]-1:
                    offset = (self.offset % self.lengthRow[index-1]) + 1
                singleRow = self.redis.hgetall("Device_" + str(index) + \
                    "_Reading_" + str(offset))
                self.rows.append(singleRow)


    def createCsvData(self):
        blob = []
        for i in range(len(self.config['filePaths'])):
            df = pd.read_csv(self.config['filePaths'][i])        
            blob.append(df)      
        self.blob = blob


    def getCsvSpecificRows(self):                           
        if self.config['numberOfDevices'] > 0:
            for i in range(self.config['numberOfDevices']):                
                index = i
                lengthDevices = len(self.blob)
                if index > lengthDevices-1:
                    index =  i % lengthDevices                                 
                lengthRow = len(self.blob[index])
                offset = self.offset
                if self.offset > lengthRow-1:
                    offset = self.offset % lengthRow                 
                singleRow = self.blob[index].iloc[offset].to_dict()
                self.rows.append(singleRow) 


    def loadData(self):
        '''
        Initializes the data object based on what the config['dataMode'] 
        is configured to use.
        '''
        if self.config['dataMode'] == "flatFile":
            self.createCsvData()
        elif self.config['dataMode'] == "redis":
            self.createRedisData()


    def fetchRows(self, offset):
        self.offset = offset
        self.rows = []
        if self.config['dataMode'] == "flatFile":
            self.getCsvSpecificRows()
            return self.rows
        elif self.config['dataMode'] == "redis":
            self.getRedisSpecificRows()
            return self.rows
