import sys, time, os
sys.path.append(".")
sys.path.append("..")
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtTest
import pyqtgraph as pg
import striptool as striptool
import numpy as np
''' Load loggerWidget library (comment out if not available) '''
# sys.path.append(str(os.path.dirname(os.path.abspath(__file__)))+'\\..\\..\\loggerWidget\\')
# import loggerWidget as lw
# import logging
# logger = logging.getLogger(__name__)

seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]]

class timeButton(QPushButton):

    timeButtonPushed = pyqtSignal('int')

    def __init__(self, label):
        super(timeButton, self).__init__()
        self.setText(label)
        self.clicked.connect(self.buttonPushed)

    def buttonPushed(self):
        self.timeButtonPushed.emit(convert_to_seconds(str(self.text())))

class striptool_Demo(QMainWindow):
    def __init__(self, parent = None):
        super(striptool_Demo, self).__init__(parent)

        stdicon = self.style().standardIcon
        style = QStyle
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        self.setWindowTitle("striptool_Demo")
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        # self.toolbar = self.addToolBar('Exit')
        # self.toolbar.addAction(exitAction)

        ''' Initiate logger (requires loggerWidget - comment out if not available)'''
        # self.logwidget1 = lw.loggerWidget([logger,striptool.logger])

        ''' These are some options for pyqtgraph that make the graph black-on-white, and turn on antialiasing, which is nicer on the eye '''
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        ''' initialise an instance of the stripPlot Widget '''
        self.sp = striptool.stripPlot(plotRateBar=True,crosshairs=True)
        self.sp2 = striptool.stripPlot(plotRateBar=False)
        self.sp3 = striptool.stripPlot(plotRateBar=True,crosshairs=False)

        ''' This sets the signal length at which the system starts decimating the data to speed up plotting.
            For a 2*DecimateLength signal, the decimation factor would be 2.
            Record lengths > 10,000 should plot fine for most people, and is the default.
            Here I set it to 1000 as an example :
                 - a 3600 length record would decimate at order 1/3 and would have a plotting record length of 1200
                 - you probably don't need to use this unless you are having trouble with slow plotting.'''
        # self.sp.setDecimateLength(1000)
        self.sp2.setDecimateLength(100000)
        # self.sp3.setDecimateLength(1000)

        ''' Add some signals to the striptool - note they call our signal generator at a frequency of 1/timer (100 Hz and 10 Hz in these cases).
            The 'pen' argument sets the color of the curves, but can be changed in the GUI
                - see <http://www.pyqtgraph.org/documentation/style.html>'''
        self.sp.addSignal(name='signal1',pen='r', timer=1.0/100.0, function=self.createRandomSignal, arg=[0.5])
        self.sp2.addSignal(name='signal2',pen='r', timer=1.0/10.0, function=self.createRandomSignal, arg=[-5])
        self.sp2.addSignal(name='signal3',pen='g', timer=1.0/10.0, function=self.createRandomSignal, arg=[-3])
        self.sp2.addSignal(name='signal4',pen='b', timer=1.0/10.0, function=self.createRandomSignal, arg=[-1])
        self.sp2.addSignal(name='signal5',pen='c', timer=1.0/10.0, function=self.createRandomSignal, arg=[1])
        self.sp2.addSignal(name='signal6',pen='m', timer=1.0/10.0, function=self.createRandomSignal, arg=[3])
        self.sp2.addSignal(name='signal7',pen='y', timer=1.0/10.0, function=self.createRandomSignal, arg=[5])
        # self.sp3.addSignal(name='signal8',pen='b', timer=1.0/10.0, function=self.createRandomSignal, arg=[0.5])

        ''' this adds pre-data to the signal '''
        for name, offset in {'signal2':-5,'signal3':-3,'signal4':-1,'signal5':1,'signal6':3,'signal7':5}.items():
            testdata = []
            t = time.time()
            n = 100
            for i in range(n):
                testdata.append([t-(n/10)+i/10.0,self.createRandomSignal(offset,t-(n/10)+i/10.0)])
            self.sp2.records[name]['data'] = np.array(testdata)

        ''' To remove a signal, reference it by name or use the in-built controls'''
        # sp.removeSignal(name='signal1')
        # sp.removeSignal(name='signal2')

        ''' Here we create a tab layout widget, and put the 3 stripplots into a grid layout in one of the tabs
            In the second tab we put the first stripplot. NB: the stripplot "sp" can only exist in one place at a time!
        '''
        self.tab = QTabWidget()
        self.plotLayout = QGridLayout()
        self.plotLayout.addWidget(self.sp2,0,0)
        self.plotLayout.addWidget(self.sp3,1,0)
        self.timeButtonList = []
        self.timeButton10 = self.createTimeButton('10s')
        self.timeButton60 = self.createTimeButton('1m')
        self.timeButton600 = self.createTimeButton('10m')
        self.timeButton6000 = self.createTimeButton('100m')
        self.timeButton60000 = self.createTimeButton('1000m')
        self.timeButtonLayout = QHBoxLayout()
        self.timeButtonLayout.addWidget(self.timeButton10)
        self.timeButtonLayout.addWidget(self.timeButton60)
        self.timeButtonLayout.addWidget(self.timeButton600)
        self.timeButtonLayout.addWidget(self.timeButton6000)
        self.timeButtonLayout.addWidget(self.timeButton60000)
        self.plotLayout.addLayout(self.timeButtonLayout,3,0,1,1)
        self.plotWidget = QFrame()
        self.plotWidget.setLayout(self.plotLayout)
        self.tab.addTab(self.plotWidget,"Strip Plot")
        self.tab.addTab(self.sp,"Strip Plot 1")
        ''' Here we connect the QTabWidget signal "currentChanged" to a function defined above. This will pause plots not currently visible
            whenever the tabs are changed. This reduces the load as only visible plots are updated. '''
        self.tab.currentChanged.connect(lambda x: self.pausePlots(self.tab))

        ''' Add loggerWidget Tab (requires loggerWidget - comment out if not available)'''
        # self.tab.addTab(self.logwidget1,"Log")

        ''' This starts the plotting timer (by default at 1 Hz) '''
        # self.sp.start()
        self.sp2.start()
        # self.sp3.start()

        ''' modify the plot scale to 10 secs '''
        self.sp.setPlotScale(600)
        self.sp2.setPlotScale(600*1)
        self.sp3.setPlotScale(600)

        # self.sp2.setPlotType(FFT=True)
        # self.sp3.setPlotType(FFT=False)
        self.sp.setPlotRate(10)
        self.sp2.setPlotRate(1)
        self.sp3.setPlotRate(10)

        ''' Display the Qt App '''
        self.setCentralWidget(self.tab)

        # self.sp.plotWidget.statusChanged.connect(self.updateStatusBar)
        # self.sp2.plotWidget.statusChanged.connect(self.updateStatusBar)
        # self.sp3.plotWidget.statusChanged.connect(self.updateStatusBar)
    ''' This is a signal generator. It could easily read a magnet current using the hardware controllers
        The signal should have peaks at 5 Hz and 10 Hz, which should be seen on the FFT plot assuming the
        sample rate is high enough
    '''
    def createRandomSignal(self, offset=0, t=None):
        if t == None:
            t = time.time()
        signalValue = np.sin(2*2*np.pi*t+0.05)+np.sin(1.384*2*np.pi*t-0.1)+0.5*np.random.normal()
        return signalValue+offset

    def createTimeButton(self,label):
        button = timeButton(label)
        button.timeButtonPushed.connect(self.changePlotScales)
        return button

    def changePlotScales(self, time):
        print( 'time = ', time)
        for plot in self.findChildren((striptool.stripPlot)):
            plot.setPlotScale(time)

    def pausePlots(self, parentwidget):
        widgets = parentwidget.findChildren((striptool.stripPlot))
        for widget in widgets:
            if widget.isVisible():
                widget.pausePlotting(False)
                widget.plotUpdate()
            else:
                widget.pausePlotting(True)

    def updateStatusBar(self,text):
        self.statusBar.clearMessage()
        self.statusBar.showMessage(text,2000)

    def testSleep(self):
        import time
        for i in range(100):
            self.sp.setPlotScale((i+1)*60)
            self.sp2.setPlotScale((i+1)*60)
            self.sp3.setPlotScale((i+1)*60)
            QtTest.QTest.qWait(1000*60)
        exit()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_F11:
            print( "Maximise!")
            self.sp.handleSignalValueTableSplitterButton(left=True)
            self.sp.strip.handleLegendSplitterButton(left=True)

    def closeEvent(self, event):
        for plot in self.findChildren((striptool.stripPlot)):
            plot.close()

def main():
   app = QApplication(sys.argv)
   # app.setStyle(QStyleFactory.create("plastique"))
   ex = striptool_Demo()
   ex.show()
   ex.pausePlots(ex.tab)
   # ex.testSleep()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()
