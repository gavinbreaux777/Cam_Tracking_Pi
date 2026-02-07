from typing import Tuple, Callable
class DetectionObserver:
    '''
        Observer of detection class, contains notifications to detection events
    '''
    def OnMotionFound(self, location: Tuple[int,int], acknowledgeNotification: Callable[[bool], None]):
        '''
        Called when motion is detected

        args:
            location: (Tuple[int,int]: X Y coordinates of found motion)
            
            acknowledgeNotification: (Callable[bool]: Callback to call to acknowledge the motion notification. Call once done and processing can start again)
        '''
        print("OnMotionFound method not implemented. Motion found at " + str(location))
