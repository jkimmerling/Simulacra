import pandas as pd

def getDataBlob(filePaths):
    blob = []
    for i in range(len(filePaths)):
        df = pd.read_csv(filePaths[i])        
        blob.append(df)      
    return blob

def getSpecificRows(dataBlob, offset):
    rows = []
    for i in range(len(dataBlob)):
        singleRow = dataBlob[i].iloc[offset].to_dict()
        rows.append(singleRow)
    return rows
  