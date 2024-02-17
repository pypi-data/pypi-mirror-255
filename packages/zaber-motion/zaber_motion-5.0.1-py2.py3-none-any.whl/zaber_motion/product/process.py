# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from ..ascii.warnings import Warnings
from ..ascii.response import Response
from ..measurement import Measurement
from ..ascii.axis import Axis
from ..ascii.axis_settings import AxisSettings
from ..ascii.storage import AxisStorage
from .process_controller_mode import ProcessControllerMode
from .process_controller_source import ProcessControllerSource

if TYPE_CHECKING:
    from .process_controller import ProcessController


class Process:
    """
    Use to drive voltage for a process such as a heater, valve, Peltier device, etc.
    Requires at least Firmware 7.35.
    """

    @property
    def controller(self) -> 'ProcessController':
        """
        Controller for this process.
        """
        return self._controller

    @property
    def process_number(self) -> int:
        """
        The process number identifies the process on the controller.
        """
        return self._process_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this process.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this process.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this process.
        """
        return self._warnings

    def __init__(self, controller: 'ProcessController', process_number: int):
        self._controller = controller
        self._process_number = process_number
        self._axis = Axis(controller.device, process_number)
        self._settings = AxisSettings(self._axis)
        self._storage = AxisStorage(self._axis)
        self._warnings = Warnings(controller.device, process_number)

    def enable(
            self,
            enabled: bool = True
    ) -> None:
        """
        Sets the enabled state of the driver.

        Args:
            enabled: If true (default) enables drive. If false disables.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = enabled
        call("process-controller/enable", request)

    async def enable_async(
            self,
            enabled: bool = True
    ) -> None:
        """
        Sets the enabled state of the driver.

        Args:
            enabled: If true (default) enables drive. If false disables.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = enabled
        await call_async("process-controller/enable", request)

    def on(
            self,
            duration: float = 0
    ) -> None:
        """
        Turns this process on. In manual mode, this supplies voltage; in controlled mode, it starts the control loop.

        Args:
            duration: How long to leave the process on in milliseconds.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = True
        request.duration = duration
        call("process-controller/on", request)

    async def on_async(
            self,
            duration: float = 0
    ) -> None:
        """
        Turns this process on. In manual mode, this supplies voltage; in controlled mode, it starts the control loop.

        Args:
            duration: How long to leave the process on in milliseconds.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = True
        request.duration = duration
        await call_async("process-controller/on", request)

    def off(
            self
    ) -> None:
        """
        Turns this process off.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = False
        call("process-controller/on", request)

    async def off_async(
            self
    ) -> None:
        """
        Turns this process off.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = False
        await call_async("process-controller/on", request)

    def set_mode(
            self,
            mode: ProcessControllerMode
    ) -> None:
        """
        Sets the control mode of this process.

        Args:
            mode: Mode to set this process to.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.setting = "process.control.mode"
        request.value = mode.value
        call("device/set_setting", request)

    async def set_mode_async(
            self,
            mode: ProcessControllerMode
    ) -> None:
        """
        Sets the control mode of this process.

        Args:
            mode: Mode to set this process to.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.setting = "process.control.mode"
        request.value = mode.value
        await call_async("device/set_setting", request)

    def get_mode(
            self
    ) -> ProcessControllerMode:
        """
        Gets the control mode of this process.

        Returns:
            Control mode.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.setting = "process.control.mode"
        response = main_pb2.DoubleResponse()
        call("device/get_setting", request, response)
        return ProcessControllerMode(response.value)

    async def get_mode_async(
            self
    ) -> ProcessControllerMode:
        """
        Gets the control mode of this process.

        Returns:
            Control mode.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.setting = "process.control.mode"
        response = main_pb2.DoubleResponse()
        await call_async("device/get_setting", request, response)
        return ProcessControllerMode(response.value)

    def get_source(
            self
    ) -> ProcessControllerSource:
        """
        Gets the source used to control this process.

        Returns:
            The source providing feedback for this process.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.ProcessControllerSource()
        call("process_controller/get_source", request, response)
        return ProcessControllerSource.from_protobuf(response)

    async def get_source_async(
            self
    ) -> ProcessControllerSource:
        """
        Gets the source used to control this process.

        Returns:
            The source providing feedback for this process.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.ProcessControllerSource()
        await call_async("process_controller/get_source", request, response)
        return ProcessControllerSource.from_protobuf(response)

    def set_source(
            self,
            source: ProcessControllerSource
    ) -> None:
        """
        Sets the source used to control this process.

        Args:
            source: Sets the source that should provide feedback for this process.
        """
        request = main_pb2.SetProcessControllerSource()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.source.CopyFrom(ProcessControllerSource.to_protobuf(source))
        call("process_controller/set_source", request)

    async def set_source_async(
            self,
            source: ProcessControllerSource
    ) -> None:
        """
        Sets the source used to control this process.

        Args:
            source: Sets the source that should provide feedback for this process.
        """
        request = main_pb2.SetProcessControllerSource()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.source.CopyFrom(ProcessControllerSource.to_protobuf(source))
        await call_async("process_controller/set_source", request)

    def get_input(
            self
    ) -> Measurement:
        """
        Gets the current value of the source used to control this process.

        Returns:
            The current value of this process's controlling source.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.Measurement()
        call("process_controller/get_input", request, response)
        return Measurement.from_protobuf(response)

    async def get_input_async(
            self
    ) -> Measurement:
        """
        Gets the current value of the source used to control this process.

        Returns:
            The current value of this process's controlling source.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.Measurement()
        await call_async("process_controller/get_input", request, response)
        return Measurement.from_protobuf(response)

    def bridge(
            self
    ) -> None:
        """
        Creates an H-bridge between this process and its neighbor. This method is only callable on axis 1 and 3.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = True
        call("process_controller/bridge", request)

    async def bridge_async(
            self
    ) -> None:
        """
        Creates an H-bridge between this process and its neighbor. This method is only callable on axis 1 and 3.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = True
        await call_async("process_controller/bridge", request)

    def unbridge(
            self
    ) -> None:
        """
        Breaks the H-bridge between this process and its neighbor, allowing them to be independently controlled.
        This method is only callable on axis 1 and 3.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = False
        call("process_controller/bridge", request)

    async def unbridge_async(
            self
    ) -> None:
        """
        Breaks the H-bridge between this process and its neighbor, allowing them to be independently controlled.
        This method is only callable on axis 1 and 3.
        """
        request = main_pb2.ProcessOn()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.on = False
        await call_async("process_controller/bridge", request)

    def is_bridge(
            self
    ) -> bool:
        """
        Detects if the given process is in bridging mode.

        Returns:
            Whether this process is bridged with its neighbor.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.BoolResponse()
        call("process_controller/is_bridge", request, response)
        return response.value

    async def is_bridge_async(
            self
    ) -> bool:
        """
        Detects if the given process is in bridging mode.

        Returns:
            Whether this process is bridged with its neighbor.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.BoolResponse()
        await call_async("process_controller/is_bridge", request, response)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this process' underlying axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        call("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    async def generic_command_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this process' underlying axis.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when the device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            A response to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponse()
        await call_async("interface/generic_command", request, response)
        return Response.from_protobuf(response)

    def generic_command_multi_response(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this process and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        call("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(a) for a in response.responses]

    async def generic_command_multi_response_async(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> List[Response]:
        """
        Sends a generic ASCII command to this process and expect multiple responses.
        Responses are returned in order of arrival.
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
            check_errors: Controls whether to throw an exception when a device rejects the command.
            timeout: The timeout, in milliseconds, for a device to respond to the command.
                Overrides the connection default request timeout.

        Returns:
            All responses to the command.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        request.check_errors = check_errors
        request.timeout = timeout
        response = main_pb2.GenericCommandResponseCollection()
        await call_async("interface/generic_command_multi_response", request, response)
        return [Response.from_protobuf(a) for a in response.responses]

    def generic_command_no_response(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this process without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this process without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.command = command
        await call_async("interface/generic_command_no_response", request)

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current process state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the process.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.StringResponse()
        call("device/get_state", request, response)
        return response.value

    async def get_state_async(
            self
    ) -> str:
        """
        Returns a serialization of the current process state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the process.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        response = main_pb2.StringResponse()
        await call_async("device/get_state", request, response)
        return response.value

    def set_state(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to this process.

        Args:
            state: The state object to apply to this process.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.state = state
        call("device/set_state", request)

    async def set_state_async(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to this process.

        Args:
            state: The state object to apply to this process.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.state = state
        await call_async("device/set_state", request)

    def can_set_state(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this process.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this process.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        call("device/can_set_axis_state", request, response)
        return response.error

    async def can_set_state_async(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this process.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this process.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        await call_async("device/can_set_axis_state", request, response)
        return response.error

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the process.

        Returns:
            A string that represents the process.
        """
        request = main_pb2.AxisToStringRequest()
        request.interface_id = self.controller.device.connection.interface_id
        request.device = self.controller.device.device_address
        request.axis = self.process_number
        request.type_override = "Process"
        response = main_pb2.StringResponse()
        call_sync("device/axis_to_string", request, response)
        return response.value
