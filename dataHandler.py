import pandas as pd

def getDataBlob(filePaths):
    blob = []
    for i in range(len(filePaths)):
        df = pd.read_csv(filePaths[i])        
        blob.append(df)      
    return blob

def getSpecificRows(dataBlob, offset, numberOfDevices=0):
    rows = []
    length = len(dataBlob)
    if offset > length:
        offset = offset % length
    if numberOfDevices > 0:
        for i in range(numberOfDevices):
            index = i
            if index > length:
                index =  i % length
            singleRow = dataBlob[index-1].iloc[offset].to_dict()
            rows.append(singleRow)
    else: 
        for i in range(len(dataBlob)):
            singleRow = dataBlob[i].iloc[offset].to_dict()
            rows.append(singleRow)
    return rows
  