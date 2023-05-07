from PyQt5.QtCore import QPoint

class Park:
    ''''''
    # is park available: E1 E2 W1 W2 N1 N2 S1 S2
    park_space = [True for i in range(8)]
    # park position: E1 E2 W1 W2 N1 N2 S1 S2
    park_pos =[QPoint(410, 213), QPoint(410, 263), 
                    QPoint(145, 313), QPoint(145, 363),
                    QPoint(263, 146), QPoint(213, 146),
                    QPoint(363, 413), QPoint(313, 413)]  
    
    def __init__(self):
        pass
              
    def get_park_mutex(self, direction):
        '''return: park_mutex, park_position(QPoint)'''
        index = 0
        if direction == 'EAST':
            index = 0
        elif direction =='WEST':
            index = 2
        elif direction =='NORTH':
            index = 4
        elif direction =='SOUTH':
            index = 6
        
        if self.park_space[index] == True:
            self.park_space[index] = False
            return index + 1, self.park_pos[index]
        elif self.park_space[index + 1] == True:
            self.park_space[index + 1] = False
            return index + 2, self.park_pos[index + 1]
        else:
            return 0, QPoint(0, 0)
        
    def release_mutex(self, car):
        '''release park mutex when the car drives out'''
        if car.park_no > 0 and car.park_no <= 8:
            self.park_space[car.park_no - 1] = True
            print("Park No.{} released".format(car.park_no))
            car.park_no = 0
                            