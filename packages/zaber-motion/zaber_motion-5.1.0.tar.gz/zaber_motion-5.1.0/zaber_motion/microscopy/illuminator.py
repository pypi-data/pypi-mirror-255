# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from ..call import call, call_async, call_sync
from ..protobufs import main_pb2
from ..ascii import DeviceIO, Connection, Device
from .illuminator_channel import IlluminatorChannel


class Illuminator:
    """
    Use to manage an LED controller.
    It is subject to breaking changes without warning until further notice.
    Requires at least Firmware 7.09.
    """

    @property
    def device(self) -> Device:
        """
        The base device of this illuminator.
        """
        return self._device

    @property
    def io(self) -> DeviceIO:
        """
        I/O channels of this device.
        """
        return self._io

    def __init__(self, device: Device):
        """
        Creates instance of `Illuminator` based on the given device.
        If the device is identified, this constructor will ensure it is an illuminator.
        """
        self._device = device
        self._io = DeviceIO(device)
        self.__verify_is_illuminator()

    def get_channel(
            self,
            channel_number: int
    ) -> IlluminatorChannel:
        """
        Gets an IlluminatorChannel class instance that allows control of a particular channel.
        Channels are numbered from 1.

        Args:
            channel_number: Number of channel to control.

        Returns:
            Illuminator channel instance.
        """
        if channel_number <= 0:
            raise ValueError('Invalid value; channels are numbered from 1.')

        return IlluminatorChannel(self, channel_number)

    def __verify_is_illuminator(
            self
    ) -> None:
        """
        Checks if this is an illuminator or some other type of device and throws an error if it is not.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        call_sync("illuminator/verify", request)

    @staticmethod
    def find(
            connection: Connection,
            device_address: int = 0
    ) -> 'Illuminator':
        """
        Finds an illuminator on a connection.
        In case of conflict, specify the optional device address.

        Args:
            connection: Connection on which to detect the illuminator.
            device_address: Optional device address of the illuminator.

        Returns:
            New instance of illuminator.
        """
        request = main_pb2.FindDeviceRequest()
        request.interface_id = connection.interface_id
        request.device_address = device_address
        response = main_pb2.FindDeviceResponse()
        call("illuminator/detect", request, response)
        return Illuminator(Device(connection, response.address))

    @staticmethod
    async def find_async(
            connection: Connection,
            device_address: int = 0
    ) -> 'Illuminator':
        """
        Finds an illuminator on a connection.
        In case of conflict, specify the optional device address.

        Args:
            connection: Connection on which to detect the illuminator.
            device_address: Optional device address of the illuminator.

        Returns:
            New instance of illuminator.
        """
        request = main_pb2.FindDeviceRequest()
        request.interface_id = connection.interface_id
        request.device_address = device_address
        response = main_pb2.FindDeviceResponse()
        await call_async("illuminator/detect", request, response)
        return Illuminator(Device(connection, response.address))

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = main_pb2.AxisToStringRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        response = main_pb2.StringResponse()
        call_sync("device/device_to_string", request, response)
        return response.value
