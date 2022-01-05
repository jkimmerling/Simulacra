from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run
from bacpypes.task import RecurringTask

from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogValueObject, BinaryValueObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.service.cov import ChangeOfValueServices
from bacpypes.service.object import ReadWritePropertyMultipleServices


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


def main():
    global test_av, test_bv, test_application

    # make a parser
    # parser = ConfigArgumentParser(description=__doc__)

    # parse the command line arguments
    # args = parser.parse_args()

    # make a device object
    this_device = LocalDeviceObject(objectIdentifier=599, vendorIdentifier=15, address="192.168.1.14/24")
    address="192.168.1.14/24"
    # make a sample application
    test_application = BIPSimpleApplication(this_device, address)

    # make an analog value object
    test_av = AnalogValueObject(
        objectIdentifier=("analogValue", 1),
        objectName="av",
        presentValue=0.0,
        statusFlags=[0, 0, 0, 0],
        covIncrement=1.0,
    )

    # add it to the device
    test_application.add_object(test_av)

    # make a binary value object
    test_bv = BinaryValueObject(
        objectIdentifier=("binaryValue", 1),
        objectName="bv",
        presentValue="inactive",
        statusFlags=[0, 0, 0, 0],
    )

    # add it to the device
    test_application.add_object(test_bv)

    # binary value task
    do_something_task = DoSomething(INTERVAL)
    do_something_task.install_task()

    run()


if __name__ == "__main__":
    main()