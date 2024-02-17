# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import TYPE_CHECKING, List
from ..call import call, call_async, call_sync

from ..protobufs import main_pb2
from ..units import UnitsAndLiterals, Units, units_from_literals
from .conversion_factor import ConversionFactor

from .get_axis_setting import GetAxisSetting
from .get_axis_setting_result import GetAxisSettingResult

if TYPE_CHECKING:
    from .axis import Axis


class AxisSettings:
    """
    Class providing access to various axis settings and properties.
    """

    def __init__(self, axis: 'Axis'):
        self._axis = axis

    def get(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any axis setting or property.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        call("device/get_setting", request, response)
        return response.value

    async def get_async(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns any axis setting or property.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        await call_async("device/get_setting", request, response)
        return response.value

    def set(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any axis setting.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = units_from_literals(unit).value
        call("device/set_setting", request)

    async def set_async(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> None:
        """
        Sets any axis setting.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
            unit: Units of setting.
        """
        request = main_pb2.DeviceSetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = units_from_literals(unit).value
        await call_async("device/set_setting", request)

    def get_string(
            self,
            setting: str
    ) -> str:
        """
        Returns any axis setting or property as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.StringResponse()
        call("device/get_setting_str", request, response)
        return response.value

    async def get_string_async(
            self,
            setting: str
    ) -> str:
        """
        Returns any axis setting or property as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.StringResponse()
        await call_async("device/get_setting_str", request, response)
        return response.value

    def set_string(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any axis setting as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingStrRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        call("device/set_setting_str", request)

    async def set_string_async(
            self,
            setting: str,
            value: str
    ) -> None:
        """
        Sets any axis setting as a string.
        For more information refer to the [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_settings).

        Args:
            setting: Name of the setting.
            value: Value of the setting.
        """
        request = main_pb2.DeviceSetSettingStrRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        await call_async("device/set_setting_str", request)

    def convert_to_native_units(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals
    ) -> float:
        """
        Convert arbitrary setting value to Zaber native units.

        Args:
            setting: Name of the setting.
            value: Value of the setting in units specified by following argument.
            unit: Units of the value.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceConvertSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.value = value
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        call_sync("device/convert_setting", request, response)
        return response.value

    def convert_from_native_units(
            self,
            setting: str,
            value: float,
            unit: UnitsAndLiterals
    ) -> float:
        """
        Convert arbitrary setting value from Zaber native units.

        Args:
            setting: Name of the setting.
            value: Value of the setting in Zaber native units.
            unit: Units to convert value to.

        Returns:
            Setting value.
        """
        request = main_pb2.DeviceConvertSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.from_native = True
        request.setting = setting
        request.value = value
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        call_sync("device/convert_setting", request, response)
        return response.value

    def get_default(
            self,
            setting: str,
            unit: UnitsAndLiterals = Units.NATIVE
    ) -> float:
        """
        Returns the default value of a setting.

        Args:
            setting: Name of the setting.
            unit: Units of setting.

        Returns:
            Default setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        request.unit = units_from_literals(unit).value
        response = main_pb2.DoubleResponse()
        call_sync("device/get_setting_default", request, response)
        return response.value

    def get_default_string(
            self,
            setting: str
    ) -> str:
        """
        Returns the default value of a setting as a string.

        Args:
            setting: Name of the setting.

        Returns:
            Default setting value.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.StringResponse()
        call_sync("device/get_setting_default_str", request, response)
        return response.value

    def can_convert_native_units(
            self,
            setting: str
    ) -> bool:
        """
        Indicates if given setting can be converted from and to native units.

        Args:
            setting: Name of the setting.

        Returns:
            True if unit conversion can be performed.
        """
        request = main_pb2.DeviceGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.setting = setting
        response = main_pb2.BoolResponse()
        call_sync("device/can_convert_setting", request, response)
        return response.value

    def set_custom_unit_conversions(
            self,
            conversions: List[ConversionFactor]
    ) -> None:
        """
        Overrides default unit conversions.
        Conversion factors are specified by setting names representing underlying dimensions.
        Requires at least Firmware 7.30.

        Args:
            conversions: Factors of all conversions to override.
        """
        request = main_pb2.DeviceSetUnitConversionsRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.conversions.extend([ConversionFactor.to_protobuf(a) for a in conversions])
        call("device/set_unit_conversions", request)

    async def set_custom_unit_conversions_async(
            self,
            conversions: List[ConversionFactor]
    ) -> None:
        """
        Overrides default unit conversions.
        Conversion factors are specified by setting names representing underlying dimensions.
        Requires at least Firmware 7.30.

        Args:
            conversions: Factors of all conversions to override.
        """
        request = main_pb2.DeviceSetUnitConversionsRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.conversions.extend([ConversionFactor.to_protobuf(a) for a in conversions])
        await call_async("device/set_unit_conversions", request)

    def get_many(
            self,
            *settings: GetAxisSetting
    ) -> List[GetAxisSettingResult]:
        """
        Gets many setting values in as few requests as possible.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = main_pb2.DeviceMultiGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.settings.extend([GetAxisSetting.to_protobuf(a) for a in settings])
        response = main_pb2.GetSettingResults()
        call("device/get_many_settings", request, response)
        return [GetAxisSettingResult.from_protobuf(a) for a in response.results]

    async def get_many_async(
            self,
            *settings: GetAxisSetting
    ) -> List[GetAxisSettingResult]:
        """
        Gets many setting values in as few requests as possible.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = main_pb2.DeviceMultiGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.settings.extend([GetAxisSetting.to_protobuf(a) for a in settings])
        response = main_pb2.GetSettingResults()
        await call_async("device/get_many_settings", request, response)
        return [GetAxisSettingResult.from_protobuf(a) for a in response.results]

    def get_synchronized(
            self,
            *settings: GetAxisSetting
    ) -> List[GetAxisSettingResult]:
        """
        Gets many setting values in the same tick, ensuring their values are synchronized.
        Requires at least Firmware 7.35.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = main_pb2.DeviceMultiGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.settings.extend([GetAxisSetting.to_protobuf(a) for a in settings])
        response = main_pb2.GetSettingResults()
        call("device/get_sync_settings", request, response)
        return [GetAxisSettingResult.from_protobuf(a) for a in response.results]

    async def get_synchronized_async(
            self,
            *settings: GetAxisSetting
    ) -> List[GetAxisSettingResult]:
        """
        Gets many setting values in the same tick, ensuring their values are synchronized.
        Requires at least Firmware 7.35.

        Args:
            settings: The settings to read.

        Returns:
            The setting values read.
        """
        request = main_pb2.DeviceMultiGetSettingRequest()
        request.interface_id = self._axis.device.connection.interface_id
        request.device = self._axis.device.device_address
        request.axis = self._axis.axis_number
        request.settings.extend([GetAxisSetting.to_protobuf(a) for a in settings])
        response = main_pb2.GetSettingResults()
        await call_async("device/get_sync_settings", request, response)
        return [GetAxisSettingResult.from_protobuf(a) for a in response.results]
