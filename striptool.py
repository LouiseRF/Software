import sys, time, os, datetime
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np
import threading
from threading import Thread, Event, Timer
from PyQt4.QtCore import QObject, pyqtSignal, pyqtSlot
import signal, datetime
from bisect import bisect_left, bisect_right
import peakutils
import logging
logger = logging.getLogger(__name__)

signal.signal(signal.SIGINT, signal.SIG_DFL)

tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

Qtableau20 = [QColor(i,j,k) for (i,j,k) in tableau20]

def takeClosestPosition(xvalues, myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(xvalues, myNumber)
    if pos == 0:
        return [0,myList[0]]
    if pos == len(myList):
        return [-1,myList[-1]]
    before = myList[pos-1]
    after = myList[pos]
    if abs(after[0] - myNumber) < abs(myNumber - before[0]):
       return [pos,after]
    else:
       return [pos-1,before]

def logthread(caller):
    print('%-25s: %s, %s,' % (caller, threading.current_thread().name,
                              threading.current_thread().ident))

class repeatedTimer:

    """Repeat `function` every `interval` seconds."""

    def __init__(self, interval, function, *args, **kwargs):
        self.interval = 1000*interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.thread = QtCore.QThread()
        self.worker = repeatedWorker(interval, function, *args, **kwargs)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.loop)
        self.thread.start()
        self.thread.setPriority(QThread.TimeCriticalPriority)

    def setInterval(self, interval):
        self.worker.setInterval(interval)


class repeatedWorker(QtCore.QObject):
    def __init__(self, interval, function, *args, **kwargs):
        super(repeatedWorker, self).__init__()
        self.interval = 1000.0*interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.prev = 1000.0*time.clock();

    def loop(self):
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        newinterval = self.interval - ((1000.0*time.clock()) % self.interval)
        self.prev = 1000.0*time.clock()
        if newinterval < 0:
            self.timer.singleShot(0, self._target)
        else:
            self.timer.singleShot(newinterval, self._target)

    def stop(self):
        self.timer.stop()

    def _target(self):
        self.function(*self.args, **self.kwargs)
        newinterval = self.interval - ((1000.0*time.clock()) % self.interval)
        while newinterval < 0.2*self.interval:
            time.sleep(0.001)
            newinterval = self.interval - ((1000.0*time.clock()) % self.interval)
        self.timer.singleShot(newinterval, self._target)

    def setInterval(self, interval):
        self.interval = 1000*interval

class threadedFunction:

    """Repeat `function` every `interval` seconds."""

    def __init__(self, worker):
        self.interval = 1000*interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.thread = QtCore.QThread()
        self.worker = worker
        self.worker.moveToThread(self.thread)
        self.thread.start()

class createSignalTimer(QObject):

    dataReady = QtCore.pyqtSignal(list)

    def __init__(self, name, function, *args):
        # Initialize the signal as a QObject
        QObject.__init__(self)
        self.function = function
        self.args = args
        self.name = name

    def startTimer(self, interval=1):
        self.timer = repeatedTimer(interval, self.update)

    def update(self):
        ''' call signal generating Function '''
        value = self.function(*self.args)
        self.dataReady.emit([time.time(),value])

class recordWorker(QtCore.QObject):
    def __init__(self, records, signal, name):
        super(recordWorker, self).__init__()
        self.records = records
        self.signal = signal
        self.name = name
        self.signal.dataReady.connect(self.updateRecord)

    @QtCore.pyqtSlot(list)
    def updateRecord(self, value):
        if len(self.records[self.name]['data']) > 1 and value[1] == self.records[self.name]['data'][-1][1]:
            self.records[self.name]['data'][-1] = value
        else:
            self.records[self.name]['data'].append(value)

class createSignalRecord(QObject):

    def __init__(self, records, name, timer, function, *args):
        # Initialize the PunchingBag as a QObject
        QObject.__init__(self)
        self.records = records
        self.records[name] = {'name': name, 'pen': 'r', 'timer': timer, 'function': function, 'ploton': True, 'data': []}
        self.name = name
        self.signal = createSignalTimer(name, function, *args)
        self.thread = QtCore.QThread()
        self.worker = recordWorker(self.records, self.signal, name)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.signal.startTimer(timer)

    def setInterval(self, newinterval):
        self.signal.timer.setInterval(newinterval)

    def stop(self):
        self.signal.timer.stop()

