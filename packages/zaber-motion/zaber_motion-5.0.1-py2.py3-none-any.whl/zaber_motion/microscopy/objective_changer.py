# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from ..call import call, call_async, call_sync
from ..protobufs import main_pb2
from ..measurement import Measurement
from ..ascii import Connection, Device, Axis
from ..units import Units, units_from_literals, LengthUnits


class ObjectiveChanger:
    """
    Represents an objective changer of a microscope.
    Unstable. Expect breaking changes in future releases.
    Requires at least Firmware 7.32.
    """

    @property
    def turret(self) -> Device:
        """
        Device address of the turret.
        """
        return self._turret

    @property
    def focus_axis(self) -> Axis:
        """
        The focus axis.
        """
        return self._focus_axis

    def __init__(self, turret: Device, focus_axis: Axis):
        """
        Creates instance of `ObjectiveChanger` based on the given device.
        If the device is identified, this constructor will ensure it is an objective changer.
        """
        self._turret = turret
        self._focus_axis = focus_axis
        self.__verify_is_changer()

    @staticmethod
    def find(
            connection: Connection,
            turret_address: int = 0,
            focus_address: int = 0
    ) -> 'ObjectiveChanger':
        """
        Finds an objective changer on a connection.
        In case of conflict, specify the optional device addresses.
        Devices on the connection must be identified.

        Args:
            connection: Connection on which to detect the objective changer.
            turret_address: Optional device address of the turret device (X-MOR).
            focus_address: Optional device address of the focus device (X-LDA).

        Returns:
            New instance of objective changer.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = connection.interface_id
        request.turret_address = turret_address
        request.focus_address = focus_address
        response = main_pb2.ObjectiveChangerCreateResponse()
        call("objective_changer/detect", request, response)
        return ObjectiveChanger(
            Device(connection, response.turret),
            Axis(Device(connection, response.focus_address), response.focus_axis))

    @staticmethod
    async def find_async(
            connection: Connection,
            turret_address: int = 0,
            focus_address: int = 0
    ) -> 'ObjectiveChanger':
        """
        Finds an objective changer on a connection.
        In case of conflict, specify the optional device addresses.
        Devices on the connection must be identified.

        Args:
            connection: Connection on which to detect the objective changer.
            turret_address: Optional device address of the turret device (X-MOR).
            focus_address: Optional device address of the focus device (X-LDA).

        Returns:
            New instance of objective changer.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = connection.interface_id
        request.turret_address = turret_address
        request.focus_address = focus_address
        response = main_pb2.ObjectiveChangerCreateResponse()
        await call_async("objective_changer/detect", request, response)
        return ObjectiveChanger(
            Device(connection, response.turret),
            Axis(Device(connection, response.focus_address), response.focus_axis))

    def change(
            self,
            objective: int,
            focus_offset: Measurement = Measurement(0)
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.
        The focus stage moves to the focus datum after the objective change.

        Args:
            objective: Objective number starting from 1.
            focus_offset: Optional offset from the focus datum.
        """
        request = main_pb2.ObjectiveChangerChangeRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.objective = objective
        request.focus_offset.CopyFrom(Measurement.to_protobuf(focus_offset))
        call("objective_changer/change", request)

    async def change_async(
            self,
            objective: int,
            focus_offset: Measurement = Measurement(0)
    ) -> None:
        """
        Changes the objective.
        Runs a sequence of movements switching from the current objective to the new one.
        The focus stage moves to the focus datum after the objective change.

        Args:
            objective: Objective number starting from 1.
            focus_offset: Optional offset from the focus datum.
        """
        request = main_pb2.ObjectiveChangerChangeRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.objective = objective
        request.focus_offset.CopyFrom(Measurement.to_protobuf(focus_offset))
        await call_async("objective_changer/change", request)

    def release(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        call("objective_changer/release", request)

    async def release_async(
            self
    ) -> None:
        """
        Moves the focus stage out of the turret releasing the current objective.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        await call_async("objective_changer/release", request)

    def get_current_objective(
            self
    ) -> int:
        """
        Returns current objective number starting from 1.
        The value of 0 indicates that the position is either unknown or between two objectives.

        Returns:
            Current objective number starting from 1 or 0 if not applicable.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.turret.connection.interface_id
        request.device = self.turret.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        call("device/get_index_position", request, response)
        return response.value

    async def get_current_objective_async(
            self
    ) -> int:
        """
        Returns current objective number starting from 1.
        The value of 0 indicates that the position is either unknown or between two objectives.

        Returns:
            Current objective number starting from 1 or 0 if not applicable.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.turret.connection.interface_id
        request.device = self.turret.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        await call_async("device/get_index_position", request, response)
        return response.value

    def get_number_of_objectives(
            self
    ) -> int:
        """
        Gets number of objectives that the turret can accommodate.

        Returns:
            Number of positions.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.turret.connection.interface_id
        request.device = self.turret.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        call("device/get_index_count", request, response)
        return response.value

    async def get_number_of_objectives_async(
            self
    ) -> int:
        """
        Gets number of objectives that the turret can accommodate.

        Returns:
            Number of positions.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.turret.connection.interface_id
        request.device = self.turret.device_address
        request.axis = 1
        response = main_pb2.IntResponse()
        await call_async("device/get_index_count", request, response)
        return response.value

    def get_focus_datum(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            unit: Units of datum.

        Returns:
            The datum.
        """
        request = main_pb2.ObjectiveChangerSetRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        call("objective_changer/get_datum", request, response)
        return response.value

    async def get_focus_datum_async(
            self,
            unit: LengthUnits = Units.NATIVE
    ) -> float:
        """
        Gets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            unit: Units of datum.

        Returns:
            The datum.
        """
        request = main_pb2.ObjectiveChangerSetRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        await call_async("objective_changer/get_datum", request, response)
        return response.value

    def set_focus_datum(
            self,
            datum: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            datum: Value of datum.
            unit: Units of datum.
        """
        request = main_pb2.ObjectiveChangerSetRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.value = datum
        request.unit = units_from_literals(unit).value
        call("objective_changer/set_datum", request)

    async def set_focus_datum_async(
            self,
            datum: float,
            unit: LengthUnits = Units.NATIVE
    ) -> None:
        """
        Sets the focus datum.
        The focus datum is the position that the focus stage moves to after an objective change.
        It is backed by the limit.home.offset setting.

        Args:
            datum: Value of datum.
            unit: Units of datum.
        """
        request = main_pb2.ObjectiveChangerSetRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        request.value = datum
        request.unit = units_from_literals(unit).value
        await call_async("objective_changer/set_datum", request)

    def __verify_is_changer(
            self
    ) -> None:
        """
        Checks if this is a objective changer and throws an error if it is not.
        """
        request = main_pb2.ObjectiveChangerRequest()
        request.interface_id = self.turret.connection.interface_id
        request.turret_address = self.turret.device_address
        request.focus_address = self.focus_axis.device.device_address
        request.focus_axis = self.focus_axis.axis_number
        call_sync("objective_changer/verify", request)

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the device.

        Returns:
            A string that represents the device.
        """
        request = main_pb2.AxisToStringRequest()
        request.interface_id = self.turret.connection.interface_id
        request.device = self.turret.device_address
        response = main_pb2.StringResponse()
        call_sync("device/device_to_string", request, response)
        return response.value
