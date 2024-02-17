# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from .oscilloscope_data_source import OscilloscopeDataSource
from .io_port_type import IoPortType


class OscilloscopeCaptureProperties:
    """
    The public properties of one channel of recorded oscilloscope data.
    """

    @property
    def data_source(self) -> OscilloscopeDataSource:
        """
        Indicates whether the data came from a setting or an I/O pin.
        """

        return self._data_source

    @data_source.setter
    def data_source(self, value: OscilloscopeDataSource) -> None:
        self._data_source = value

    @property
    def setting(self) -> str:
        """
        The name of the recorded setting.
        """

        return self._setting

    @setting.setter
    def setting(self, value: str) -> None:
        self._setting = value

    @property
    def axis_number(self) -> int:
        """
        The number of the axis the data was recorded from, or 0 for the controller.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def io_type(self) -> IoPortType:
        """
        Which kind of I/O port data was recorded from.
        """

        return self._io_type

    @io_type.setter
    def io_type(self, value: IoPortType) -> None:
        self._io_type = value

    @property
    def io_channel(self) -> int:
        """
        Which I/O pin within the port was recorded.
        """

        return self._io_channel

    @io_channel.setter
    def io_channel(self, value: int) -> None:
        self._io_channel = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.OscilloscopeCaptureProperties
    ) -> 'OscilloscopeCaptureProperties':
        instance = OscilloscopeCaptureProperties.__new__(
            OscilloscopeCaptureProperties
        )  # type: OscilloscopeCaptureProperties
        instance.data_source = OscilloscopeDataSource(pb_data.data_source)
        instance.setting = pb_data.setting
        instance.axis_number = pb_data.axis_number
        instance.io_type = IoPortType(pb_data.io_type)
        instance.io_channel = pb_data.io_channel
        return instance