class CAxisTime(pg.AxisItem):
    ## Formats axis label to human readable time.
    # @param[in] values List of \c time_t.
    # @param[in] scale Not used.
    # @param[in] spacing Not used.
    def __init__(self, orientation=None, pen=None, linkView=None, parent=None, maxTickLength=-5, showValues=True):
        super(CAxisTime, self).__init__(parent=parent, orientation=orientation, linkView=linkView)
        self.dateTicksOn = True
        self.autoscroll = True
        self.fixedtimepoint = time.time()

    def tickStrings(self, values, scale, spacing):
        if self.dateTicksOn:
            if self.autoscroll:
                reftime = time.time()
            else:
                reftime = self.fixedtimepoint
            strns = []
            for x in values:
                try:
                    strns.append(time.strftime("%H:%M:%S", time.localtime(reftime+x)))    # time_t --> time.struct_time
                except ValueError:  # Windows can't handle dates before 1970
                    strns.append('')
            return strns
        else:
            return values

class generalPlot(pg.PlotWidget):
    changePlotScale = pyqtSignal('PyQt_PyObject')

    def __init__(self, record, parent = None):
        super(generalPlot, self).__init__(parent=parent)
        self.parent=parent
        self.records = record
        self.linearPlot = True
        self.histogramPlot = False
        self.FFTPlot = False
        self.scatterPlot = False
        self.doingPlot = False
        self.usePlotRange = True
        self.autoscroll = True
        self.decimateScale = 5000
        self.legend = pg.LegendItem(size=(100,100))
        self.legend.setParentItem(None)
        self.globalPlotRange = [-10,0]

    def createPlot(self):
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.date_axis = CAxisTime(orientation = 'bottom')
        self.plot = self.plotWidget.addPlot() #, axisItems = {'bottom': self.date_axis}
        nontimeaxisItems = {'bottom': self.plot.axes['bottom']['item'], 'top': self.plot.axes['top']['item'], 'left': self.plot.axes['left']['item'], 'right': self.plot.axes['right']['item']}
        axisItems = {'bottom': self.date_axis, 'top': self.plot.axes['top']['item'], 'left': self.plot.axes['left']['item'], 'right': self.plot.axes['right']['item']}
        self.plot.axes = {}
        for k, pos in (('top', (1,1)), ('bottom', (3,1)), ('left', (2,0)), ('right', (2,2))):
            if k in axisItems:
                axis = axisItems[k]
                axis.linkToView(self.plot.vb)
                self.plot.axes[k] = {'item': axis, 'pos': pos}
                self.plot.layout.removeItem(self.plot.layout.itemAt(*pos))
                self.plot.layout.addItem(axis, *pos)
                axis.setZValue(-1000)
                axis.setFlag(axis.ItemNegativeZStacksBehindParent)
        self.plot.showGrid(x=True, y=True)
        return self.plot

    def addCurve(self, record, plot, name):
        curve = self.curve(record, plot, name)
        return curve

    class curve(QObject):
        def __init__(self, record, plot, name):
            QObject.__init__(self)
            self.plotScale = None
            self.name = name
            self.plot = plot
            self.records = record
            # self.globalPlotRange = self.plot.globalPlotRange
            self.doingPlot = False
            self.curve = self.plot.plot.plot()
            self.addCurve()

        def addCurve(self):
            return self.curve

        def updateData(self, data, pen):
            if len(data) > 0 and not self.plot.scatterPlot:
                if self.plot.histogramPlot:
                    x,y = np.transpose(data)
                    y,x = np.histogram(y, bins=50)
                else:
                    x,y = np.transpose(data)
                if self.plot.histogramPlot:
                    self.curve.setData({'x': x, 'y': y}, pen=pen, stepMode=True, fillLevel=0)
                elif self.plot.FFTPlot:
                    self.curve.setData({'x': x, 'y': y}, pen=pen, stepMode=False)
                    indexes = peakutils.indexes(self.curve.yDisp, thres=0.75, min_dist=1)
                    self.plot.updateSpectrumMode(True)
                else:
                    self.curve.setData({'x': x, 'y': y}, pen=pen, stepMode=False)

        def timeFilter(self, datain, timescale):
            if self.plot.autoscroll:
                currenttime = time.time()
            else:
                currenttime =  self.plot.currenttime#list(reversed(data))[0][0]#self.plot.currenttime
            data = map(lambda x: [x[0]-currenttime, x[1]], datain)
            def func1(values):
                for x in reversed(values):
                    if x[0] > (self.plot.globalPlotRange[0]) :
                        yield x
                    else:
                        break
            newlist = list(func1(data))
            for x in reversed(newlist):
                if x[0] < (self.plot.globalPlotRange[1]):
                    yield x
                else:
                    break

        def filterRecord(self, data, timescale):
            return list(list(self.timeFilter(data, timescale)))

        def clear(self):
            self.curve.clear()

        def update(self):
            if not self.plot.paused and not self.doingPlot:
                self.doingPlot = True
                if self.records[self.name]['ploton']:
                    # start = time.clock()
                    self.plotData = self.filterRecord(self.records[self.name]['data'],self.plot.globalPlotRange)
                    if len(self.plotData) > 100*self.plot.decimateScale:
                        decimationfactor = int(np.floor(len(self.plotData)/self.plot.decimateScale))
                        self.plotData = self.plotData[0::decimationfactor]
                        self.updateData(self.plotData, self.records[self.name]['pen'])
                    else:
                        self.updateData(self.plotData, self.records[self.name]['pen'])
                else:
                    self.clear()
                self.doingPlot = False
    def setPlotScale(self, timescale, padding=0.0):
        if self.linearPlot:
            self.plotRange = timescale
            self.globalPlotRange = list(timescale)
            self.plot.vb.setRange(xRange=self.globalPlotRange, padding=0)

    def updatePlotScale(self, padding=0.0):
        if self.linearPlot:
            vbPlotRange = self.plot.vb.viewRange()[0]
            if vbPlotRange != [0,1]:
                self.globalPlotRange = self.plot.vb.viewRange()[0]
            self.plotRange = self.globalPlotRange

    def show(self):
        self.plotWidget.show()

    def togglePause(self, value):
        self.paused = value

    def toggleAutoScroll(self, value):
        self.autoscroll = value
        if not value:
            self.currenttime = self.currentPlotTime
            self.date_axis.fixedtimepoint = self.currentPlotTime
    #
    def updateScatterPlot(self):
        if self.scatterPlot and not self.doingPlot:
            self.doingPlot = True
            # self.legend.setParentItem(self.plot)
            # self.legend.items = []
            scatteritemnames=[]
            scatteritems=[]
            color=0
            for name in self.records:
                if self.records[name]['ploton']:
                    scatteritemnames.append(name)
            self.plot.clear()
            start = time.clock()
            for i in range(len(scatteritemnames)):
                for j in range(i+1, len(scatteritemnames)):
                    data1 = self.records[scatteritemnames[i]]['curve'].plotData
                    data2 = self.records[scatteritemnames[j]]['curve'].plotData
                    signalDelayTime1 = self.records[scatteritemnames[i]]['timer']
                    signalDelayTime2 = self.records[scatteritemnames[j]]['timer']
                    if data1[0] < data2[0]:
                        ans = takeClosestPosition(zip(*data1)[0], data1, data2[0][0])
                        starttime = ans[1]
                        startpos1 = ans[0]
                        startpos2 = 0
                    else:
                        ans = takeClosestPosition(zip(*data2)[0], data2, data1[0][0])
                        starttime = ans[1]
                        startpos1 = 0
                        startpos2 = ans[0]
                    data1 = data1[startpos1:-1]
                    data2 = data2[startpos2:-1]
                    if len(data1) > len(data2):
                        data1 = data1[0:len(data2)]
                    elif len(data2) > len(data1):
                        data2 = data2[0:len(data1)]
                    # if signalDelayTime1 != signalDelayTime2:
                    # if signalDelayTime1 > signalDelayTime2:
                    #     tmpdata1 = zip(*data1)[0]
                    #     data1 = [takeClosestPosition(tmpdata1, data1, timeval[0])[1] for timeval in data2]
                    # else:
                    #     tmpdata2 = zip(*data2)[0]
                    #     data2 = [takeClosestPosition(tmpdata2, data2, timeval[0])[1] for timeval in data1]
                    x1,x = zip(*data1)
                    x2,y = zip(*data2)
                    plotname = str(i+1)+" vs "+str(j+1)
                    s1 = pg.ScatterPlotItem(x=x, y=y, size=2, pen=pg.mkPen(None), brush=pg.mkBrush(Qtableau20[color]))
                    # self.legend.addItem(s1, plotname)
                    color += 1
                    self.plot.addItem(s1)
            self.doingPlot = False

