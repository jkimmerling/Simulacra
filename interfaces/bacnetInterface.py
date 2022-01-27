from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run
from bacpypes.task import RecurringTask

from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, BinaryValueObject, MultiStateValueObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices

from datetime import datetime
import handlers.dataHandler as dh
import handlers.timeHandler as th

# Initialize and load the data
# data = dh(config)
# data.loadData()


INTERVAL = 10

class DoSomething(RecurringTask):
    count = 0
    timeAtStart = datetime.now()
    def __init__(self, interval, bacnet_points_list, data, config):
        RecurringTask.__init__(self, interval * 1000)

        # save the interval
        self.interval = config['interval']
        self.bacnet_points_list = bacnet_points_list
        self.data = data
        self.config = config
        self.timeAtRun = datetime.now()    
        
    def process_values(self, output):
        value_list = []
        for index in range(len(output)):
            output[index].pop('Datetime', None)
            for k, v in output[index].items():
                value_list.append(v)
        return value_list

    def update_point_values(self, bacnet_points_list, list_of_point_values):
        for index in range(len(bacnet_points_list)):
            if bacnet_points_list[index].objectName[-2:] == "AV":
                bacnet_points_list[index].presentValue = float(list_of_point_values[index])
            elif bacnet_points_list[index].objectName[-2:] == "BV":
                if int(list_of_point_values[index]) == 1:
                    bacnet_points_list[index].presentValue = 'active'
                else:
                    bacnet_points_list[index].presentValue = 'inactive'
            elif bacnet_points_list[index].objectName[-3:] == "MSV":
                bacnet_points_list[index].presentValue = int(list_of_point_values[index])

    def process_task(self):
        if self.config['postMode'] == 'intervalBased':
            self.timeAtRun = datetime.now().replace(second=0, microsecond=0)
        offsetList = th.getOffset(self.config['postMode'], DoSomething.count, 
                self.timeAtStart, self.timeAtRun, self.config['interval'])
        if len(offsetList) > 1:
            DoSomething.count += 1
        raw_point_values = self.data.fetchRows(offsetList[0])  
        list_of_point_values = self.process_values(raw_point_values)
        self.update_point_values(self.bacnet_points_list, list_of_point_values)


def main(data, config):

    address=config['bacnetBindAddress']
    
    this_device = LocalDeviceObject(objectIdentifier=599, vendorIdentifier=15, address=address)
    
    
    test_application = BIPSimpleApplication(this_device, address)

    point_list = data.fetchColumnNames()
    av_point_number = 1
    bv_point_number = 1
    msv_point_number = 1
    bacnet_point_list = []
    for device in range(len(point_list)):
        for point in range(1, len(point_list[device])):
            if point_list[device][point][-2:] == "AV":
                bacnet_point_list.append(AnalogValueObject(
                    objectIdentifier=("analogValue", av_point_number),
                    objectName= str(device + 1) + "_" + point_list[device][point],
                    presentValue=0.0,
                    statusFlags=[0, 0, 0, 0],
                    covIncrement=1.0,
                ))
                test_application.add_object(bacnet_point_list[-1])
                av_point_number += 1
            elif point_list[device][point][-2:] == "BV":
                bacnet_point_list.append(BinaryValueObject(
                    objectIdentifier=("binaryValue", bv_point_number),
                    objectName=str(device + 1) + "_" + point_list[device][point],
                    presentValue="inactive",
                    statusFlags=[0, 0, 0, 0],
                ))
                test_application.add_object(bacnet_point_list[-1])
                bv_point_number += 1
            elif point_list[device][point][-3:] == "MSV":
                bacnet_point_list.append(MultiStateValueObject(
                    objectIdentifier=("multiStateValue", msv_point_number),
                    objectName=str(device + 1) + "_" + point_list[device][point],
                    presentValue=1,
                    statusFlags=[0, 0, 0, 0],
                ))
                test_application.add_object(bacnet_point_list[-1])
                msv_point_number += 1

    

    do_something_task = DoSomething(INTERVAL, bacnet_point_list, data, config)
    do_something_task.install_task()

    run()
