from RawServoControl import RawServoControl
from IOControl import IOControl
import time

class ServoControl:
    def __init__(self, ioControl:IOControl):
        self.servo = RawServoControl(ioControl, 12, 50)
        self.activeInlet = 1
        self.ammoInlets = AmmoInletTrio(
            AmmoInletSingle(3, 3, 150, 165),
            AmmoInletSingle(3, 3, 115, 125),
            AmmoInletSingle(3, 3, 65, 75)
        )
        
        self.CloseGate()

    @property
    def servoPosition(self) -> float:
        return self.servo.position
    
    def OpenGate(self):
        '''Open gate to release all balls'''
        self.servo.SetAngle(self.ammoInlets.activeOpenServoAngle)

    def CloseGate(self):
        '''Close gate to stop releasing balls'''
        self.servo.SetAngle(self.ammoInlets.activeClosedServoAngle)

    def SetServoAngle(self, angle: float):
        self.servo.SetAngle(angle)

    def ReleaseSingle(self):
        '''Release single ball. Motors should be spooled already'''
        self.OpenGate()
        time.sleep(0.1) #Add sensor to allow only 1 ball?
        self.CloseGate()
        
        self.ammoInlets.ReduceActiveAmmoCount()
        self.CloseGate()

    
class AmmoInletSingle():
    def __init__(self, Capacity: int, CurrentCount: int, OpenServoAngle: int, ClosedServoAngle: int):
        self.capacity = Capacity
        self.currentCount = CurrentCount
        self.openServoAngle = OpenServoAngle
        self.closedServoAngle = ClosedServoAngle
    
class AmmoInletTrio():
    def __init__(self, ammoInlet1: AmmoInletSingle, ammoInlet2: AmmoInletSingle, ammoInlet3: AmmoInletSingle):
        self.inlets: list[AmmoInletSingle, AmmoInletSingle, AmmoInletSingle] = [ammoInlet1, ammoInlet2, ammoInlet3]
        self.activeInlet = 0
        self.activeAmmoCount = self.inlets[0].currentCount
        self.activeOpenServoAngle = self.inlets[0].openServoAngle
        self.activeClosedServoAngle = self.inlets[0].closedServoAngle\

    def ReduceActiveAmmoCount(self):
        '''Reduce active ammo count by 1. If active ammo count is 0, set next inlet active'''
        self.activeAmmoCount -= 1
        print("Active ammo count: ", self.activeAmmoCount)
        if(self.activeAmmoCount <= 0):
            self.SetNextInletActive()
    
    def SetNextInletActive(self):
        '''Set next inlet active. If all inlets are empty, set active inlet to 0'''
        nextInlet = self.activeInlet + 1
        while(nextInlet < 3):
            if(self.inlets[nextInlet].currentCount > 0):
                self.SetActiveInlet(nextInlet)
                return
            else:
                self.activeInlet += 1
        self.SetActiveInlet(0)

    def SetActiveInlet(self, inlet: int):
        if(inlet > 2 or inlet < 0):
            raise ValueError("Invalid inlet number. Must be 0, 1, or 2.")
        else:
            print(f"Setting inlet {inlet} active")
            self.activeInlet = inlet
            self.activeAmmoCount = self.inlets[inlet].currentCount
            self.activeOpenServoAngle = self.inlets[inlet].openServoAngle
            self.activeClosedServoAngle = self.inlets[inlet].closedServoAngle