class stripLegend(pg.TreeWidget):
    def __init__(self, record, parent = None):
        super(stripLegend, self).__init__(parent)
        self.records = record
        self.layout = pg.TreeWidget()
        self.layout.header().close()
        self.layout.setColumnCount(2)
        self.layout.header().setResizeMode(0,QtGui.QHeaderView.Stretch)
        self.layout.setColumnWidth(2,50)
        self.layout.header().setStretchLastSection(False)
        self.newRowNumber = 0
        self.deleteIcon  = QtGui.QIcon(str(os.path.dirname(os.path.abspath(__file__)))+'\icons\delete.png')

    def addTreeWidget(self, parent, name, text, widget):
        child = QtGui.QTreeWidgetItem()
        child.setText(0, text)
        parent.addChild(child)
        self.layout.setItemWidget(child,1,widget)
        return child

    def addLegendItem(self, name):
        parentTreeWidget = QtGui.QTreeWidgetItem([name])
        self.layout.addTopLevelItem(parentTreeWidget)
        plotOnOff = QCheckBox()
        plotOnOff.setChecked(True)
        plotOnOff.toggled.connect(lambda x: self.togglePlotOnOff(name, x))
        self.addTreeWidget(parentTreeWidget, name, "Plot On?", plotOnOff)
        signalRate = QComboBox()
        signalRate.setFixedSize(80,25)
        signalRate.setStyleSheet("subcontrol-origin: padding;\
        subcontrol-position: top right;\
        width: 15px;\
        border-left-width: 0px;\
        border-left-color: darkgray;\
        border-left-style: solid;\
        border-top-right-radius: 3px; /* same radius as the QComboBox */\
        border-bottom-right-radius: 3px;\
         ")
        i = 0
        selected = 0
        for rate in [0.1,1,5,10,25,50,100]:
            signalRate.addItem(str(rate)+' Hz')
            if self.records[name]['timer'] == 1.0/rate:
                selected = i
            i += 1
        signalRate.setCurrentIndex(selected)
        signalRate.currentIndexChanged.connect(lambda x: self.changeSampleRate(name, signalRate))
        self.addTreeWidget(parentTreeWidget, name, "Signal Rate", signalRate)
        colorbox = pg.ColorButton()
        colorbox.setFixedSize(30,25)
        colorbox.setFlat(True)
        colorbox.setColor(self.records[name]['pen'])
        colorbox.sigColorChanged.connect(lambda x: self.changePenColor(name, x))
        colorbox.sigColorChanging.connect(lambda x: self.changePenColor(name, x))
        self.addTreeWidget(parentTreeWidget, name, "Plot Color", colorbox)
        saveButton = QPushButton('Save Data')
        saveButton.setFixedSize(74,20)
        saveButton.setFlat(True)
        saveButton.clicked.connect(lambda x: self.saveCurve(name))
        self.addTreeWidget(parentTreeWidget, name, "Save Signal", saveButton)
        resetButton = QPushButton('Clear')
        resetButton.setFixedSize(50,20)
        resetButton.setFlat(True)
        resetButton.clicked.connect(lambda x: self.clearCurve(name))
        self.addTreeWidget(parentTreeWidget, name, "Clear Signal", resetButton)
        deleteRowButton = QPushButton()
        deleteRowButton.setFixedSize(50,20)
        deleteRowButton.setFlat(True)
        deleteRowButton.setIcon(self.deleteIcon)
        deleteRowChild = self.addTreeWidget(parentTreeWidget, name, "Delete Signal", deleteRowButton)
        deleteRowButton.clicked.connect(lambda x: self.deleteRow(name, deleteRowChild))
        self.newRowNumber += 1

    def formatCurveData(self, name):
        return [(str(time.strftime('%Y/%m/%d', time.localtime(x[0]))),str(datetime.datetime.fromtimestamp(x[0]).strftime('%H:%M:%S.%f')),x[1]) for x in self.records[name]['data']]

    def saveCurve(self, name, saveFileName=None):
        if saveFileName == None:
            saveFileName = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Array ['+name+']', name, filter="CSV files (*.csv);; Binary Files (*.bin)", selectedFilter="CSV files (*.csv)"))
        filename, file_extension = os.path.splitext(saveFileName)
        saveData = self.formatCurveData(name)
        if file_extension == '.csv':
            fmt='%s,%s,%.18e'
            target = open(saveFileName,'w')
            for row in saveData:
                target.write((fmt % tuple(row))+'\n')
            target.close()
        elif file_extension == '.bin':
            np.array(self.records[name]['data']).tofile(saveFileName)
        else:
            np.save(saveFileName,np.array(self.records[name]['data']))

    def changePenColor(self, name, widget):
        self.records[name]['pen'] = widget._color

    def togglePlotOnOff(self, name, value):
        self.records[name]['ploton'] = value

    def changeSampleRate(self, name, widget):
        string = str(widget.currentText())
        number = [int(s) for s in string.split() if s.isdigit()][0]
        value = 1.0/float(number)
        self.records[name]['timer'] = value
        self.records[name]['record'].setInterval(value)

    def clearCurve(self, name):
        self.records[name]['data'] = []
        self.records[name]['curve'].clear()

    def deleteRow(self, name, child):
        row = self.layout.indexOfTopLevelItem(child.parent())
        self.layout.takeTopLevelItem(row)
        self.records[name]['record'].stop()
        self.clearCurve(name)
        del self.records[name]

