# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List  # pylint: disable=unused-import
from ..protobufs import main_pb2
from ..units import UnitsAndLiterals, Units


class GetSettingResult:
    """
    The response from a multi-get command.
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
    def values(self) -> List[float]:
        """
        The list of values returned.
        """

        return self._values

    @values.setter
    def values(self, value: List[float]) -> None:
        self._values = value

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
    ) -> 'GetSettingResult':
        instance = GetSettingResult.__new__(
            GetSettingResult
        )  # type: GetSettingResult
        instance.setting = pb_data.setting
        instance.values = list(pb_data.values)
        instance.unit = Units(pb_data.unit)
        return instance
