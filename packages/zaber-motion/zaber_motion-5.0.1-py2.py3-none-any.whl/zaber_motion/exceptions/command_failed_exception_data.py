# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class CommandFailedExceptionData:
    """
    Contains additional data for CommandFailedException.
    """

    @property
    def command(self) -> str:
        """
        The command that got rejected.
        """

        return self._command

    @command.setter
    def command(self, value: str) -> None:
        self._command = value

    @property
    def response_data(self) -> str:
        """
        The data from the reply containing the rejection reason.
        """

        return self._response_data

    @response_data.setter
    def response_data(self, value: str) -> None:
        self._response_data = value

    @property
    def reply_flag(self) -> str:
        """
        The flag indicating that the command was rejected.
        """

        return self._reply_flag

    @reply_flag.setter
    def reply_flag(self, value: str) -> None:
        self._reply_flag = value

    @property
    def status(self) -> str:
        """
        The current device or axis status.
        """

        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def warning_flag(self) -> str:
        """
        The highest priority warning flag on the device or axis.
        """

        return self._warning_flag

    @warning_flag.setter
    def warning_flag(self, value: str) -> None:
        self._warning_flag = value

    @property
    def device_address(self) -> int:
        """
        The address of the device that rejected the command.
        """

        return self._device_address

    @device_address.setter
    def device_address(self, value: int) -> None:
        self._device_address = value

    @property
    def axis_number(self) -> int:
        """
        The number of the axis which the rejection relates to.
        """

        return self._axis_number

    @axis_number.setter
    def axis_number(self, value: int) -> None:
        self._axis_number = value

    @property
    def id(self) -> int:
        """
        The message ID of the reply.
        """

        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.CommandFailedExceptionData
    ) -> 'CommandFailedExceptionData':
        instance = CommandFailedExceptionData.__new__(
            CommandFailedExceptionData
        )  # type: CommandFailedExceptionData
        instance.command = pb_data.command
        instance.response_data = pb_data.response_data
        instance.reply_flag = pb_data.reply_flag
        instance.status = pb_data.status
        instance.warning_flag = pb_data.warning_flag
        instance.device_address = pb_data.device_address
        instance.axis_number = pb_data.axis_number
        instance.id = pb_data.id
        return instance
