# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import Optional  # pylint: disable=unused-import
from ..protobufs import main_pb2
from .process_controller_source_sensor import ProcessControllerSourceSensor


class ProcessControllerSource:
    """
    The source used by a process in a closed-loop mode.
    """

    def __init__(
            self: 'ProcessControllerSource',
            sensor: ProcessControllerSourceSensor,
            port: int
    ) -> None:
        self._sensor = sensor
        self._port = port

    @property
    def sensor(self) -> ProcessControllerSourceSensor:
        """
        The type of input sensor.
        """

        return self._sensor

    @sensor.setter
    def sensor(self, value: ProcessControllerSourceSensor) -> None:
        self._sensor = value

    @property
    def port(self) -> int:
        """
        The specific input to use.
        """

        return self._port

    @port.setter
    def port(self, value: int) -> None:
        self._port = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.ProcessControllerSource
    ) -> 'ProcessControllerSource':
        instance = ProcessControllerSource.__new__(
            ProcessControllerSource
        )  # type: ProcessControllerSource
        instance.sensor = ProcessControllerSourceSensor(pb_data.sensor)
        instance.port = pb_data.port
        return instance

    @staticmethod
    def to_protobuf(source: 'Optional[ProcessControllerSource]') -> main_pb2.ProcessControllerSource:
        pb_data = main_pb2.ProcessControllerSource()

        if source is None:
            return pb_data

        if not isinstance(source, ProcessControllerSource):
            raise TypeError("Provided value is not ProcessControllerSource.")

        pb_data.sensor = source.sensor.value if source.sensor is not None else 0
        pb_data.port = source.port
        return pb_data
