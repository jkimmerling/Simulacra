from datetime import datetime, timedelta

def getPublishTime(postMode, interval, timeAtStart, timeAtRun):    
        if postMode == 'perCallBased':
            publishTime = str(timeAtRun)
        elif postMode == 'intervalBased':
            timeDeltaM = getTimeDelta(postMode, timeAtStart, timeAtRun)
            remainder = int(timeDeltaM) % interval
            publishTime = str(timeAtRun - timedelta(seconds=remainder*60))     
        return publishTime             

def getTimeDelta(postMode, timeAtStart, timeAtRun):
        if postMode == 'intervalBased':
            timeAtStart = timeAtStart.replace(second=0, microsecond=0)
        tDeltaSeconds = timeAtRun - timeAtStart
        tDeltaMinutes = tDeltaSeconds.total_seconds() // 60
        return tDeltaMinutes

def getOffset(postMode, count, timeAtStart, timeAtRun, interval):
        if postMode == 'perCallBased':
            offset = count
            count += 1
            print(offset)
            return [offset, count]
        elif postMode == 'intervalBased':
            intTimeDeltaM = int(getTimeDelta(postMode, timeAtStart, timeAtRun))
            remainder = intTimeDeltaM % interval
            offset = intTimeDeltaM - remainder
            print(locals())
            return [offset]
        