from dataclasses import dataclass  

@dataclass
class Limits:
    '''Holds lower and upper position limits'''
    lower: float | int = -9999
    upper: float | int = 9999