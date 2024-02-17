# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from ..protobufs import main_pb2
from ..units import UnitsAndLiterals, Units, units_from_literals


class GetAxisSetting:
    """
    Specifies a setting to get with one of the multi-get commands.
    """

    def __init__(
            self: 'GetAxisSetting',
            setting: str,
            unit: Optional[UnitsAndLiterals] = None
    ) -> None:
        self._setting = setting
        self._unit = unit

    @property
    def setting(self) -> str:
        """
        The setting to read.
        """

        return self._setting

    @setting.setter
    def setting(self, value: str) -> None:
        self._setting = value

    @property
    def unit(self) -> Optional[UnitsAndLiterals]:
        """
        The unit to convert the read setting to.
        """

        return self._unit

    @unit.setter
    def unit(self, value: Optional[UnitsAndLiterals]) -> None:
        self._unit = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def to_protobuf(source: 'Optional[GetAxisSetting]') -> main_pb2.GetSetting:
        pb_data = main_pb2.GetSetting()

        if source is None:
            return pb_data

        if not isinstance(source, GetAxisSetting):
            raise TypeError("Provided value is not GetAxisSetting.")

        pb_data.setting = source.setting
        pb_data.unit = units_from_literals(source.unit or Units.NATIVE).value
        return pb_data
