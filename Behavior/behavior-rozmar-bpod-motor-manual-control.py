import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

import zaber.serial as zaber_serial
import time
variables = {'comport_motor' : 'COM7',
             }
class App(QDialog):

    def __init__(self):
        super().__init__()
        self.handles = dict()
        self.title = 'pybpod and zaber control'
        self.left = 10
        self.top = 10
        self.width = 0
        self.height = 0
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.Motorcontrol)
        windowLayout.addWidget(self.bpodcontrol)
        self.setLayout(windowLayout)
        
        self.show()
    
    def createGridLayout(self):
        self.Motorcontrol = QGroupBox("Motor Control")
        layout_motor = QGridLayout()
# =============================================================================
#         layout.setColumnStretch(1, 4)
#         layout.setColumnStretch(2, 4)
# =============================================================================
        self.handles['motor_refresh'] = QPushButton('Refresh')
        self.handles['motor_refresh'].clicked.connect(self.zaber_refresh) 
        layout_motor.addWidget(self.handles['motor_refresh'],0,0)
        
        layout_motor.addWidget(QLabel('Rostro-caudal:'),0,1)

        self.handles['motor_RC_edit'] = QLineEdit('')
        layout_motor.addWidget(self.handles['motor_RC_edit'],0,2)
        self.handles['motor_RC_edit'].returnPressed.connect(self.zaber_move_RC)
        layout_motor.addWidget(QLabel('Lateral:'),0,3)
		
        self.handles['motor_LAT_edit'] = QLineEdit('')
        self.handles['motor_LAT_edit'].returnPressed.connect(self.zaber_move_Lat)
        layout_motor.addWidget(self.handles['motor_LAT_edit'],0,4)
        
        self.handles['motor_step_edit'] = QLineEdit('5000')
        layout_motor.addWidget(self.handles['motor_step_edit'],1,6)
        self.handles['motor_forward'] = QPushButton('Forward')
        layout_motor.addWidget(self.handles['motor_forward'],0,6)
        self.handles['motor_forward'].clicked.connect(self.zaber_move_forward)
        self.handles['motor_back'] = QPushButton('Back')
        layout_motor.addWidget(self.handles['motor_back'],2,6)
        self.handles['motor_back'].clicked.connect(self.zaber_move_back)
        self.handles['motor_left'] = QPushButton('Left')
        layout_motor.addWidget(self.handles['motor_left'],1,5)
        self.handles['motor_left'].clicked.connect(self.zaber_move_left)
        self.handles['motor_left'] = QPushButton('Right')
        layout_motor.addWidget(self.handles['motor_left'] ,1,7)
        self.handles['motor_left'].clicked.connect(self.zaber_move_right)
        
        self.Motorcontrol.setLayout(layout_motor)
        
        
        
        self.bpodcontrol = QGroupBox("bpod Control")
        layout_bpod = QGridLayout()
        self.handles['bpod_Connect'] = QPushButton('Connect to bpod')
        self.handles['bpod_Connect'].setCheckable(True)
        self.handles['bpod_Connect'].clicked.connect(self.bpod_connect)
        layout_bpod.addWidget(self.handles['bpod_Connect'],0,0)
        for i in range(1, 9):
            self.handles['bpod_Valve_'+ str(i)] = QPushButton('Valve-'+str(i))
            layout_bpod.addWidget(self.handles['bpod_Valve_'+ str(i)],1,i-1)
            self.handles['bpod_Valve_'+ str(i)].clicked.connect(lambda: self.bpod_sendcommand('Valve'+str(i)))
            
            self.handles['bpod_PWM_'+ str(i)] = QPushButton('PWM-'+str(i))
            layout_bpod.addWidget(self.handles['bpod_PWM_'+ str(i)],2,i-1)
            self.handles['bpod_PWM_'+ str(i)].clicked.connect(lambda: self.bpod_sendcommand('PWM'+str(i)))            
        self.bpodcontrol.setLayout(layout_bpod)
        
    def bpod_connect(self):
      if self.handles['bpod_Connect'].isChecked():
         self.handles['bpod_Connect'].setText('Disconnect from bpod')
      else:
         self.handles['bpod_Connect'].setText('Connect to bpod')
    def bpod_sendcommand(self,command):
        print(command)

    def zaber_refresh(self):
        with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
            Forward_Backward_device = zaber_serial.BinaryDevice(ser,1)
            Left_Right_device = zaber_serial.BinaryDevice(ser,2)
            pos_Forward_Backward = Forward_Backward_device.get_position()
            pos_Left_Right = Left_Right_device.get_position()
        self.handles['motor_RC_edit'].setText(str(pos_Forward_Backward))
        self.handles['motor_LAT_edit'].setText(str(pos_Left_Right))
        
    def zaber_move_Lat(self):
        if 	self.handles['motor_LAT_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moveabs_cmd = zaber_serial.BinaryCommand(2,20,int(self.handles['motor_LAT_edit'].text()))
                ser.write(moveabs_cmd)
                time.sleep(1)
        self.zaber_refresh()
		
    def zaber_move_RC(self):
        if 	self.handles['motor_RC_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moveabs_cmd = zaber_serial.BinaryCommand(1,20,int(self.handles['motor_RC_edit'].text()))
                ser.write(moveabs_cmd)
                time.sleep(1)
        self.zaber_refresh()
        
    def zaber_move_forward(self):
        if 	self.handles['motor_step_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moverel_cmd = zaber_serial.BinaryCommand(1,21,-1*int(self.handles['motor_step_edit'].text()))
                ser.write(moverel_cmd)
                time.sleep(1)
        self.zaber_refresh()
        print('forward')
    def zaber_move_back(self):
        if 	self.handles['motor_step_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moverel_cmd = zaber_serial.BinaryCommand(1,21,int(self.handles['motor_step_edit'].text()))
                ser.write(moverel_cmd)
                time.sleep(1)
        self.zaber_refresh()
        print('back')
    def zaber_move_left(self):
        if 	self.handles['motor_step_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moverel_cmd = zaber_serial.BinaryCommand(2,21,-1*int(self.handles['motor_step_edit'].text()))
                ser.write(moverel_cmd)
                time.sleep(1)
        self.zaber_refresh()
        print('left')
    def zaber_move_right(self):
        if 	self.handles['motor_step_edit'].text().isnumeric:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moverel_cmd = zaber_serial.BinaryCommand(2,21,1*int(self.handles['motor_step_edit'].text()))
                ser.write(moverel_cmd)
                time.sleep(1)
        self.zaber_refresh()
        print('right')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
