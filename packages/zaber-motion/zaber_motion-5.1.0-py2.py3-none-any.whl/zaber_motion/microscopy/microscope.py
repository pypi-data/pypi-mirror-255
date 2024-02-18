# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Optional
from ..call import call, call_async, call_sync
from ..protobufs import main_pb2
from ..ascii import Connection, Device, Axis, AxisGroup
from .illuminator import Illuminator
from .filter_changer import FilterChanger
from .objective_changer import ObjectiveChanger
from .microscope_config import MicroscopeConfig


class Microscope:
    """
    Represent a microscope.
    It is subject to breaking changes without warning until further notice.
    Parts of the microscope may or may not be instantiated depending on the configuration.
    Requires at least Firmware 7.34.
    """

    @property
    def connection(self) -> Connection:
        """
        Connection of the microscope.
        """
        return self._connection

    @property
    def illuminator(self) -> Optional[Illuminator]:
        """
        The illuminator.
        """
        return self._illuminator

    @property
    def focus_axis(self) -> Optional[Axis]:
        """
        The focus axis.
        """
        return self._focus_axis

    @property
    def x_axis(self) -> Optional[Axis]:
        """
        The X axis.
        """
        return self._x_axis

    @property
    def y_axis(self) -> Optional[Axis]:
        """
        The Y axis.
        """
        return self._y_axis

    @property
    def plate(self) -> Optional[AxisGroup]:
        """
        Axis group consisting of X and Y axes representing the plate of the microscope.
        """
        return self._plate

    @property
    def objective_changer(self) -> Optional[ObjectiveChanger]:
        """
        The objective changer.
        """
        return self._objective_changer

    @property
    def filter_changer(self) -> Optional[FilterChanger]:
        """
        The filter changer.
        """
        return self._filter_changer

    def __init__(self, connection: Connection, config: MicroscopeConfig):
        """
        Creates instance of `Microscope` from the given config.
        Parts are instantiated depending on device addresses in the config.
        """
        self._connection = connection
        self._config = MicroscopeConfig.from_protobuf(MicroscopeConfig.to_protobuf(config))
        self._illuminator = Illuminator(Device(connection, config.illuminator)) if config.illuminator else None
        self._focus_axis = Axis(Device(connection, config.focus_axis.device), config.focus_axis.axis)\
            if config.focus_axis and config.focus_axis.device else None
        self._x_axis = Axis(Device(connection, config.x_axis.device), config.x_axis.axis)\
            if config.x_axis and config.x_axis.device else None
        self._y_axis = Axis(Device(connection, config.y_axis.device), config.y_axis.axis)\
            if config.y_axis and config.y_axis.device else None
        self._plate = AxisGroup([self._x_axis, self._y_axis])\
            if self._x_axis is not None and self._y_axis is not None else None
        self._objective_changer = ObjectiveChanger(Device(connection, config.objective_changer), self._focus_axis)\
            if config.objective_changer and self._focus_axis else None
        self._filter_changer = FilterChanger(Device(connection, config.filter_changer))\
            if config.filter_changer else None

    @staticmethod
    def find(
            connection: Connection
    ) -> 'Microscope':
        """
        Finds a microscope on a connection.

        Args:
            connection: Connection on which to detect the microscope.

        Returns:
            New instance of microscope.
        """
        request = main_pb2.InterfaceEmptyRequest()
        request.interface_id = connection.interface_id
        response = main_pb2.MicroscopeConfig()
        call("microscope/detect", request, response)
        return Microscope(connection, MicroscopeConfig.from_protobuf(response))

    @staticmethod
    async def find_async(
            connection: Connection
    ) -> 'Microscope':
        """
        Finds a microscope on a connection.

        Args:
            connection: Connection on which to detect the microscope.

        Returns:
            New instance of microscope.
        """
        request = main_pb2.InterfaceEmptyRequest()
        request.interface_id = connection.interface_id
        response = main_pb2.MicroscopeConfig()
        await call_async("microscope/detect", request, response)
        return Microscope(connection, MicroscopeConfig.from_protobuf(response))

    def initialize(
            self
    ) -> None:
        """
        Initializes the microscope.
        Homes all axes, filter changer, and objective changer.
        """
        request = main_pb2.MicroscopeEmptyRequest()
        request.interface_id = self.connection.interface_id
        request.config.CopyFrom(MicroscopeConfig.to_protobuf(self._config))
        call("microscope/initialize", request)

    async def initialize_async(
            self
    ) -> None:
        """
        Initializes the microscope.
        Homes all axes, filter changer, and objective changer.
        """
        request = main_pb2.MicroscopeEmptyRequest()
        request.interface_id = self.connection.interface_id
        request.config.CopyFrom(MicroscopeConfig.to_protobuf(self._config))
        await call_async("microscope/initialize", request)

    def is_initialized(
            self
    ) -> bool:
        """
        Checks whether the microscope is initialized.

        Returns:
            True, when the microscope is initialized. False, otherwise.
        """
        request = main_pb2.MicroscopeEmptyRequest()
        request.interface_id = self.connection.interface_id
        request.config.CopyFrom(MicroscopeConfig.to_protobuf(self._config))
        response = main_pb2.BoolResponse()
        call("microscope/is_initialized", request, response)
        return response.value

    async def is_initialized_async(
            self
    ) -> bool:
        """
        Checks whether the microscope is initialized.

        Returns:
            True, when the microscope is initialized. False, otherwise.
        """
        request = main_pb2.MicroscopeEmptyRequest()
        request.interface_id = self.connection.interface_id
        request.config.CopyFrom(MicroscopeConfig.to_protobuf(self._config))
        response = main_pb2.BoolResponse()
        await call_async("microscope/is_initialized", request, response)
        return response.value

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the microscope.

        Returns:
            A string that represents the microscope.
        """
        request = main_pb2.MicroscopeEmptyRequest()
        request.interface_id = self.connection.interface_id
        request.config.CopyFrom(MicroscopeConfig.to_protobuf(self._config))
        response = main_pb2.StringResponse()
        call_sync("microscope/to_string", request, response)
        return response.value
