import sys
from PyQt5.QtWidgets import *
from light import *
from car import *
from mutex import *

stylesheet = """
            MainWindow {
                background-image: url("images/bk.jpg");
                background-repeat: no-repeat;
                background-position: center;
            }
        """

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
               
    def initUI(self):
        self.centralWidget = QWidget()
        self.resize(600, 600)   
        self.setStyleSheet(stylesheet)
        
        # traffic light ui control
        self.init_light()
        self.light_thread = Light()
        self.light_thread.light_signal.connect(self.switch_light)
        self.light_thread.start()
        # LCD shows how many seconds before light switch
        self.lcd = QLCDNumber(1, self)
        self.lcd.setGeometry(75, 80, 35, 70)
        self.lcd.setStyleSheet("""QLCDNumber { background-color: rgb(81, 80, 75); color: green; border: none; }""")
        self.light_thread.second_signal.connect(self.lcd.display)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.show()
        
        # buttons to set cars
        self.set_btns()
        
        # cars
        self.car_labels = {}   # save car_name: car_label 
        self.car_threads = []  # save car threads

        self.setWindowIcon(QIcon('images/icon.ico'))
        self.setWindowTitle("Crossing Simulator --Copyright@2151765")
        self.show()

    def init_light(self):
        self.green_pixmap = QPixmap("images/greenlight.png")
        self.green_label = QLabel(self)
        self.green_label.setGeometry(120, 80, 40, 85)
        self.green_label.setPixmap(self.green_pixmap)
        self.green_label.resize(40, 83) # orignial image size = 65*136
        self.green_label.setScaledContents(True)
        self.green_label.setObjectName("greenlight")
        self.green_label.show()
        
        self.red_pixmap = QPixmap("images/redlight.png")
        self.red_label = QLabel(self)
        self.red_label.setGeometry(120, 80, 40, 85)
        self.red_label.setPixmap(self.red_pixmap)
        self.red_label.resize(40, 83) # orignial 65*136
        self.red_label.setScaledContents(True)
        self.red_label.setObjectName("redlight")
        
        text = QLabel(self)
        text.setGeometry(120, 63, 40, 12)
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        text.setFont(font)
        text.setText(" N&S")
        self.green_label.setToolTip("This is the Traffic Light for direction <b>N</b>orth and <b>S</b>outh")
        self.red_label.setToolTip("This is the Traffic Light for direction <b>N</b>orth and <b>S</b>outh")
               

    def switch_light(self, signal):
        if signal == True:
            self.green_label.show()
            self.red_label.hide()
            self.lcd.setStyleSheet("""QLCDNumber { background-color: rgb(81, 80, 75); color: green; border: none; }""")
            self.lcd.show()
        else:
            self.red_label.show()
            self.green_label.hide()
            self.lcd.setStyleSheet("""QLCDNumber { background-color: rgb(81, 80, 75); color: red; border: none; }""")
            self.lcd.show()     

    def set_btns(self):
        
        self.btn = [QPushButton("NormalE", self), QPushButton("EmergencyE", self),
                    QPushButton("NormalW", self), QPushButton("EmergencyW", self),
                    QPushButton("NormalN", self), QPushButton("EmergencyN", self),
                    QPushButton("NormalS", self), QPushButton("EmergencyS", self),]
        
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(9)
        
        for i in range(8):
            self.btn[i].setToolTip("Click to add one {} car".format("Normal" if i%2==0 else "Emergency"))
            self.btn[i].resize(110, 28)
            self.btn[i].clicked.connect(self.btn_clicked)
            self.btn[i].setFont(font)
        
        self.btn[0].move(480, 160)
        self.btn[1].move(480, 140)
        self.btn[2].move(10, 440)
        self.btn[3].move(10, 420)
        self.btn[4].move(80, 30)
        self.btn[5].move(80, 10)
        self.btn[6].move(410, 560)
        self.btn[7].move(410, 540)

    def btn_clicked(self):
        sender = self.sender().text()
        park_space_remain = -1
        if sender == "NormalE" or sender == "EmergencyE":
            direction = 'EAST'
            park_space_remain, location = Park.get_park_mutex(Park, direction)
        elif sender == "NormalW" or sender == "EmergencyW":
            direction = 'WEST'
            park_space_remain, location = Park.get_park_mutex(Park, direction)
        elif sender == "NormalS" or sender == "EmergencyS":
            direction = 'SOUTH'
            park_space_remain, location = Park.get_park_mutex(Park, direction)
        elif sender == "NormalN" or sender == "EmergencyN":
            direction = 'NORTH'
            park_space_remain, location = Park.get_park_mutex(Park, direction)     
        
        if park_space_remain > 0:
            ct = Car(location, direction, park_space_remain, (1 if sender[0] == 'E' else 0))
            ct.start() 
            ct.cc.start_signal.connect(self.init_car)
            ct.cc.move_signal.connect(self.move_car)
            ct.cc.end_signal.connect(self.end_car)
            self.car_threads.append(ct)
                   
        else:
            box = QMessageBox.question(self, 'Cannot Add New Car!', "Parking Already Full! (Max = 2)", QMessageBox.Yes | 
            QMessageBox.Ok, QMessageBox.Ok) 

    def init_car(self, signal):
        print("Signal Received: init car", signal) 
        self.car_labels[signal[2]] = QLabel(self)
        pixmap = QPixmap(signal[0])
        self.car_labels[signal[2]].setPixmap(pixmap)
        self.car_labels[signal[2]].setGeometry(signal[1])
        self.car_labels[signal[2]].show()
        self.car_labels[signal[2]].setScaledContents(True)
        self.car_labels[signal[2]].setObjectName(signal[2])
    
    def move_car(self, signal):
        # print("Signal Received: move car ", signal)
        self.car_labels[signal[0]].move(signal[1], signal[2])
        self.car_labels[signal[0]].show()

    def end_car(self, signal):
        print("Signal Received: end car", signal)
        self.car_labels[signal].hide()
        del self.car_labels[signal]

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = MainWindow() 
    sys.exit(app.exec_())