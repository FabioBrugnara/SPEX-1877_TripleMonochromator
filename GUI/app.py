### IMPORTS ###

# GUI libraries
import traceback, sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtWidgets, QtCore, uic
from threading import Thread
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, pyqtSignal, pyqtSlot, QThreadPool
import pyqtgraph as pg

# Other libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

# Connect to the detector and spectrometer
print("Connecting to the detector and spectrometer...")
#time.sleep(5)
print("Connected!")

### MAIN ###

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        
        # load the ui file
        uic.loadUi("mainwindow.ui", self)

        # work with threads
        self.threadpool = QThreadPool()

        ### Variables ###
        self.T0 = time.time()
        
        self.data = {}
        self.data['RTD'] = pd.DataFrame(columns=['pos', 'current'])
        self.plots = {}

        ### initiallize variables ###
        self.spinBox_SpecPos = self.findChild(QtWidgets.QSpinBox, "spinBox_SpecPos")
        self.spinBox_SpecPos.setKeyboardTracking(False)
        self.spinBox_SpecPos.setValue(self.read_pos("spec"))

        self.spinBox_FilterPos = self.findChild(QtWidgets.QSpinBox, "spinBox_FilterPos")
        self.spinBox_FilterPos.setKeyboardTracking(False)
        self.spinBox_FilterPos.setValue(self.read_pos("filter"))

        self.spinBox_ITime = self.findChild(QtWidgets.QSpinBox, "spinBox_ITime")
        self.spinBox_ITime.setKeyboardTracking(False)
        self.spinBox_ITime.setValue(self.read_Itime())

        self.frame_controls = self.findChild(QtWidgets.QFrame, "frame_Controls")


        self.groupBox_motors = self.findChild(QtWidgets.QGroupBox, "groupBox_Motors")

        self.groupBox_detector = self.findChild(QtWidgets.QGroupBox, "groupBox_Detector")

        self.statusbar = self.findChild(QtWidgets.QStatusBar, "statusbar")
        self.statusbar.showMessage("Ready")

        self.pushButton_RTD = self.findChild(QtWidgets.QPushButton, "pushButton_RTD")

        self.comboBox_range = self.findChild(QtWidgets.QComboBox, "comboBox_Range")
        self.comboBox_range.addItems(['X1', 'X2', 'X5', 'X50'])

        self.pushButton_measure = self.findChild(QtWidgets.QPushButton, "pushButton_Measure")

        # plots
        self.plot_RTD = self.findChild(QtWidgets.QWidget, "plot_RTD")

        self.lcd_RTD = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_RTD")
        self.comboBox_RTDaxis = self.findChild(QtWidgets.QComboBox, "comboBox_RTDaxis")
        self.comboBox_RTDaxis.addItems(['Time', 'Position'])
        self.pushButton_ClearRTD = self.findChild(QtWidgets.QPushButton, "pushButton_ClearRTD")
        
        # adding graphWidget to the tab

        self.graphWidget_RTDt = pg.PlotWidget()
        self.graphWidget_RTDc = pg.PlotWidget()
        graphLayout = QtWidgets.QStackedLayout()
        graphLayout.addWidget(self.graphWidget_RTDt)
        graphLayout.addWidget(self.graphWidget_RTDc)
        self.plot_RTD.setLayout(graphLayout)
        
        # Styling the graph
        self.graphWidget_RTDt.setBackground('w')
        self.graphWidget_RTDt.setLabel('left', 'Current [A]')
        self.graphWidget_RTDt.setLabel('bottom', 'Time [s]')
        self.graphWidget_RTDt.showGrid(x=True, y=True)
        self.graphWidget_RTDt.addLegend()

        self.graphWidget_RTDc.setBackground('w')
        self.graphWidget_RTDc.setLabel('left', 'Current [A]')
        self.graphWidget_RTDc.setLabel('bottom', 'Position [steps]')
        self.graphWidget_RTDc.showGrid(x=True, y=True)
        self.graphWidget_RTDc.addLegend()


        # plot data: x, y values
        pen = pg.mkPen(color='r', width=5) #, style=QtCore.Qt.PenStyle.DashLine)
        self.plots['RTDt'] = self.graphWidget_RTDt.plot(self.data['RTD'].index, self.data['RTD'].current, pen=pen, name='RTD', symbol='o', symbolSize=10, symbolBrush=('b'))
        self.plots['RTDc'] = self.graphWidget_RTDc.plot(self.data['RTD'].pos, self.data['RTD'].current, pen=pen, name='RTD', symbol='o', symbolSize=10, symbolBrush=('b'))


        ### connect the signals ###
        self.spinBox_FilterPos.valueChanged.connect(lambda: self.GUI_goto("filter",))
        self.spinBox_SpecPos.valueChanged.connect(lambda: self.GUI_goto("spec",))

        self.spinBox_ITime.valueChanged.connect(self.GUI_set_itime)
        self.comboBox_range.currentIndexChanged.connect(self.GUI_set_range)

        self.pushButton_RTD.clicked.connect(self.GUI_RTD)

        self.pushButton_ClearRTD.clicked.connect(self.GUI_clearRTD)

        self.comboBox_RTDaxis.currentIndexChanged.connect(graphLayout.setCurrentIndex)
        

    def read_pos(self, motor):
        ### simulate the true read_pos function
        if motor == "filter":
            return 5
        elif motor == "spec":
            return 6
        ###
    
    def read_Itime(self):
        ### simulate the true read_Itime function
        return 100
        ###
    
    def RealTimeDisplay(self, newData_callback):
        while self.pushButton_RTD.isChecked():
            time.sleep(0.1) #jump
            time.sleep(1) #read
            print('reading detector')
            self.data['RTD'].loc[time.time()-self.T0] = [1, np.random.randint(0, 100)]
            newData_callback.emit('RTD')

    def GUI_RTD(self):
        if self.pushButton_RTD.isChecked():
            worker = Worker(self.RealTimeDisplay)

            worker.signals.started.connect(lambda: self.statusbar.showMessage("RTD..."))
            worker.signals.started.connect(lambda: self.frame_controls.setEnabled(False))
            worker.signals.started.connect(lambda: self.pushButton_measure.setEnabled(False))
            worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
            worker.signals.finished.connect(lambda: self.frame_controls.setEnabled(True))
            worker.signals.finished.connect(lambda: self.pushButton_measure.setEnabled(True))

            worker.signals.newData.connect(self.GUI_plotNewData)

            self.threadpool.start(worker)
        
    def GUI_plotNewData(self, newData):
        if newData == 'RTD':
            self.plots['RTDt'].setData(list(self.data['RTD'].index), list(self.data['RTD'].current))
            self.plots['RTDc'].setData(list(self.data['RTD'].pos), list(self.data['RTD'].current))
            self.lcd_RTD.display(list(self.data['RTD'].current)[-1])

    def GUI_clearRTD(self):
        self.data['RTD'] = pd.DataFrame(columns=['position', 'current'])
        self.plots['RTDt'].setData(list(self.data['RTD'].index), list(self.data['RTD'].current))
        self.plots['RTDc'].setData(list(self.data['RTD'].pos), list(self.data['RTD'].current))
        self.lcd_RTD.display(0)




    ###### GUI FUNCTIONS ########
    def GUI_goto(self, motor):
        ### simulate the true goto function, change this
        def goto(motor):
            if motor == "filter":
                print('going to ', self.spinBox_FilterPos.value())
                time.sleep(5)
                print('done')
            
            elif motor == "spec":
                print('going to ', self.spinBox_SpecPos.value())
                time.sleep(5)
                print('done')
        ###
        
        worker = Worker(lambda: goto(motor))

        worker.signals.started.connect(lambda: self.statusbar.showMessage("Moving..."))
        worker.signals.started.connect(lambda: self.groupBox_motors.setEnabled(False))
        worker.signals.started.connect(lambda: self.pushButton_measure.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.groupBox_motors.setEnabled(True))
        worker.signals.started.connect(lambda: self.pushButton_measure.setEnabled(True))

        # Execute
        self.threadpool.start(worker)

    def GUI_set_itime(self):
        ### simulate the true goto function
        def set_Itime(iTime):
            print('setting itime')
            time.sleep(1)
            print('done')
        ###     
        
        worker = Worker(lambda: set_Itime(self.spinBox_ITime.value()))

        worker.signals.started.connect(lambda: self.statusbar.showMessage("Setting integration time..."))
        worker.signals.started.connect(lambda: self.groupBox_detector.setEnabled(False))
        worker.signals.started.connect(lambda: self.pushButton_measure.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.groupBox_detector.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_measure.setEnabled(True))
        
        self.threadpool.start(worker)

    def GUI_set_range(self):
        ### simulate the true goto function
        def set_range(range):
            print('setting range', range)
            time.sleep(5)
            print('done')
        ###
        
        worker = Worker(lambda: set_range(self.comboBox_range.currentIndex()))

        worker.signals.started.connect(lambda: self.statusbar.showMessage("Setting range..."))
        worker.signals.started.connect(lambda: self.groupBox_detector.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.groupBox_detector.setEnabled(True))
        
        self.threadpool.start(worker)



##################################################################

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    newData = pyqtSignal(str)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        
        self.signals.started.emit() # start signal

        try:
            result = self.fn(*self.args, **self.kwargs, newData_callback=self.signals.newData) # run the function with new_data keyword
        except:
            result = self.fn(*self.args, **self.kwargs)

        self.signals.result.emit(result)  # Return the result of the processing

        self.signals.finished.emit()  # Done

        
### RUN ###

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MainWindow()
window.show()
app.exec()
