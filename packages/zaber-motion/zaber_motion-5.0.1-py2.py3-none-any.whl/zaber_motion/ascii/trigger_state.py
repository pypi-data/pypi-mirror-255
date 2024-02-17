# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List  # pylint: disable=unused-import
from ..protobufs import main_pb2


class TriggerState:
    """
    The complete state of a trigger.
    """

    @property
    def condition(self) -> str:
        """
        The firing condition for a trigger.
        """

        return self._condition

    @condition.setter
    def condition(self, value: str) -> None:
        self._condition = value

    @property
    def actions(self) -> List[str]:
        """
        The actions for a trigger.
        """

        return self._actions

    @actions.setter
    def actions(self, value: List[str]) -> None:
        self._actions = value

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
    def fires_total(self) -> int:
        """
        The number of total fires for this trigger.
        A value of -1 indicates unlimited fires.
        """

        return self._fires_total

    @fires_total.setter
    def fires_total(self, value: int) -> None:
        self._fires_total = value

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
        pb_data: main_pb2.TriggerState
    ) -> 'TriggerState':
        instance = TriggerState.__new__(
            TriggerState
        )  # type: TriggerState
        instance.condition = pb_data.condition
        instance.actions = list(pb_data.actions)
        instance.enabled = pb_data.enabled
        instance.fires_total = pb_data.fires_total
        instance.fires_remaining = pb_data.fires_remaining
        return instance
