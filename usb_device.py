import logging
import usb.core
import usb.util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def kustom_match(endpoint, direction=usb.util.ENDPOINT_IN):
    """
    Custom search function for findings endpoints in selected direction

    :param usb.core.Endpoint endpoint: endpoint from device
    :param int direction: desired direction of endpoint
    :return: `True` or `False` depending whether endpoint direction is equal to provided argument
    """
    return usb.util.endpoint_direction(endpoint.bEndpointAddress) == direction


class UsbDeviceNotFoundException(Exception):
    pass


class UsbDevice(object):
    """
    Class represents USB device with wrapped pyusb methods
    """

    def __init__(self, vendor, product):
        """
        Finds device on USB bus

        :return: None
        """
        self.vendor = vendor
        self.product = product

        self.device = self._find_device(self.vendor, self.product)

        self.interface = 0  # 0 is almost always used
        # self.device.reset()

    @staticmethod
    def _find_device(vendor, product):
        device = usb.core.find(idVendor=vendor, idProduct=product)

        if device is None:
            raise UsbDeviceNotFoundException()
        else:
            return device

    def get_endpoint(self, direction):
        """
        Returns USB endpoint (pipe) in selected direction

        :param int direction: direction (`usb.util.ENDPOINT_IN` or `usb.util.ENDPOINT_OUT`)
        :return: endpoint in selected direction
        :rtype: usb.core.Endpoint
        """
        configuration = self.device.get_active_configuration()

        interface = configuration[(0, 0)]

        endpoint = usb.util.find_descriptor(
            interface,
            custom_match=lambda e: kustom_match(e, direction)
        )

        return endpoint

    def read(self, endpoint):
        """
        Reads a single datagram from provided endpoint

        :param usb.core.Endpoint endpoint: endpoint to read
        :return: data from device
        :rtype: list
        """
        assert endpoint is not None

        return self.device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)

    def write(self, endpoint, data):
        """
        Writes a single datagram to provided endpoint

        :param usb.core.Endpoint endpoint: endpoint to write
        :param list data: data to write
        :return: None
        """
        assert endpoint is not None

        return self.device.write(endpoint.bEndpointAddress, data)

    def __enter__(self):
        """
        If device is already active (claimed for example by usbhid or usbfs driver), detaches it and claims for
        exclusive usage by class (as Context Manager)

        :return: handle to `self`
        :rtype: UsbDevice
        """
        if self.device.is_kernel_driver_active(self.interface) is True:
            logger.info("Device is claimed by usbhid driver, detaching it")
            # tell the kernel to detach
            self.device.detach_kernel_driver(self.interface)
            # claim the device
            usb.util.claim_interface(self.device, self.interface)
        return self

    def __exit__(self, unused_exc_type, unused_exc_val, unused_exc_tb):
        """
        Releases device claimed in `__enter__`

        :return:
        :rtype: None
        """
        usb.util.release_interface(self.device, self.interface)

    def __str__(self):
        return str(self.device)
