from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run
from bacpypes.task import RecurringTask

from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, BinaryValueObject, MultiStateValueObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices

import handlers.dataHandler as dh
import handlers.timeHandler as th

# Initialize and load the data
# data = dh(config)
# data.loadData()


INTERVAL = 10

class DoSomething(RecurringTask):
    def __init__(self, interval):
        RecurringTask.__init__(self, interval * 1000)

        # save the interval
        self.interval = interval

        # make a list of test values
        self.test_values = [
            ("active", 1.0),
            ("inactive", 2.0),
            ("active", 3.0),
            ("inactive", 4.0),
        ]

    def process_task(self):
        global test_av, test_bv

        # pop the next value
        next_value = self.test_values.pop(0)
        self.test_values.append(next_value)

        # change the point
        test_av.presentValue = next_value[1]
        test_bv.presentValue = next_value[0]


def main(data):
    global test_av, test_bv, test_application

    # make a parser
    # parser = ConfigArgumentParser(description=__doc__)

    # parse the command line arguments
    # args = parser.parse_args()

    # make a device object
    this_device = LocalDeviceObject(objectIdentifier=599, vendorIdentifier=15, address="10.10.1.109/24")
    address="10.10.1.109/24"
    # make a sample application
    test_application = BIPSimpleApplication(this_device, address)

    point_list = data.fetchColumnNames()
    av_point_number = 1
    bv_point_number = 1
    msv_point_number = 1
    for device in range(len(point_list)):
        for point in range(1, len(point_list[device])):
            if point_list[device][point][-2:] == "AV":
                test_av = AnalogValueObject(
                    objectIdentifier=("analogValue", av_point_number),
                    objectName= str(device + 1) + "_" + point_list[device][point],
                    presentValue=0.0,
                    statusFlags=[0, 0, 0, 0],
                    covIncrement=1.0,
                )
                # add it to the device
                test_application.add_object(test_av)
                av_point_number += 1
            elif point_list[device][point][-2:] == "BV":
                test_bv = BinaryValueObject(
                    objectIdentifier=("binaryValue", bv_point_number),
                    objectName=str(device + 1) + "_" + point_list[device][point],
                    presentValue="inactive",
                    statusFlags=[0, 0, 0, 0],
                )   
                # add it to the device
                test_application.add_object(test_bv)
                bv_point_number += 1
            elif point_list[device][point][-3:] == "MSV":
                test_msv = MultiStateValueObject(
                    objectIdentifier=("multiStateValue", msv_point_number),
                    objectName=str(device + 1) + "_" + point_list[device][point],
                    presentValue=1,
                    statusFlags=[0, 0, 0, 0],
                )
                test_application.add_object(test_msv)
                msv_point_number += 1
    # # make an analog value object
    # test_av = AnalogValueObject(
    #     objectIdentifier=("analogValue", 1),
    #     objectName="av",
    #     presentValue=0.0,
    #     statusFlags=[0, 0, 0, 0],
    #     covIncrement=1.0,
    # )

    # # add it to the device
    # test_application.add_object(test_av)

    # make a binary value object
    

    # binary value task
    do_something_task = DoSomething(INTERVAL)
    do_something_task.install_task()

    run()


# if __name__ == "__main__":
#     main()