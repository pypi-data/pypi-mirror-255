# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from ..protobufs import main_pb2
from ..axis_address import AxisAddress


class MicroscopeConfig:
    """
    Configuration representing a microscope setup.
    Device address of value 0 means that the part is not present.
    """

    def __init__(
            self: 'MicroscopeConfig',
            focus_axis: Optional[AxisAddress] = None,
            x_axis: Optional[AxisAddress] = None,
            y_axis: Optional[AxisAddress] = None,
            illuminator: Optional[int] = None,
            filter_changer: Optional[int] = None,
            objective_changer: Optional[int] = None
    ) -> None:
        self._focus_axis = focus_axis
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._illuminator = illuminator
        self._filter_changer = filter_changer
        self._objective_changer = objective_changer

    @property
    def focus_axis(self) -> Optional[AxisAddress]:
        """
        Focus axis of the microscope.
        """

        return self._focus_axis

    @focus_axis.setter
    def focus_axis(self, value: Optional[AxisAddress]) -> None:
        self._focus_axis = value

    @property
    def x_axis(self) -> Optional[AxisAddress]:
        """
        X axis of the microscope.
        """

        return self._x_axis

    @x_axis.setter
    def x_axis(self, value: Optional[AxisAddress]) -> None:
        self._x_axis = value

    @property
    def y_axis(self) -> Optional[AxisAddress]:
        """
        Y axis of the microscope.
        """

        return self._y_axis

    @y_axis.setter
    def y_axis(self, value: Optional[AxisAddress]) -> None:
        self._y_axis = value

    @property
    def illuminator(self) -> Optional[int]:
        """
        Illuminator device address.
        """

        return self._illuminator

    @illuminator.setter
    def illuminator(self, value: Optional[int]) -> None:
        self._illuminator = value

    @property
    def filter_changer(self) -> Optional[int]:
        """
        Filter changer device address.
        """

        return self._filter_changer

    @filter_changer.setter
    def filter_changer(self, value: Optional[int]) -> None:
        self._filter_changer = value

    @property
    def objective_changer(self) -> Optional[int]:
        """
        Objective changer device address.
        """

        return self._objective_changer

    @objective_changer.setter
    def objective_changer(self, value: Optional[int]) -> None:
        self._objective_changer = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.MicroscopeConfig
    ) -> 'MicroscopeConfig':
        instance = MicroscopeConfig.__new__(
            MicroscopeConfig
        )  # type: MicroscopeConfig
        instance.focus_axis = AxisAddress.from_protobuf(pb_data.focus_axis)
        instance.x_axis = AxisAddress.from_protobuf(pb_data.x_axis)
        instance.y_axis = AxisAddress.from_protobuf(pb_data.y_axis)
        instance.illuminator = pb_data.illuminator
        instance.filter_changer = pb_data.filter_changer
        instance.objective_changer = pb_data.objective_changer
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[MicroscopeConfig]') -> main_pb2.MicroscopeConfig:
        pb_data = main_pb2.MicroscopeConfig()

        if source is None:
            pb_data.focus_axis.CopyFrom(AxisAddress.to_protobuf(None))
            pb_data.x_axis.CopyFrom(AxisAddress.to_protobuf(None))
            pb_data.y_axis.CopyFrom(AxisAddress.to_protobuf(None))
            return pb_data

        if not isinstance(source, MicroscopeConfig):
            raise TypeError("Provided value is not MicroscopeConfig.")

        pb_data.focus_axis.CopyFrom(AxisAddress.to_protobuf(source.focus_axis))
        pb_data.x_axis.CopyFrom(AxisAddress.to_protobuf(source.x_axis))
        pb_data.y_axis.CopyFrom(AxisAddress.to_protobuf(source.y_axis))
        if source.illuminator is not None:
            pb_data.illuminator = source.illuminator
        if source.filter_changer is not None:
            pb_data.filter_changer = source.filter_changer
        if source.objective_changer is not None:
            pb_data.objective_changer = source.objective_changer
        return pb_data
