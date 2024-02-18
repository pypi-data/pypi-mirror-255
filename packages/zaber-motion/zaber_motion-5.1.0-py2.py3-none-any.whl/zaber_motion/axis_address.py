# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from .protobufs import main_pb2


class AxisAddress:
    """
    Holds device address and axis number.
    """

    def __init__(
            self: 'AxisAddress',
            device: int,
            axis: int
    ) -> None:
        self._device = device
        self._axis = axis

    @property
    def device(self) -> int:
        """
        Device address.
        """

        return self._device

    @device.setter
    def device(self, value: int) -> None:
        self._device = value

    @property
    def axis(self) -> int:
        """
        Axis number.
        """

        return self._axis

    @axis.setter
    def axis(self, value: int) -> None:
        self._axis = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.AxisAddress
    ) -> 'AxisAddress':
        instance = AxisAddress.__new__(
            AxisAddress
        )  # type: AxisAddress
        instance.device = pb_data.device
        instance.axis = pb_data.axis
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[AxisAddress]') -> main_pb2.AxisAddress:
        pb_data = main_pb2.AxisAddress()

        if source is None:
            return pb_data

        if not isinstance(source, AxisAddress):
            raise TypeError("Provided value is not AxisAddress.")

        pb_data.device = source.device
        pb_data.axis = source.axis
        return pb_data
