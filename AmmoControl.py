from RawServoControl import RawServoControl
from IOControl import IOControl
import time
from ConfigClasses import ChamberServoConfig

class AmmoControl:
    def __init__(self, ioControl:IOControl, config: ChamberServoConfig):
        #self.triInletServo = RawServoControl(ioControl, -1, 50)
        self.chamberServo = RawServoControl(ioControl, config)
        self.activeInlet = 1
        self.ammoInlets = AmmoInletTrio(
            AmmoInletSingle(3, 3, 150, 165),
            AmmoInletSingle(3, 3, 115, 125),
            AmmoInletSingle(3, 3, 65, 75)
        )
        self.chamberServoOpenAngle = 115
        self.chamberServoClosedAngle = 100
        #self.CloseTriInletServo()

    @property
    def chamberServoPosition(self) -> float:
        return self.chamberServo.position
    @property
    def triInletServoPosition(self) -> float:
        return self.triInletServo.position
    
    # region chamberServo Control
    def OpenChamberServo(self):
        '''Allow ball into chamber'''
        self.chamberServo.SetAngle(self.chamberServoOpenAngle)
    
    def CloseChamberServo(self):
        '''Closes chamber servo, forcing a ball into firing wheels, if present'''
        self.chamberServo.SetAngle(self.chamberServoClosedAngle)
        
    def SetChamberServoAngle(self, angle: float):
        self.chamberServo.SetAngle(angle)

    def FireSingle(self):
        '''Force single ball through chamber into wheels. Motors should be spooled already'''
        self.CloseChamberServo()
        time.sleep(0.1) 
        self.OpenChamberServo()
    #endregion

    # region triInlet Control
    def OpenTriInletServo(self):
        '''Open gate to release all balls in active chute'''
        self.triInletServo.SetAngle(self.ammoInlets.activeOpenServoAngle)

    def CloseTriInletServo(self):
        '''Close gate to stop releasing balls in active chute'''
        self.triInletServo.SetAngle(self.ammoInlets.activeClosedServoAngle)

    def SetTriInletServoAngle(self, angle: float):
        self.triInletServo.SetAngle(angle)

    def ReleaseSingle(self):
        '''Release single ball through triInlet. Motors should be spooled already'''
        self.OpenTriInletServo()
        time.sleep(0.1) #Add sensor to allow only 1 ball?
        self.CloseTriInletServo()
        
        self.ammoInlets.ReduceActiveAmmoCount()
        self.CloseTriInletServo()
    # endregion
    
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
