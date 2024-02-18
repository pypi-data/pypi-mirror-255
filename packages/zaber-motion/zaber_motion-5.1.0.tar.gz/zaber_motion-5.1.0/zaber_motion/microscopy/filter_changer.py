# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0622

from ..call import call, call_async, call_sync
from ..protobufs import main_pb2
from ..ascii import Device


class FilterChanger:
    """
    A generic turret device.
    """

    @property
    def device(self) -> Device:
        """
        The base device of this turret.
        """
        return self._device

    def __init__(self, device: Device):
        """
        Creates instance of `FilterChanger` based on the given device.
        """
        self._device = device

    def get_number_of_filters(
            self
    ) -> int:
        """
        Gets number of filters of the changer.

        Returns:
            Number of positions.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        call("device/get_index_count", request, response)
        return response.value

    async def get_number_of_filters_async(
            self
    ) -> int:
        """
        Gets number of filters of the changer.

        Returns:
            Number of positions.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        await call_async("device/get_index_count", request, response)
        return response.value

    def get_current_filter(
            self
    ) -> int:
        """
        Returns the current filter number starting from 1.
        The value of 0 indicates that the position is either unknown or between two filters.

        Returns:
            Filter number starting from 1 or 0 if the position cannot be determined.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        call("device/get_index_position", request, response)
        return response.value

    async def get_current_filter_async(
            self
    ) -> int:
        """
        Returns the current filter number starting from 1.
        The value of 0 indicates that the position is either unknown or between two filters.

        Returns:
            Filter number starting from 1 or 0 if the position cannot be determined.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        await call_async("device/get_index_position", request, response)
        return response.value

    def change(
            self,
            filter: int
    ) -> None:
        """
        Changes to the specified filter.

        Args:
            filter: Filter number starting from 1.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        request.type = main_pb2.DeviceMoveRequest.INDEX
        request.wait_until_idle = True
        request.arg_int = filter
        call("device/move", request)

    async def change_async(
            self,
            filter: int
    ) -> None:
        """
        Changes to the specified filter.

        Args:
            filter: Filter number starting from 1.
        """
        request = main_pb2.DeviceMoveRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.axis = 1
        request.type = main_pb2.DeviceMoveRequest.INDEX
        request.wait_until_idle = True
        request.arg_int = filter
        await call_async("device/move", request)

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
