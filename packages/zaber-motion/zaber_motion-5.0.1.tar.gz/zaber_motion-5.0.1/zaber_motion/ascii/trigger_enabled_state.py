# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2


class TriggerEnabledState:
    """
    The enabled state of a single trigger.
    Returns whether the given trigger is enabled and the number of times it will fire.
    This is a subset of the complete state, and is faster to query.
    """

    @property
    def enabled(self) -> bool:
        """
        The enabled state for a trigger.
        """

        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def fires_remaining(self) -> int:
        """
        The number of remaining fires for this trigger.
        A value of -1 indicates unlimited fires remaining.
        """

        return self._fires_remaining

    @fires_remaining.setter
    def fires_remaining(self, value: int) -> None:
        self._fires_remaining = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.TriggerEnabledState
    ) -> 'TriggerEnabledState':
        instance = TriggerEnabledState.__new__(
            TriggerEnabledState
        )  # type: TriggerEnabledState
        instance.enabled = pb_data.enabled
        instance.fires_remaining = pb_data.fires_remaining
        return instance
