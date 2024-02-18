# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync
from ..protobufs import main_pb2
from ..ascii import Axis, AxisSettings, AxisStorage, Warnings, Response

if TYPE_CHECKING:
    from .illuminator import Illuminator


class IlluminatorChannel:
    """
    Use to control a channel (LED lamp) on an illuminator.
    It is subject to breaking changes without warning until further notice.
    Requires at least Firmware 7.09.
    """

    @property
    def illuminator(self) -> 'Illuminator':
        """
        Illuminator of this channel.
        """
        return self._illuminator

    @property
    def channel_number(self) -> int:
        """
        The channel number identifies the channel on the illuminator.
        """
        return self._channel_number

    @property
    def settings(self) -> AxisSettings:
        """
        Settings and properties of this channel.
        """
        return self._settings

    @property
    def storage(self) -> AxisStorage:
        """
        Key-value storage of this channel.
        """
        return self._storage

    @property
    def warnings(self) -> Warnings:
        """
        Warnings and faults of this channel.
        """
        return self._warnings

    def __init__(self, illuminator: 'Illuminator', channel_number: int):
        self._illuminator = illuminator
        self._channel_number = channel_number
        self._axis = Axis(illuminator.device, channel_number)
        self._settings = AxisSettings(self._axis)
        self._storage = AxisStorage(self._axis)
        self._warnings = Warnings(illuminator.device, channel_number)

    def on(
            self
    ) -> None:
        """
        Turns this channel on.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = True
        call("illuminator/on", request)

    async def on_async(
            self
    ) -> None:
        """
        Turns this channel on.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = True
        await call_async("illuminator/on", request)

    def off(
            self
    ) -> None:
        """
        Turns this channel off.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = False
        call("illuminator/on", request)

    async def off_async(
            self
    ) -> None:
        """
        Turns this channel off.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = False
        await call_async("illuminator/on", request)

    def set_on(
            self,
            on: bool
    ) -> None:
        """
        Turns this channel on or off.

        Args:
            on: True to turn channel on, false to turn it off.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = on
        call("illuminator/on", request)

    async def set_on_async(
            self,
            on: bool
    ) -> None:
        """
        Turns this channel on or off.

        Args:
            on: True to turn channel on, false to turn it off.
        """
        request = main_pb2.ChannelOn()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.on = on
        await call_async("illuminator/on", request)

    def is_on(
            self
    ) -> bool:
        """
        Checks if this channel is on.

        Returns:
            True if channel is on, false otherwise.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.BoolResponse()
        call("illuminator/is_on", request, response)
        return response.value

    async def is_on_async(
            self
    ) -> bool:
        """
        Checks if this channel is on.

        Returns:
            True if channel is on, false otherwise.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.BoolResponse()
        await call_async("illuminator/is_on", request, response)
        return response.value

    def set_intensity(
            self,
            intensity: float
    ) -> None:
        """
        Sets channel intensity as a fraction of the maximum flux.

        Args:
            intensity: Fraction of intensity to set (between 0 and 1).
        """
        request = main_pb2.ChannelSetIntensity()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.intensity = intensity
        call("illuminator/set_intensity", request)

    async def set_intensity_async(
            self,
            intensity: float
    ) -> None:
        """
        Sets channel intensity as a fraction of the maximum flux.

        Args:
            intensity: Fraction of intensity to set (between 0 and 1).
        """
        request = main_pb2.ChannelSetIntensity()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.intensity = intensity
        await call_async("illuminator/set_intensity", request)

    def get_intensity(
            self
    ) -> float:
        """
        Gets the current intensity of this channel.

        Returns:
            Current intensity as fraction of maximum flux.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.DoubleResponse()
        call("illuminator/get_intensity", request, response)
        return response.value

    async def get_intensity_async(
            self
    ) -> float:
        """
        Gets the current intensity of this channel.

        Returns:
            Current intensity as fraction of maximum flux.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.DoubleResponse()
        await call_async("illuminator/get_intensity", request, response)
        return response.value

    def generic_command(
            self,
            command: str,
            check_errors: bool = True,
            timeout: int = 0
    ) -> Response:
        """
        Sends a generic ASCII command to this channel.
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
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
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
        Sends a generic ASCII command to this channel.
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
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
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
        Sends a generic ASCII command to this channel and expects multiple responses.
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
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
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
        Sends a generic ASCII command to this channel and expects multiple responses.
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
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
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
        Sends a generic ASCII command to this channel without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.command = command
        call("interface/generic_command_no_response", request)

    async def generic_command_no_response_async(
            self,
            command: str
    ) -> None:
        """
        Sends a generic ASCII command to this channel without expecting a response and without adding a message ID
        For more information refer to: [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_commands).

        Args:
            command: Command and its parameters.
        """
        request = main_pb2.GenericCommandRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.command = command
        await call_async("interface/generic_command_no_response", request)

    def get_state(
            self
    ) -> str:
        """
        Returns a serialization of the current channel state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the channel.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.StringResponse()
        call("device/get_state", request, response)
        return response.value

    async def get_state_async(
            self
    ) -> str:
        """
        Returns a serialization of the current channel state that can be saved and reapplied.

        Returns:
            A serialization of the current state of the channel.
        """
        request = main_pb2.AxisEmptyRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        response = main_pb2.StringResponse()
        await call_async("device/get_state", request, response)
        return response.value

    def set_state(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to this channel.

        Args:
            state: The state object to apply to this channel.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.state = state
        call("device/set_state", request)

    async def set_state_async(
            self,
            state: str
    ) -> None:
        """
        Applies a saved state to this channel.

        Args:
            state: The state object to apply to this channel.
        """
        request = main_pb2.SetStateRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.state = state
        await call_async("device/set_state", request)

    def can_set_state(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this channel.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this channel.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        call("device/can_set_axis_state", request, response)
        return response.error

    async def can_set_state_async(
            self,
            state: str
    ) -> str:
        """
        Checks if a state can be applied to this channel.
        This only covers exceptions that can be determined statically such as mismatches of ID or version,
        the process of applying the state can still fail when running.

        Args:
            state: The state object to check against.

        Returns:
            An explanation of why this state cannot be set to this channel.
        """
        request = main_pb2.CanSetStateRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.state = state
        response = main_pb2.CanSetStateAxisResponse()
        await call_async("device/can_set_axis_state", request, response)
        return response.error

    def __repr__(
            self
    ) -> str:
        """
        Returns a string that represents the channel.

        Returns:
            A string that represents the channel.
        """
        request = main_pb2.AxisToStringRequest()
        request.interface_id = self.illuminator.device.connection.interface_id
        request.device = self.illuminator.device.device_address
        request.axis = self.channel_number
        request.type_override = "Channel"
        response = main_pb2.StringResponse()
        call_sync("device/axis_to_string", request, response)
        return response.value
