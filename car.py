from PyQt5.QtCore import QThread, QPoint, QObject, QRect
from PyQt5.QtGui import *
from light import *
from park import *
from mutex import *

gl_car_count = 0

class CarCommunication(QObject):
    start_signal = pyqtSignal(tuple)
    move_signal = pyqtSignal(tuple)
    end_signal = pyqtSignal(str)

class Car(QThread):
    '''car thread'''
    def __init__(self, pos, direction, park_no, flag):
        super(Car, self).__init__()
        
        self.pos = QPoint(pos.x(), pos.y())  # if written as "self.pos = pos", Park will change
        self.direction = direction # where the car comes from
        self.park_no = park_no     # park number 1~8
        self.size = QPoint(15, 27) if direction == 'NORTH' or direction =='SOUTH'\
            else QPoint(27,15)     # casr size
        self.flag = flag           # car type, 1 for emergency car, 0 for normal car
               
        # mutex number
        self.now_mutex = -1
        self.next_mutex = -1
        
        # set car name
        global gl_car_count
        self.car_name = "car{}".format(gl_car_count)
        gl_car_count += 1
        
        # signal    
        self.cc = CarCommunication()
        
        # select car images
        if self.flag == 1:
            if self.direction == 'EAST':
                self.carpic = "images/emergencyE.png"
            elif self.direction == 'WEST':
                self.carpic = "images/emergencyW.png"
            elif self.direction == 'NORTH':
                self.carpic = "images/emergencyN.png"  
            elif self.direction == 'SOUTH':
                self.carpic = "images/emergencyS.png"
            else:
                print("\nNo Direction Error")
        else:
            if self.direction == 'EAST':
                self.carpic = "images/normalE.png"
            elif self.direction == 'WEST':
                self.carpic = "images/normalW.png"
            elif self.direction == 'NORTH':
                self.carpic = "images/normalN.png"    
            elif self.direction == 'SOUTH':
                self.carpic = "images/normalS.png"
            else:
                print("\nNo Direction Error") 
        
               
    def get_next_mutex(self):
        '''get mutex of next space in 4*4 Mutex'''
        nmutex = -1    
        if self.direction == 'EAST':
            nmutex = Mutex.get_mutex(Mutex, QPoint(self.pos.x() - 21, self.pos.y()))
        elif self.direction == 'WEST':
            nmutex = Mutex.get_mutex(Mutex, QPoint(self.pos.x() + 56, self.pos.y()))
        elif self.direction == 'NORTH':
            nmutex = Mutex.get_mutex(Mutex, QPoint(self.pos.x(), self.pos.y() + 55))
        elif self.direction == 'SOUTH':
            nmutex = Mutex.get_mutex(Mutex, QPoint(self.pos.x(), self.pos.y() - 14))
           
        if nmutex >= 0:
            self.next_mutex = nmutex
            return True
        else:
            return False
        
    def set_last_mutex(self):
        Mutex.reset_mutex(Mutex, self.now_mutex)
    
    def is_finished(self):
        '''is car out of screen'''
        return True if self.pos.x() >= 600 or self.pos.x() <= 0 or self.pos.y() >= 600 or self.pos.y() <= 0\
            else False
            
    def move_one_mutex(self, step):
        '''前进一个信号量长度'''
        count = 0 
        while count < step:
            self.short_pause()
            if self.direction == 'EAST':
                self.pos.setX(self.pos.x() - 1)               
            elif self.direction == 'WEST':
                self.pos.setX(self.pos.x() + 1)
            elif self.direction == 'NORTH':
                self.pos.setY(self.pos.y() + 1) 
            elif self.direction == 'SOUTH':
                self.pos.setY(self.pos.y() - 1)  
                
            self.cc.move_signal.emit((self.car_name, self.pos.x(), self.pos.y()))
            
            count += 1
        self.now_mutex = self.next_mutex
        self.next_mutex = 0   
     
    def move(self):
        # before entering the crossing
        self.move_one_mutex(step = 4)  
        # mark move times, 4 times to cross
        move_count = 0
        
        # only normal car follows traffic light
        if self.flag == 0:
            if self.direction == 'EAST' or self.direction == 'WEST':
                while Light.get_EW_state(Light) == False:
                    self.short_pause()
            else:
                while Light.get_NS_state(Light) == False:
                    self.short_pause()
       
        # no mutex, stop  
        while self.get_next_mutex() == False:
            self.short_pause()
        
        self.move_one_mutex(50)
        move_count += 1
        Park.release_mutex(Park, self)
        
        while move_count < 4:
            self.short_pause()
                
            if self.get_next_mutex() == True:
                self.set_last_mutex()
                self.move_one_mutex(50)
                move_count += 1
        
        self.set_last_mutex()
        # leave crossing
        while self.is_finished() == False:
            self.move_one_mutex(50)
        self.cc.end_signal.emit(self.car_name)

    def run(self):
        self.cc.start_signal.emit((self.carpic,\
            QRect(self.pos.x(), self.pos.y(), self.size.x(), self.size.y()),\
                self.car_name))
        self.move()
        
    def short_pause(self):
        '''move forward or check condition every 20ms'''
        try:
            self.msleep(20)
        except Exception as e:
            print("not sleep")
