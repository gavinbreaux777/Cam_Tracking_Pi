from dataclasses import dataclass  

@dataclass
class Limits:
    '''Holds lower and upper position limits'''
    lower: float | int = -999
    upper: float | int = 999