# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from .protobufs import main_pb2
from .units import UnitsAndLiterals, Units, units_from_literals


class Measurement:
    """
    Represents a numerical value with optional units specified.
    """

    def __init__(
            self: 'Measurement',
            value: float,
            unit: Optional[UnitsAndLiterals] = None
    ) -> None:
        self._value = value
        self._unit = unit

    @property
    def value(self) -> float:
        """
        Value of the measurement.
        """

        return self._value

    @value.setter
    def value(self, value: float) -> None:
        self._value = value

    @property
    def unit(self) -> Optional[UnitsAndLiterals]:
        """
        Optional units of the measurement.
        """

        return self._unit

    @unit.setter
    def unit(self, value: Optional[UnitsAndLiterals]) -> None:
        self._unit = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.Measurement
    ) -> 'Measurement':
        instance = Measurement.__new__(
            Measurement
        )  # type: Measurement
        instance.value = pb_data.value
        instance.unit = Units(pb_data.unit)
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[Measurement]') -> main_pb2.Measurement:
        pb_data = main_pb2.Measurement()

        if source is None:
            pb_data.is_null = True
            return pb_data

        if not isinstance(source, Measurement):
            raise TypeError("Provided value is not Measurement.")

        pb_data.value = source.value
        pb_data.unit = units_from_literals(source.unit or Units.NATIVE).value
        return pb_data
