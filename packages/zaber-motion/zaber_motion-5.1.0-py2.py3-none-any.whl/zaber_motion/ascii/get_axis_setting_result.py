# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from ..units import UnitsAndLiterals, Units


class GetAxisSettingResult:
    """
    The response from a multi-get axis command.
    """

    @property
    def setting(self) -> str:
        """
        The setting read.
        """

        return self._setting

    @setting.setter
    def setting(self, value: str) -> None:
        self._setting = value

    @property
    def value(self) -> float:
        """
        The value read.
        """

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def unit(self) -> UnitsAndLiterals:
        """
        The unit of the values.
        """

        return self._unit

    @unit.setter
    def unit(self, value: UnitsAndLiterals) -> None:
        self._unit = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.GetSettingResult
    ) -> 'GetAxisSettingResult':
        instance = GetAxisSettingResult.__new__(
            GetAxisSettingResult
        )  # type: GetAxisSettingResult
        instance.setting = pb_data.setting
        instance.value = pb_data.values[0]
        instance.unit = Units(pb_data.unit)
        return instance
