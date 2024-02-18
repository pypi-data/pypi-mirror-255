# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import List
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from .axis import Axis
from ..measurement import Measurement
from ..units import units_from_literals, LengthUnits


class AxisGroup:
    """
    Groups multiple axes across devices into a single group to allow for simultaneous movement.
    Note that the movement is not coordinated and trajectory is inconsistent and not repeatable between calls.
    Make sure that any possible trajectory is clear of potential obstacles.
    """

    @property
    def axes(self) -> List[Axis]:
        """
        Axes of the group.
        """
        return self._axes

    def __init__(self, axes: List[Axis]):
        """
        Initializes the group with the axes to be controlled.
        """
        self._axes = axes.copy()

    def home(
            self
    ) -> None:
        """
        Homes the axes.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        call("axes/home", request)

    async def home_async(
            self
    ) -> None:
        """
        Homes the axes.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        await call_async("axes/home", request)

    def stop(
            self
    ) -> None:
        """
        Stops the axes.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        call("axes/stop", request)

    async def stop_async(
            self
    ) -> None:
        """
        Stops the axes.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        await call_async("axes/stop", request)

    def move_absolute(
            self,
            *position: Measurement
    ) -> None:
        """
        Moves the axes to absolute position.

        Args:
            position: Position.
        """
        request = main_pb2.AxesMoveRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.position.extend([Measurement.to_protobuf(a) for a in position])
        call("axes/move_absolute", request)

    async def move_absolute_async(
            self,
            *position: Measurement
    ) -> None:
        """
        Moves the axes to absolute position.

        Args:
            position: Position.
        """
        request = main_pb2.AxesMoveRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.position.extend([Measurement.to_protobuf(a) for a in position])
        await call_async("axes/move_absolute", request)

    def move_relative(
            self,
            *position: Measurement
    ) -> None:
        """
        Move axes to position relative to the current position.

        Args:
            position: Position.
        """
        request = main_pb2.AxesMoveRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.position.extend([Measurement.to_protobuf(a) for a in position])
        call("axes/move_relative", request)

    async def move_relative_async(
            self,
            *position: Measurement
    ) -> None:
        """
        Move axes to position relative to the current position.

        Args:
            position: Position.
        """
        request = main_pb2.AxesMoveRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.position.extend([Measurement.to_protobuf(a) for a in position])
        await call_async("axes/move_relative", request)

    def move_min(
            self
    ) -> None:
        """
        Moves axes to the minimum position as specified by limit.min.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        call("axes/move_min", request)

    async def move_min_async(
            self
    ) -> None:
        """
        Moves axes to the minimum position as specified by limit.min.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        await call_async("axes/move_min", request)

    def move_max(
            self
    ) -> None:
        """
        Moves axes to the maximum position as specified by limit.max.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        call("axes/move_max", request)

    async def move_max_async(
            self
    ) -> None:
        """
        Moves axes to the maximum position as specified by limit.max.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        await call_async("axes/move_max", request)

    def wait_until_idle(
            self
    ) -> None:
        """
        Waits until all the axes stop moving.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        call("axes/wait_until_idle", request)

    async def wait_until_idle_async(
            self
    ) -> None:
        """
        Waits until all the axes stop moving.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        await call_async("axes/wait_until_idle", request)

    def get_position(
            self,
            *unit: LengthUnits
    ) -> List[float]:
        """
        Returns current axes position.
        The positions are requested sequentially.
        The result position may not be accurate if the axes are moving.

        Args:
            unit: Units of position. You can specify units once or for each axis separately.

        Returns:
            Axes position.
        """
        request = main_pb2.AxesGetSettingRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.setting = "pos"
        request.unit.extend([units_from_literals(u).value for u in unit])
        response = main_pb2.DoubleArrayResponse()
        call("axes/get_setting", request, response)
        return list(response.values)

    async def get_position_async(
            self,
            *unit: LengthUnits
    ) -> List[float]:
        """
        Returns current axes position.
        The positions are requested sequentially.
        The result position may not be accurate if the axes are moving.

        Args:
            unit: Units of position. You can specify units once or for each axis separately.

        Returns:
            Axes position.
        """
        request = main_pb2.AxesGetSettingRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        request.setting = "pos"
        request.unit.extend([units_from_literals(u).value for u in unit])
        response = main_pb2.DoubleArrayResponse()
        await call_async("axes/get_setting", request, response)
        return list(response.values)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the axes.

        Returns:
            A string that represents the axes.
        """
        request = main_pb2.AxesEmptyRequest()
        request.interfaces.extend([axis.device.connection.interface_id for axis in self._axes])
        request.devices.extend([axis.device.device_address for axis in self._axes])
        request.axes.extend([axis.axis_number for axis in self._axes])
        response = main_pb2.StringResponse()
        call_sync("axes/to_string", request, response)
        return response.value
