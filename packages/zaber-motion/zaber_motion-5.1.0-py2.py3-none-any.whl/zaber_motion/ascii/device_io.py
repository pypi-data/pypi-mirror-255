# pylint: disable=dangerous-default-value
# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async
from ..units import Units, units_from_literals, TimeUnits
from .device_io_info import DeviceIOInfo
from .digital_output_action import DigitalOutputAction

from ..protobufs import main_pb2

if TYPE_CHECKING:
    from .device import Device


class DeviceIO:
    """
    Class providing access to the I/O channels of the device.
    """

    def __init__(self, device: 'Device'):
        self._device = device

    def get_all_digital_inputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        call("device/get_all_digital_io", request, response)
        return list(response.values)

    async def get_all_digital_inputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital input channels.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        await call_async("device/get_all_digital_io", request, response)
        return list(response.values)

    def get_all_digital_outputs(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        call("device/get_all_digital_io", request, response)
        return list(response.values)

    async def get_all_digital_outputs_async(
            self
    ) -> List[bool]:
        """
        Returns the current values of all digital output channels.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetAllDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        response = main_pb2.DeviceGetAllDigitalIOResponse()
        await call_async("device/get_all_digital_io", request, response)
        return list(response.values)

    def get_all_analog_inputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
             Measurements of the voltage present on the input channels.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        call("device/get_all_analog_io", request, response)
        return list(response.values)

    async def get_all_analog_inputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog input channels.

        Returns:
             Measurements of the voltage present on the input channels.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        await call_async("device/get_all_analog_io", request, response)
        return list(response.values)

    def get_all_analog_outputs(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
             Measurements of voltage that the output channels are conducting.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        call("device/get_all_analog_io", request, response)
        return list(response.values)

    async def get_all_analog_outputs_async(
            self
    ) -> List[float]:
        """
        Returns the current values of all analog output channels.

        Returns:
             Measurements of voltage that the output channels are conducting.
        """
        request = main_pb2.DeviceGetAllAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        response = main_pb2.DeviceGetAllAnalogIOResponse()
        await call_async("device/get_all_analog_io", request, response)
        return list(response.values)

    def get_digital_input(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        request.channel_number = channel_number
        response = main_pb2.BoolResponse()
        call("device/get_digital_io", request, response)
        return response.value

    async def get_digital_input_async(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if voltage is present on the input channel and false otherwise.
        """
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "di"
        request.channel_number = channel_number
        response = main_pb2.BoolResponse()
        await call_async("device/get_digital_io", request, response)
        return response.value

    def get_digital_output(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        request.channel_number = channel_number
        response = main_pb2.BoolResponse()
        call("device/get_digital_io", request, response)
        return response.value

    async def get_digital_output_async(
            self,
            channel_number: int
    ) -> bool:
        """
        Returns the current value of the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            True if the output channel is conducting and false otherwise.
        """
        request = main_pb2.DeviceGetDigitalIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "do"
        request.channel_number = channel_number
        response = main_pb2.BoolResponse()
        await call_async("device/get_digital_io", request, response)
        return response.value

    def get_analog_input(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current value of the specified analog input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
             A measurementsof the voltage present on the input channel.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        request.channel_number = channel_number
        response = main_pb2.DoubleResponse()
        call("device/get_analog_io", request, response)
        return response.value

    async def get_analog_input_async(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current value of the specified analog input channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
             A measurementsof the voltage present on the input channel.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ai"
        request.channel_number = channel_number
        response = main_pb2.DoubleResponse()
        await call_async("device/get_analog_io", request, response)
        return response.value

    def get_analog_output(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current values of the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            A measurement of voltage that the output channel is conducting.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        request.channel_number = channel_number
        response = main_pb2.DoubleResponse()
        call("device/get_analog_io", request, response)
        return response.value

    async def get_analog_output_async(
            self,
            channel_number: int
    ) -> float:
        """
        Returns the current values of the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.

        Returns:
            A measurement of voltage that the output channel is conducting.
        """
        request = main_pb2.DeviceGetAnalogIORequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_type = "ao"
        request.channel_number = channel_number
        response = main_pb2.DoubleResponse()
        await call_async("device/get_analog_io", request, response)
        return response.value

    def set_all_digital_outputs(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = main_pb2.DeviceSetAllDigitalOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend([x.value for x in values])
        call("device/set_all_digital_outputs", request)

    async def set_all_digital_outputs_async(
            self,
            values: List[DigitalOutputAction]
    ) -> None:
        """
        Sets values for all digital output channels.

        Args:
            values: The type of action to perform on the channel.
        """
        request = main_pb2.DeviceSetAllDigitalOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend([x.value for x in values])
        await call_async("device/set_all_digital_outputs", request)

    def set_all_digital_outputs_schedule(
            self,
            values: List[DigitalOutputAction],
            future_values: List[DigitalOutputAction],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for all digital output channels.
        Requires at least Firmware 7.37.

        Args:
            values: The type of actions to perform immediately on output channels.
            future_values: The type of actions to perform in the future on output channels.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = main_pb2.DeviceSetAllDigitalOutputsScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend([x.value for x in values])
        request.future_values.extend([x.value for x in future_values])
        request.delay = delay
        request.unit = units_from_literals(unit).value
        call("device/set_all_digital_outputs_schedule", request)

    async def set_all_digital_outputs_schedule_async(
            self,
            values: List[DigitalOutputAction],
            future_values: List[DigitalOutputAction],
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for all digital output channels.
        Requires at least Firmware 7.37.

        Args:
            values: The type of actions to perform immediately on output channels.
            future_values: The type of actions to perform in the future on output channels.
            delay: Delay between setting current values and setting future values.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = main_pb2.DeviceSetAllDigitalOutputsScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend([x.value for x in values])
        request.future_values.extend([x.value for x in future_values])
        request.delay = delay
        request.unit = units_from_literals(unit).value
        await call_async("device/set_all_digital_outputs_schedule", request)

    def cancel_all_digital_outputs_schedule(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled digital output actions.
        Requires at least Firmware 7.37.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled digital output action for that channel.
        """
        request = main_pb2.DeviceCancelAllDigitalOutputsScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channels.extend(channels)
        call("device/cancel_all_digital_outputs_schedule", request)

    async def cancel_all_digital_outputs_schedule_async(
            self,
            channels: List[bool] = []
    ) -> None:
        """
        Cancel all scheduled digital output actions.
        Requires at least Firmware 7.37.

        Args:
            channels: Optionally specify which channels to cancel.
                Array length must be empty or equal to the number of channels on device.
                Specifying "True" for a channel will cancel the scheduled digital output action for that channel.
        """
        request = main_pb2.DeviceCancelAllDigitalOutputsScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channels.extend(channels)
        await call_async("device/cancel_all_digital_outputs_schedule", request)

    def set_all_analog_outputs(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = main_pb2.DeviceSetAllAnalogOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
        call("device/set_all_analog_outputs", request)

    async def set_all_analog_outputs_async(
            self,
            values: List[float]
    ) -> None:
        """
        Sets values for all analog output channels.

        Args:
            values: Voltage values to set the output channels to.
        """
        request = main_pb2.DeviceSetAllAnalogOutputsRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.values.extend(values)
        await call_async("device/set_all_analog_outputs", request)

    def set_digital_output(
            self,
            channel_number: int,
            value: DigitalOutputAction
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform on the channel.
        """
        request = main_pb2.DeviceSetDigitalOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value.value
        call("device/set_digital_output", request)

    async def set_digital_output_async(
            self,
            channel_number: int,
            value: DigitalOutputAction
    ) -> None:
        """
        Sets value for the specified digital output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform on the channel.
        """
        request = main_pb2.DeviceSetDigitalOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value.value
        await call_async("device/set_digital_output", request)

    def set_digital_output_schedule(
            self,
            channel_number: int,
            value: DigitalOutputAction,
            future_value: DigitalOutputAction,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified digital output channel.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform immediately on the channel.
            future_value: The type of action to perform in the future on the channel.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = main_pb2.DeviceSetDigitalOutputScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value.value
        request.future_value = future_value.value
        request.delay = delay
        request.unit = units_from_literals(unit).value
        call("device/set_digital_output_schedule", request)

    async def set_digital_output_schedule_async(
            self,
            channel_number: int,
            value: DigitalOutputAction,
            future_value: DigitalOutputAction,
            delay: float,
            unit: TimeUnits = Units.NATIVE
    ) -> None:
        """
        Sets current and future value for the specified digital output channel.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
            value: The type of action to perform immediately on the channel.
            future_value: The type of action to perform in the future on the channel.
            delay: Delay between setting current value and setting future value.
            unit: Units of time.
        """
        if delay <= 0:
            raise ValueError('Delay must be a positive value.')

        request = main_pb2.DeviceSetDigitalOutputScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value.value
        request.future_value = future_value.value
        request.delay = delay
        request.unit = units_from_literals(unit).value
        await call_async("device/set_digital_output_schedule", request)

    def cancel_digital_output_schedule(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled digital output action.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = main_pb2.DeviceCancelDigitalOutputScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        call("device/cancel_digital_output_schedule", request)

    async def cancel_digital_output_schedule_async(
            self,
            channel_number: int
    ) -> None:
        """
        Cancels a scheduled digital output action.
        Requires at least Firmware 7.37.

        Args:
            channel_number: Channel number starting at 1.
        """
        request = main_pb2.DeviceCancelDigitalOutputScheduleRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        await call_async("device/cancel_digital_output_schedule", request)

    def set_analog_output(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Sets value for the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to.
        """
        request = main_pb2.DeviceSetAnalogOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
        call("device/set_analog_output", request)

    async def set_analog_output_async(
            self,
            channel_number: int,
            value: float
    ) -> None:
        """
        Sets value for the specified analog output channel.

        Args:
            channel_number: Channel number starting at 1.
            value: Value to set the output channel voltage to.
        """
        request = main_pb2.DeviceSetAnalogOutputRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        request.channel_number = channel_number
        request.value = value
        await call_async("device/set_analog_output", request)

    def get_channels_info(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        response = main_pb2.DeviceIOInfo()
        call("device/get_io_info", request, response)
        return DeviceIOInfo.from_protobuf(response)

    async def get_channels_info_async(
            self
    ) -> DeviceIOInfo:
        """
        Returns the number of I/O channels the device has.

        Returns:
            An object containing the number of I/O channels the device has.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self._device.connection.interface_id
        request.device = self._device.device_address
        response = main_pb2.DeviceIOInfo()
        await call_async("device/get_io_info", request, response)
        return DeviceIOInfo.from_protobuf(response)
