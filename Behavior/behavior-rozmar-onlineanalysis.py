import behavior_rozmar as behavior_rozmar
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QComboBox, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import re
class App(QDialog):

    def __init__(self):
        super().__init__()
        self.dirs = dict()
        self.handles = dict()
        self.title = 'behavior - online analysis'
        self.left = 10
        self.top = 10
        self.width = 1024
        self.height = 768
        
        
        self.dirs['projectdir'] = '/home/rozmar/Data/Behavior/Projects'
        self.loadthedata()
        self.initUI()
        
    def loadthedata(self):
        self.data = behavior_rozmar.loadcsvdata(projectdir = self.dirs['projectdir'])
        #self.filterthedata()
        
    def filterthedata(self,lastselected = ' '):
        filterorder = ['project','experiment','setup','session','subject','experimenter']
        self.data_now = self.data 
        for filternow in filterorder:
            filterstring = str(self.handles['filter_'+filternow].currentText())
            if not re.findall('all',filterstring):
                self.data_now = self.data_now[self.data_now[filternow] == filterstring]
# =============================================================================
#         data = self.data 
#         handlenames = self.handles.keys()
#         filternames = list()
#         for handlename in handlenames:
#             if re.findall('filter',handlename): filternames.append(handlename)
#         if lastselected != ' ':
#             filternames.remove(lastselected)
#             filternames.insert(0,lastselected)
# =============================================================================

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.createGridLayout()
        
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox_filter)
        windowLayout.addWidget(self.horizontalGroupBox_axes)
        self.setLayout(windowLayout)
        
        self.show()
    
    def createGridLayout(self):
        self.horizontalGroupBox_filter = QGroupBox("Filter")
        layout = QGridLayout()
        self.handles['filter_project'] = QComboBox(self)
        self.handles['filter_project'].addItem('all projects')
        self.handles['filter_project'].addItems(self.data['project'].unique())
        self.handles['filter_project'].currentIndexChanged.connect(lambda: self.filterthedata('filter_project'))
        self.handles['filter_experiment'] = QComboBox(self)
        self.handles['filter_experiment'].addItem('all experiments')
        self.handles['filter_experiment'].addItems(self.data['experiment'].unique())
        self.handles['filter_experiment'].currentIndexChanged.connect(lambda: self.filterthedata('filter_experiment'))
        self.handles['filter_setup'] = QComboBox(self)
        self.handles['filter_setup'].addItem('all setups')
        self.handles['filter_setup'].addItems(self.data['setup'].unique())
        self.handles['filter_setup'].currentIndexChanged.connect(lambda: self.filterthedata('filter_setup'))
        self.handles['filter_session'] = QComboBox(self)
        self.handles['filter_session'].addItem('all sessions')
        self.handles['filter_session'].addItems(self.data['session'].unique())
        self.handles['filter_session'].currentIndexChanged.connect(lambda: self.filterthedata('filter_session'))
        self.handles['filter_subject'] = QComboBox(self)
        self.handles['filter_subject'].addItem('all subjects')
        self.handles['filter_subject'].addItems(self.data['subject'].unique())
        self.handles['filter_subject'].currentIndexChanged.connect(lambda: self.filterthedata('filter_subject'))
        self.handles['filter_experimenter'] = QComboBox(self)
        self.handles['filter_experimenter'].addItem('all experimenters')
        self.handles['filter_experimenter'].addItems(self.data['experimenter'].unique())
        self.handles['filter_experimenter'].currentIndexChanged.connect(lambda: self.filterthedata('filter_experimenter'))
        
        layout.addWidget(self.handles['filter_project'] ,0,0)
        layout.addWidget(self.handles['filter_experiment'],0,1)
        layout.addWidget(self.handles['filter_setup'],0,2)
        layout.addWidget(self.handles['filter_session'],0,3)
        layout.addWidget(self.handles['filter_subject'],0,4)
        layout.addWidget(self.handles['filter_experimenter'],0,5)
        
        self.horizontalGroupBox_filter.setLayout(layout)
        
        self.horizontalGroupBox_axes = QGroupBox("plots")
        layout_axes = QGridLayout()
        self.handles['axes1'] = PlotCanvas(self, width=5, height=4)
        self.handles['axes2'] = PlotCanvas(self, width=5, height=4)
        layout_axes.addWidget(self.handles['axes1'],0,0)
        layout_axes.addWidget(self.handles['axes2'],1,0)
        self.horizontalGroupBox_axes.setLayout(layout_axes)
        
        
        
        
class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        #self.plot()


    def plot(self,data = []):
        
        self.axes.plot(data, 'r-')
        self.axes.set_title('PyQt Matplotlib Example')
        self.draw()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

