import logging
import time
import usb.core
import usb.util

from usb_device import UsbDevice

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    with UsbDevice(vendor=0x0483, product=0x5711) as my_device:
        endpoint_in = my_device.get_endpoint(usb.util.ENDPOINT_IN)
        logger.debug(endpoint_in)

        endpoint_out = my_device.get_endpoint(usb.util.ENDPOINT_OUT)
        logger.debug(endpoint_out)

        while True:
            time.sleep(1)

            try:
                readings = my_device.read(endpoint_in)
                logger.debug(readings)
            except usb.core.USBError as e:
                logger.exception(e)

            data = my_device.write(endpoint_out, list(range(9)))

if __name__ == "__main__":
    main()
