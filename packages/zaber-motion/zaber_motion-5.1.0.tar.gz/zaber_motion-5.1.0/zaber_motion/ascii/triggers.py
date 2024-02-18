# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import TYPE_CHECKING, List
from ..protobufs import main_pb2
from ..call import call, call_async
from .trigger import Trigger
from .trigger_state import TriggerState
from .trigger_enabled_state import TriggerEnabledState

if TYPE_CHECKING:
    from .device import Device


class Triggers:
    """
    Class providing access to device triggers.
    Please note that the Triggers API is currently an experimental feature.
    Requires at least Firmware 7.06.
    """

    @property
    def device(self) -> 'Device':
        """
        Device that these triggers belong to.
        """
        return self._device

    def __init__(self, device: 'Device'):
        self._device = device

    def get_number_of_triggers(
            self
    ) -> int:
        """
        Get the number of triggers for this device.

        Returns:
            Number of triggers for this device.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.setting = "trigger.numtriggers"
        response = main_pb2.IntResponse()
        call("triggers/get_setting", request, response)
        return response.value

    async def get_number_of_triggers_async(
            self
    ) -> int:
        """
        Get the number of triggers for this device.

        Returns:
            Number of triggers for this device.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.setting = "trigger.numtriggers"
        response = main_pb2.IntResponse()
        await call_async("triggers/get_setting", request, response)
        return response.value

    def get_number_of_actions(
            self
    ) -> int:
        """
        Get the number of actions for each trigger for this device.

        Returns:
            Number of actions for each trigger for this device.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.setting = "trigger.numactions"
        response = main_pb2.IntResponse()
        call("triggers/get_setting", request, response)
        return response.value

    async def get_number_of_actions_async(
            self
    ) -> int:
        """
        Get the number of actions for each trigger for this device.

        Returns:
            Number of actions for each trigger for this device.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        request.setting = "trigger.numactions"
        response = main_pb2.IntResponse()
        await call_async("triggers/get_setting", request, response)
        return response.value

    def get_trigger(
            self,
            trigger_number: int
    ) -> 'Trigger':
        """
        Get a specific trigger for this device.

        Args:
            trigger_number: The number of the trigger to control. Trigger numbers start at 1.

        Returns:
            Trigger instance.
        """
        if trigger_number <= 0:
            raise ValueError('Invalid value; triggers are numbered from 1.')

        return Trigger(self.device, trigger_number)

    def get_trigger_states(
            self
    ) -> List[TriggerState]:
        """
        Get the state for every trigger for this device.

        Returns:
            Complete state for every trigger.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        response = main_pb2.TriggerStates()
        call("triggers/get_trigger_states", request, response)
        return [TriggerState.from_protobuf(a) for a in response.states]

    async def get_trigger_states_async(
            self
    ) -> List[TriggerState]:
        """
        Get the state for every trigger for this device.

        Returns:
            Complete state for every trigger.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        response = main_pb2.TriggerStates()
        await call_async("triggers/get_trigger_states", request, response)
        return [TriggerState.from_protobuf(a) for a in response.states]

    def get_enabled_states(
            self
    ) -> List[TriggerEnabledState]:
        """
        Gets the enabled state for every trigger for this device.

        Returns:
            Whether triggers are enabled and the number of times they will fire.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        response = main_pb2.TriggerEnabledStates()
        call("triggers/get_enabled_states", request, response)
        return [TriggerEnabledState.from_protobuf(a) for a in response.states]

    async def get_enabled_states_async(
            self
    ) -> List[TriggerEnabledState]:
        """
        Gets the enabled state for every trigger for this device.

        Returns:
            Whether triggers are enabled and the number of times they will fire.
        """
        request = main_pb2.DeviceEmptyRequest()
        request.interface_id = self.device.connection.interface_id
        request.device = self.device.device_address
        response = main_pb2.TriggerEnabledStates()
        await call_async("triggers/get_enabled_states", request, response)
        return [TriggerEnabledState.from_protobuf(a) for a in response.states]
