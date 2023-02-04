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
        self.data['RTD'] = pd.DataFrame(columns=['position', 'current'])
        self.plots = {}

        ### initiallize variables ###
        self.spinBox_SpecPos = self.findChild(QtWidgets.QSpinBox, "spinBox_SpecPos")
        self.spinBox_SpecPos.setKeyboardTracking(False)
        self.spinBox_SpecPos.setValue(self.read_pos("spec"))

        self.pushButton_ResetSpec = self.findChild(QtWidgets.QPushButton, "pushButton_ResetSpec")

        self.spinBox_FilterPos = self.findChild(QtWidgets.QSpinBox, "spinBox_FilterPos")
        self.spinBox_FilterPos.setKeyboardTracking(False)
        self.spinBox_FilterPos.setValue(self.read_pos("filter"))

        self.pushButton_ResetFilter = self.findChild(QtWidgets.QPushButton, "pushButton_ResetFilter")

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

        self.tabWidget_plots = self.findChild(QtWidgets.QTabWidget, "tabWidget_plots")
        self.tabWidget_plots.setMovable(True)
        self.tabWidget_plots.setCurrentIndex(0)

        self.plot_RTD = self.findChild(QtWidgets.QWidget, "plot_RTD")

        self.lcd_RTD = self.findChild(QtWidgets.QLCDNumber, "lcdNumber_RTD")

        self.comboBox_RTDaxis = self.findChild(QtWidgets.QComboBox, "comboBox_RTDaxis")
        self.comboBox_RTDaxis.addItems(['Time', 'Position'])

        self.pushButton_ClearRTD = self.findChild(QtWidgets.QPushButton, "pushButton_ClearRTD")
        
        self.tab_Measures = self.findChild(QtWidgets.QWidget, "tab_Measures")

        self.spinBox_MeasStart = self.findChild(QtWidgets.QSpinBox, "spinBox_MeasStart")
        self.spinBox_MeasStart.setKeyboardTracking(False)

        self.spinBox_MeasEnd = self.findChild(QtWidgets.QSpinBox, "spinBox_MeasEnd")
        self.spinBox_MeasEnd.setKeyboardTracking(False)

        self.spinBox_MeasStep = self.findChild(QtWidgets.QSpinBox, "spinBox_MeasStep")
        self.spinBox_MeasStep.setKeyboardTracking(False)

        self.lineEdit_MeasName = self.findChild(QtWidgets.QLineEdit, "lineEdit_MeasName")

        ### TAB RTD ###

        # adding graphWidget to the tab
        self.graphWidget_RTDt = pg.PlotWidget()
        self.graphWidget_RTDc = pg.PlotWidget()
        graphLayout_RTD = QtWidgets.QStackedLayout()
        graphLayout_RTD.addWidget(self.graphWidget_RTDt)
        graphLayout_RTD.addWidget(self.graphWidget_RTDc)
        self.plot_RTD.setLayout(graphLayout_RTD)
        
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

        # define the plot objects
        pen = pg.mkPen(color='r', width=5) #, style=QtCore.Qt.PenStyle.DashLine)
        self.plots['RTDt'] = self.graphWidget_RTDt.plot(self.data['RTD'].index, self.data['RTD'].current, pen=pen, name='RTD', symbol='o', symbolSize=10, symbolBrush=('b'))
        self.plots['RTDc'] = self.graphWidget_RTDc.plot(self.data['RTD'].position, self.data['RTD'].current, pen=pen, name='RTD', symbol='o', symbolSize=10, symbolBrush=('b'))


        ### TAB MEASURE ###
        
        # adding graphWidget to the tab
        self.graphWidget_Measures = pg.PlotWidget()
        #self.tab_Measures.layout().addWidget(self.graphWidget_Measures)
        graphLayout_Measures = QtWidgets.QVBoxLayout()
        graphLayout_Measures.addWidget(self.graphWidget_Measures)
        self.tab_Measures.setLayout(graphLayout_Measures)
        


        # Styling the graph
        self.graphWidget_Measures.setBackground('w')
        self.graphWidget_Measures.setLabel('left', 'Current [A]')
        self.graphWidget_Measures.setLabel('bottom', 'Position [steps]')
        self.graphWidget_Measures.showGrid(x=True, y=True)
        self.graphWidget_Measures.addLegend()




        ### connect the signals ###
        self.spinBox_FilterPos.valueChanged.connect(lambda: self.GUI_goto("filter",))
        self.spinBox_SpecPos.valueChanged.connect(lambda: self.GUI_goto("spec",))

        self.spinBox_ITime.valueChanged.connect(self.GUI_set_itime)
        self.comboBox_range.currentIndexChanged.connect(self.GUI_set_range)

        self.pushButton_RTD.clicked.connect(self.GUI_RTD)

        self.pushButton_ClearRTD.clicked.connect(self.GUI_clearRTD)

        self.comboBox_RTDaxis.currentIndexChanged.connect(graphLayout_RTD.setCurrentIndex)

        self.pushButton_measure.clicked.connect(self.GUI_Measure)

        self.pushButton_ResetSpec.clicked.connect(lambda: self.GUI_reset_pos("spec"))
        self.pushButton_ResetFilter.clicked.connect(lambda: self.GUI_reset_pos("filter"))
        

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

    def GUI_reset_pos(self, motor):
        self.statusbar.showMessage('resetting position of ' + motor)
        self.frame_controls.setEnabled(False)
        self.pushButton_measure.setEnabled(False)
        self.pushButton_RTD.setEnabled(False)

        if motor == "filter":
            time.sleep(0.1)
            self.spinBox_FilterPos.setValue(0)
        elif motor == "spec":
            time.sleep(0.1)
            self.spinBox_SpecPos.setValue(0)

        self.statusbar.showMessage('Ready')
        self.frame_controls.setEnabled(True)
        self.pushButton_measure.setEnabled(True)    
        self.pushButton_RTD.setEnabled(True)    

    def RealTimeDisplay(self, newData_callback):
        while self.pushButton_RTD.isChecked():
            time.sleep(0.1) #jump
            time.sleep(1) #read
            print('reading detector')
            self.data['RTD'].loc[time.time()-self.T0] = [1, np.random.randint(0, 100)]
            newData_callback.emit('RTD')

    def GUI_RTD(self):
        if self.pushButton_RTD.isChecked():
            self.tabWidget_plots.setCurrentIndex(0)
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
            self.plots['RTDc'].setData(list(self.data['RTD'].position), list(self.data['RTD'].current))
            self.lcd_RTD.display(list(self.data['RTD'].current)[-1])
        else:
            try:
                self.plots[newData].setData(list(self.data[newData].position), list(self.data[newData].current))
            except:
                self.plots[newData] = self.graphWidget_Measures.plot(list(self.data[newData].position), list(self.data[newData].current), pen=pg.mkPen(color='r', width=5), name=newData, symbol='o', symbolSize=10, symbolBrush=('b'))

    def GUI_clearRTD(self):
        self.data['RTD'] = pd.DataFrame(columns=['position', 'current'])
        self.plots['RTDt'].setData(list(self.data['RTD'].index), list(self.data['RTD'].current))
        self.plots['RTDc'].setData(list(self.data['RTD'].position), list(self.data['RTD'].current))
        self.lcd_RTD.display(0)
    

    def Measure(self, MeasName, newData_callback):

        vec_pos = np.arange(self.spinBox_MeasStart.value(), self.spinBox_MeasEnd.value(), self.spinBox_MeasStep.value())

        for pos in vec_pos:
            ### simulate the true measure function
            time.sleep(1)
            print('measuring')
            ###
            self.data[MeasName].loc[time.time()-self.T0] = [int(pos), np.random.randint(0, 100)]
            newData_callback.emit(MeasName)

        

    def GUI_Measure(self):
        self.tabWidget_plots.setCurrentIndex(1)
        MeasName = self.lineEdit_MeasName.text()
        if MeasName not in self.data.keys():
            self.data[MeasName] = pd.DataFrame(columns=['position', 'current'])

        worker = Worker(self.Measure, MeasName=MeasName)

        worker.signals.started.connect(lambda: self.statusbar.showMessage("Measuring..."))
        worker.signals.started.connect(lambda: self.frame_controls.setEnabled(False))
        worker.signals.started.connect(lambda: self.pushButton_RTD.setEnabled(False))
        worker.signals.started.connect(lambda: self.pushButton_measure.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.frame_controls.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_RTD.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_measure.setEnabled(True))

        worker.signals.newData.connect(self.GUI_plotNewData)

        self.threadpool.start(worker)


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
        worker.signals.started.connect(lambda: self.pushButton_RTD.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.groupBox_motors.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_measure.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_RTD.setEnabled(True))

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
        worker.signals.started.connect(lambda: self.pushButton_RTD.setEnabled(False))
        worker.signals.finished.connect(lambda: self.statusbar.showMessage("Ready"))
        worker.signals.finished.connect(lambda: self.groupBox_detector.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_measure.setEnabled(True))
        worker.signals.finished.connect(lambda: self.pushButton_RTD.setEnabled(True))
        
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
            result = self.fn(*self.args, **self.kwargs) # run the function with new_data keyword
        except:
            self.kwargs['newData_callback'] = self.signals.newData
            result = self.fn(*self.args, **self.kwargs)

        self.signals.result.emit(result)  # Return the result of the processing

        self.signals.finished.emit()  # Done

        
### RUN ###

app = QApplication(sys.argv)
app.setStyle('Fusion')
window = MainWindow()
window.show()
app.exec()