class stripPlot(QWidget):

    def __init__(self, parent = None, plotRateBar=True):
        super(stripPlot, self).__init__(parent)
        self.pg = pg
        self.paused = True
        self.signalLength = 10
        self.plotrate = 1
        self.plotScaleConnection = True
        self.pauseIcon  =  QtGui.QIcon(str(os.path.dirname(os.path.abspath(__file__)))+'\icons\pause.png')

        ''' create the stripPlot.stripPlot as a grid layout '''
        self.stripPlot = QtGui.QGridLayout()
        self.plotThread = QTimer()
        ''' Create generalPlot object '''
        self.plotWidget = generalPlot(self.parent())
        ''' Create the plot as part of the plotObject '''
        self.plot = self.plotWidget.createPlot()
        ''' Create the signalRecord object '''
        self.records = {}

        ''' Sidebar for graph type selection '''
        self.buttonLayout = QtGui.QVBoxLayout()
        self.linearRadio = QRadioButton("Linear")
        self.linearRadio.setChecked(True)
        self.linearRadio.toggled.connect(lambda: self.setPlotType(linear=True))
        self.buttonLayout.addWidget(self.linearRadio,0)
        self.HistogramRadio = QRadioButton("Histogram")
        self.HistogramRadio.toggled.connect(lambda: self.setPlotType(histogram=True))
        self.buttonLayout.addWidget(self.HistogramRadio,1)
        self.FFTRadio = QRadioButton("FFT")
        self.FFTRadio.toggled.connect(lambda: self.setPlotType(FFT=True))
        self.buttonLayout.addWidget(self.FFTRadio,2)
        # self.ScatterRadio = QRadioButton("Scatter")
        # self.ScatterRadio.toggled.connect(lambda: self.setPlotType(scatter=True))
        # self.buttonLayout.addWidget(self.ScatterRadio,3)
        ''' Create H Layout for scroll/pause '''
        self.autoscrollPauseLayout = QtGui.QHBoxLayout()
        ''' Add Autoscroll checkbox '''
        self.scrollButton = QCheckBox()
        self.scrollButton.setChecked(True)
        self.scrollButtonLabel = QtGui.QLabel()
        self.scrollButtonLabel.setText('Autoscroll')
        self.scrollButtonLabel.setAlignment(Qt.AlignCenter)
        self.scrollButton.toggled.connect(self.toggleAutoScroll)
        self.autoscrollPauseLayout.addWidget(self.scrollButtonLabel,0)
        self.autoscrollPauseLayout.addWidget(self.scrollButton,1)
        ''' Add Pause Button '''
        self.pauseButton = QPushButton()
        self.pauseButton.setIcon(self.pauseIcon)
        self.pauseButton.setFixedSize(50,20)
        self.pauseButton.setStyleSheet("border: 5px; background-color: white")
        # self.pauseButton.setFlat(False)
        self.pauseButton.clicked.connect(self.togglePause)
        self.autoscrollPauseLayout.addWidget(self.pauseButton,2)
        ''' Add scroll/pause to main layout '''
        self.buttonLayout.addLayout(self.autoscrollPauseLayout,3)

        ''' Initialise stripLegend Object '''
        self.legend = stripLegend(record=self.records)
        self.buttonLayout.addWidget(self.legend.layout,4)
        ''' Add sidebar  to main layout'''
        self.GUISplitter = QtGui.QSplitter()
        self.GUISplitter.setHandleWidth(10)
        self.GUISplitter.addWidget(self.plotWidget.plotWidget)
        self.buttonFrame = QtGui.QFrame()
        self.buttonFrame.setLayout(self.buttonLayout)
        self.GUISplitter.addWidget(self.buttonFrame)
        self.GUISplitter.setStyleSheet("QSplitter::handle{background-color:transparent;}");
        handle = self.GUISplitter.handle(1)
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.splitterbutton = QtGui.QToolButton(handle)
        self.splitterbutton.setArrowType(QtCore.Qt.LeftArrow)
        self.splitterbutton.clicked.connect(
            lambda: self.handleSplitterButton(False))
        self.GUISplitter.splitterMoved.connect(self.handleSplitterButtonArrow)
        layout.addWidget(self.splitterbutton)
        handle.setLayout(layout)
        self.GUISplitter.setSizes([1,0])
        self.stripPlot.addWidget(self.GUISplitter,0,0,5,2)
        self.setupPlotRateSlider()
        if plotRateBar:
            self.stripPlot.addWidget(self.plotRateLabel,5, 0)
            self.stripPlot.addWidget(self.plotRateSlider,5, 1)
        self.setLayout(self.stripPlot)
        self.togglePause()
        self.plotThread.timeout.connect(lambda: self.plotWidget.date_axis.linkedViewChanged(self.plotWidget.date_axis.linkedView()))
        self.plotWidget.plot.vb.sigXRangeChanged.connect(self.setPlotScaleLambda)
        # self.plotThread.timeout.connect(self.plotWidget.updateScatterPlot)
        logger.debug('stripPlot initiated!')
        # self.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

    def saveAllCurves(self, saveFileName=None):
        for name in self.records:
            if self.records[name]['parent'] == self:
                filename, file_extension = os.path.splitext(saveFileName)
                saveFileName2 = filename + '_' + self.records[name]['name'] + file_extension
                self.legend.saveCurve(self.records[name]['name'],saveFileName2)

    def saveCurve(self, name, saveFileName=None):
        self.legend.saveCurve(name,saveFileName)

    def setWidth(self, width=16777215):
        self.stripPlot.setMaximumWidth(width)

    def setHeight(self, height=16777215):
        self.stripPlot.setMaximumHeight(height)

    def setWidthHeight(self, height, width):
        self.setWidth(width)
        self.setHeight(height)

    def setQSize(self, heightwidth):
        self.setWidth(0.95*heightwidth.width())
        self.setHeight(0.95*heightwidth.height())

    def handleSplitterButton(self, left=True):
        sizes = self.GUISplitter.sizes()
        totalsize = sum(sizes)
        if not all(self.GUISplitter.sizes()):
            # logger.debug('splitter new sizes = '+str(totalsize))
            self.GUISplitter.setSizes([200,200])
            # self.GUISplitter.setSizes([1, 1000])
            # self.splitterbutton.setArrowType(QtCore.Qt.RightArrow)
        elif left:
            self.GUISplitter.setSizes([0, 1])
            # self.splitterbutton.setArrowType(QtCore.Qt.LeftArrow)
        else:
            self.GUISplitter.setSizes([1, 0])
            # self.splitterbutton.setArrowType(QtCore.Qt.LeftArrow)
        self.handleSplitterButtonArrow()

    def handleSplitterButtonArrow(self):
        sizes = self.GUISplitter.sizes()
        if self.GUISplitter.sizes()[1] > 0:
            self.splitterbutton.setArrowType(QtCore.Qt.RightArrow)
        else:
            self.splitterbutton.setArrowType(QtCore.Qt.LeftArrow)

    def setupPlotRateSlider(self):
        self.plotRateLabel = QtGui.QLabel()
        self.plotRateLabel.setText('Plot Update Rate ['+str(self.plotrate)+' Hz]:')
        self.plotRateLabel.setAlignment(Qt.AlignCenter)
        self.plotRateSlider = QtGui.QSlider()
        self.plotRateSlider.setOrientation(QtCore.Qt.Horizontal)
        self.plotRateSlider.setInvertedAppearance(False)
        self.plotRateSlider.setInvertedControls(False)
        self.plotRateSlider.setMinimum(1)
        self.plotRateSlider.setMaximum(50)
        self.plotRateSlider.setValue(self.plotrate)
        self.plotRateSlider.valueChanged.connect(self.setPlotRate)

    def setPlotRate(self, value):
        self.plotrate = value
        self.plotRateLabel.setText('Plot Update Rate ['+str(self.plotrate)+' Hz]:')
        self.plotThread.setInterval(1000*1/value)

    def setPlotScaleLambda(self, widget, timescale):
        if self.plotScaleConnection:
            self.plotWidget.setPlotScale(timescale)

    def setPlotType(self, linear=False, histogram=False, FFT=False, scatter=False):
        self.plotScaleConnection = False
        if not(self.plotWidget.linearPlot == linear and self.plotWidget.histogramPlot == histogram and self.plotWidget.FFTPlot == FFT and self.plotWidget.scatterPlot == scatter):
            self.plotWidget.linearPlot = linear
            self.plotWidget.histogramPlot = histogram
            self.plotWidget.FFTPlot = FFT
            self.plotWidget.scatterPlot = scatter
            if linear:
                logger.debug('LinearPlot enabled')
            if histogram:
                logger.debug('Histogram enabled')
            if FFT:
                logger.debug('FFTPlot enabled')
            if scatter:
                logger.debug('ScatterPlot enabled')
            if scatter:
                self.plotWidget.date_axis.dateTicksOn = False
                self.plotWidget.updateScatterPlot()
                self.plot.enableAutoRange()
            else:
                try:
                    self.plotWidget.legend.scene().removeItem(self.plotWidget.legend)
                except:
                    pass
                self.plot.clear()
                for name in self.records:
                    if self.records[name]['parent'] == self:
                        self.plot.addItem(self.records[name]['curve'].curve)
                self.plot.updateSpectrumMode(False)
                for name in self.records:
                    if self.records[name]['parent'] == self:
                        self.records[name]['curve'].update()
                if FFT:
                    self.plot.updateSpectrumMode(True)
                else:
                    self.plot.updateSpectrumMode(False)
                if not linear:
                    self.plotWidget.date_axis.dateTicksOn = False
                    self.plot.enableAutoRange()
                else:
                    self.plotWidget.date_axis.dateTicksOn = True
                    self.plot.disableAutoRange()
                    self.plotWidget.setPlotScale([self.plotWidget.plotRange[0],self.plotWidget.plotRange[1]])
                    self.plotScaleConnection = True

    def start(self, timer=1000):
        self.plotThread.start(timer)
        self.plotThread.timeout.connect(self.plotUpdate)

    def addSignal(self, name, pen, timer, function, *args):
        if not name in self.records:
            signalrecord = createSignalRecord(records=self.records, name=name, timer=timer, function=function, *args)
            self.records[name]['record'] = signalrecord
        else:
            logger.warning('Signal '+name+' already exists!')
            nameorig = name
            name = name + '_2'
            signalrecord = createSignalRecord(records=self.records, name=name, timer=timer, function=function, *args)
            self.records[name]['record'] = signalrecord
        curve = self.plotWidget.addCurve(self.records, self.plotWidget, name)
        self.records[name]['curve'] = curve
        self.records[name]['parent'] = self
        self.records[name]['pen'] = pen
        self.legend.addLegendItem(name)
        logger.info('Signal '+name+' added!')

    def plotUpdate(self):
        self.currentPlotTime = time.time()
        for name in self.records:
            self.records[name]['curve'].update()
        self.plotWidget.updateScatterPlot()

    def removeSignal(self,name):
        self.plotThread.timeout.disconnect(self.records[name]['curve'].update)
        del self.records[name]
        logger.info('Signal '+name+' removed!')

    def setPlotScale(self, timescale):
        self.plotWidget.setPlotScale([-1.05*timescale, 0.05*timescale])

    def pausePlotting(self, value=True):
        self.paused = value
        self.plotWidget.togglePause(self.paused)

    def togglePause(self):
        if self.paused:
            self.paused = False
            self.pauseButton.setStyleSheet("border: 5px; background-color: white")
            logger.debug('Plot un-paused!')
        else:
            self.paused = True
            self.pauseButton.setStyleSheet("border: 5px; background-color: red")
            logger.debug('Plot Paused!')
        self.plotWidget.togglePause(self.paused)

    def toggleAutoScroll(self):
        self.plotWidget.date_axis.autoscroll = self.scrollButton.isChecked()
        self.plotWidget.toggleAutoScroll(self.scrollButton.isChecked())

    def setDecimateLength(self, value=5000):
        self.plotWidget.decimateScale = value