from PyQt5.QtCore import QThread, pyqtSignal
from mutex import *

class Light(QThread):
    light_signal = pyqtSignal(bool)
    second_signal = pyqtSignal(int)
    green = True  # is green on NS direction
    
    def __init__(self):
        super(Light, self).__init__()
    
    def switch():
        Light.green = not Light.green
         
    def run(self):
        self.green = True
        self.light_signal.emit(self.green)
        self.second_signal.emit(8)
        while(True):
            print("Light on NS direction is:", ("green" if self.green == True else "red"))
            for i in range(8):
                self.sleep(1)
                self.second_signal.emit(7 - i if i < 7 else 8) # LCD delay
            self.green = not self.green
            Light.switch()
            self.light_signal.emit(self.green)
        
    def get_NS_state(self):
        return self.green
    
    def get_EW_state(self):
        return not self.green
