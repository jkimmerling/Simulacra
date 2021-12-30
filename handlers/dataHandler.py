import pandas as pd
import redis
import csv
import sys

class dataHandler():
    '''
    Class to load/create/return the data.
    '''
    def __init__(self, config):
        self.config = config
        self.lengthRow = []
        self.lengthDevices = []
        

    def redisConnect(self):
        '''
        Connects to the Redis backend.
        '''
        if self.config['dataMode'] == "redis":
            try:
                self.redis = redis.Redis(host=self.config['redisHost'], \
                    port=self.config['redisPort'], db=self.config['redisDB'], \
                    decode_responses=True)
                self.redis.ping()                
            except redis.ConnectionError:
                print("Could not connect to Redis, please ensure it is running")
                sys.exit("Terminating program")

    def redisInit(self):
        '''
        Checks the size of the DB. If the DB is empty it returns True. If the 
        DB is not empty it checks redisInit. If redisInit is true it will 
        flush the DB and return True, otherwise it returns False.
        '''
        self.redisConnect()
        if self.redis.dbsize() > 0:
            if self.config["redisInit"] == True:
                print("Flushing non-empty DB")
                self.redis.flushdb()
                return True
            else:
                print("The DB is not empty")
                return False
        else:
            return True
        
            
        
    def redisCreateData(self): 
        '''
        It Calls redisInit. If redisInit returns True it loads each of the 
        flat files into the redis DB and stores the number of devices and 
        number of record per device into variables for later use. If
        redisInit returns False it does nothing.
        '''  
        if self.redisInit() == True:
            for n in range(len(self.config['filePaths'])):
                count = 0
                print(f"Starting to load " + self.config['filePaths'][n] + ".")
                try:
                    with open(self.config['filePaths'][n]) as f:                
                        for row in csv.DictReader(f, skipinitialspace=True):
                            data = {k:v for k, v in row.items()} 
                            redisKeyName = "Device_" + str(n+1) + "_Reading_" \
                                + str(count+1)       
                            self.redis.hset(redisKeyName, mapping=data)
                            count+=1                    
                except:
                    print(f"Failed to load {self.config['filePaths'][n]}.")
                    sys.exit("Terminating program")
                self.lengthRow.append(count)
                print(f"Number of Rows loaded: {count}")
                print(f"Finished Loading {self.config['filePaths'][n]}.")
            self.lengthDevices = len(self.config['filePaths'])
            print(f"Number of devices loaded: {self.lengthDevices}")
        else:
            print(f"DB was not empty, and redisInit is false, no new data \
                loaded")


    def redisGetSpecificRows(self):
        '''
        Pulls specific rows for each "device" of data out of redis based on 
        the offset variable. If the numberOfDevices is greater than the number 
        of devices loaded into redis it will rotate and reuse the existing
        devices. If the offset called for is longer than the device's stored
        readings it will rotate back to the start of the readings.
        '''
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
        '''
        Loops through the config['filePaths'] and loads each csv into the
        csvData object.
        '''
        csvData = []
        for i in range(len(self.config['filePaths'])):
            try:
                df = pd.read_csv(self.config['filePaths'][i])        
                csvData.append(df) 
            except:
                print(f"Failed to load {self.config['filePaths'][i]}.")
                sys.exit("Terminating program")     
        self.csvData = csvData


    def getCsvSpecificRows(self):  
        '''
        Pulls specific rows for each "device" of data out of the csvData object
        based on the offset variable. If the numberOfDevices is greater than 
        the number of devices loaded into the csvData object it will rotate and 
        reuse the existing devices. If the offset called for is longer than the
        device's stored readings it will rotate back to the start of the 
        readings.
        '''                         
        if self.config['numberOfDevices'] > 0:
            for i in range(self.config['numberOfDevices']):                
                index = i
                lengthDevices = len(self.csvData)
                if index > lengthDevices-1:
                    index =  i % lengthDevices                                 
                lengthRow = len(self.csvData[index])
                offset = self.offset
                if self.offset > lengthRow-1:
                    offset = self.offset % lengthRow                 
                singleRow = self.csvData[index].iloc[offset].to_dict()
                self.rows.append(singleRow) 


    def loadData(self):
        '''
        Initializes the data object based on what the config['dataMode'] 
        is configured to use.
        '''
        if self.config['dataMode'] == "flatFile":
            self.createCsvData()
        elif self.config['dataMode'] == "redis":
            self.redisCreateData()


    def fetchRows(self, offset):
        '''
        Takes in the offset and sets the self.offset variable. Then based on
        what the config['dataMode'] setting is, it will either use the flat
        files directly, or it will call one of the DB backend functions.
        '''
        self.offset = offset
        self.rows = []
        if self.config['dataMode'] == "flatFile":
            self.getCsvSpecificRows()
            return self.rows
        elif self.config['dataMode'] == "redis":
            self.redisGetSpecificRows()
            return self.rows
