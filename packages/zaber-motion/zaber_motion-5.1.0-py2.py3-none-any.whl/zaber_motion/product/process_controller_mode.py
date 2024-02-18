# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class ProcessControllerMode(Enum):
    """
    Servo Tuning Parameter Set to target.
    """

    MANUAL = 0
    PID = 1
    PID_HEATER = 2
    ON_OFF = 3
