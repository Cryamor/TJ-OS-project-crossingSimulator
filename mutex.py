from PyQt5.QtCore import QPoint

class Mutex:  
    '''Crossing Mutex 4*4'''
    mutex = [True for i in range(16)]
    def __init__(self):
        pass

    def get_mutex(self, point):
        '''set mutex=mutex-1, and return mutex number, similar to P()'''
        try:
            no = self.get_mutex_no(self, point)
            if self.mutex[no] == True:
                self.mutex[no] = False
                print("Mutex No.{} set".format(no))
                return no            
        except Exception as e:
            print("While get {} mutex: {}".format(point, e))
        return -1
       
    def reset_mutex(self, no):
        '''reset mutex=1, similar to V()'''
        self.mutex[no] = True 
        print("Mutex No.{} reset".format(no))
        
    def get_mutex_no(self, point):
        # <----200px----><50px><50px><50px><50px><----200px---->
        no = ((point.y() - 200) // 50) * 4 + (point.x() - 200) // 50
        return no
