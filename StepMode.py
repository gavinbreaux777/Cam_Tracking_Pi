from enum import Enum

class StepMode(float, Enum):
    Full = 1
    Half = 1/2
    Quarter = 1/4
    Eighth = 1/8
    Sixteenth = 1/16