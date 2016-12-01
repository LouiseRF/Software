import sys
from PyQt4 import QtCore, QtGui
import logging
import os
import zmq, time
import threading
from threading import Thread, Event, Timer

widgetLogger = logging.getLogger(__name__)

colournames = {
'aliceblue':            '#F0F8FF',
'antiquewhite':         '#FAEBD7',
'aqua':                 '#00FFFF',
'aquamarine':           '#7FFFD4',
'azure':                '#F0FFFF',
'beige':                '#F5F5DC',
'bisque':               '#FFE4C4',
'black':                '#000000',
'blanchedalmond':       '#FFEBCD',
'blue':                 '#0000FF',
'blueviolet':           '#8A2BE2',
'brown':                '#A52A2A',
'burlywood':            '#DEB887',
'cadetblue':            '#5F9EA0',
'chartreuse':           '#7FFF00',
'chocolate':            '#D2691E',
'coral':                '#FF7F50',
'cornflowerblue':       '#6495ED',
'cornsilk':             '#FFF8DC',
'crimson':              '#DC143C',
'cyan':                 '#00FFFF',
'darkblue':             '#00008B',
'darkcyan':             '#008B8B',
'darkgoldenrod':        '#B8860B',
'darkgray':             '#A9A9A9',
'darkgreen':            '#006400',
'darkkhaki':            '#BDB76B',
'darkmagenta':          '#8B008B',
'darkolivegreen':       '#556B2F',
'darkorange':           '#FF8C00',
'darkorchid':           '#9932CC',
'darkred':              '#8B0000',
'darksalmon':           '#E9967A',
'darkseagreen':         '#8FBC8F',
'darkslateblue':        '#483D8B',
'darkslategray':        '#2F4F4F',
'darkturquoise':        '#00CED1',
'darkviolet':           '#9400D3',
'deeppink':             '#FF1493',
'deepskyblue':          '#00BFFF',
'dimgray':              '#696969',
'dodgerblue':           '#1E90FF',
'firebrick':            '#B22222',
'floralwhite':          '#FFFAF0',
'forestgreen':          '#228B22',
'fuchsia':              '#FF00FF',
'gainsboro':            '#DCDCDC',
'ghostwhite':           '#F8F8FF',
'gold':                 '#FFD700',
'goldenrod':            '#DAA520',
'gray':                 '#808080',
'green':                '#008000',
'greenyellow':          '#ADFF2F',
'honeydew':             '#F0FFF0',
'hotpink':              '#FF69B4',
'indianred':            '#CD5C5C',
'indigo':               '#4B0082',
'ivory':                '#FFFFF0',
'khaki':                '#F0E68C',
'lavender':             '#E6E6FA',
'lavenderblush':        '#FFF0F5',
'lawngreen':            '#7CFC00',
'lemonchiffon':         '#FFFACD',
'lightblue':            '#ADD8E6',
'lightcoral':           '#F08080',
'lightcyan':            '#E0FFFF',
'lightgoldenrodyellow': '#FAFAD2',
'lightgreen':           '#90EE90',
'lightgray':            '#D3D3D3',
'lightpink':            '#FFB6C1',
'lightsalmon':          '#FFA07A',
'lightseagreen':        '#20B2AA',
'lightskyblue':         '#87CEFA',
'lightslategray':       '#778899',
'lightsteelblue':       '#B0C4DE',
'lightyellow':          '#FFFFE0',
'lime':                 '#00FF00',
'limegreen':            '#32CD32',
'linen':                '#FAF0E6',
'magenta':              '#FF00FF',
'maroon':               '#800000',
'mediumaquamarine':     '#66CDAA',
'mediumblue':           '#0000CD',
'mediumorchid':         '#BA55D3',
'mediumpurple':         '#9370DB',
'mediumseagreen':       '#3CB371',
'mediumslateblue':      '#7B68EE',
'mediumspringgreen':    '#00FA9A',
'mediumturquoise':      '#48D1CC',
'mediumvioletred':      '#C71585',
'midnightblue':         '#191970',
'mintcream':            '#F5FFFA',
'mistyrose':            '#FFE4E1',
'moccasin':             '#FFE4B5',
'navajowhite':          '#FFDEAD',
'navy':                 '#000080',
'oldlace':              '#FDF5E6',
'olive':                '#808000',
'olivedrab':            '#6B8E23',
'orange':               '#FFA500',
'orangered':            '#FF4500',
'orchid':               '#DA70D6',
'palegoldenrod':        '#EEE8AA',
'palegreen':            '#98FB98',
'paleturquoise':        '#AFEEEE',
'palevioletred':        '#DB7093',
'papayawhip':           '#FFEFD5',
'peachpuff':            '#FFDAB9',
'peru':                 '#CD853F',
'pink':                 '#FFC0CB',
'plum':                 '#DDA0DD',
'powderblue':           '#B0E0E6',
'purple':               '#800080',
'red':                  '#FF0000',
'rosybrown':            '#BC8F8F',
'royalblue':            '#4169E1',
'saddlebrown':          '#8B4513',
'salmon':               '#FA8072',
'sandybrown':           '#FAA460',
'seagreen':             '#2E8B57',
'seashell':             '#FFF5EE',
'sienna':               '#A0522D',
'silver':               '#C0C0C0',
'skyblue':              '#87CEEB',
'slateblue':            '#6A5ACD',
'slategray':            '#708090',
'snow':                 '#FFFAFA',
'springgreen':          '#00FF7F',
'steelblue':            '#4682B4',
'tan':                  '#D2B48C',
'teal':                 '#008080',
'thistle':              '#D8BFD8',
'tomato':               '#FF6347',
'turquoise':            '#40E0D0',
'violet':               '#EE82EE',
'wheat':                '#F5DEB3',
'white':                '#FFFFFF',
'whitesmoke':           '#F5F5F5',
'yellow':               '#FFFF00',
'yellowgreen':          '#9ACD32'}

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class colourNameError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    def __init__(self, expr, msg):
        self.expr = expr
        self.msg = msg

def getColour(label):
    return colournames[label.lower()]

class zmqPublishLogger(logging.Handler):
    def __init__(self, ipaddress='127.0.0.1', port=5556, publishname=__name__):
        super(zmqPublishLogger, self).__init__()
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.ipaddress = str(ipaddress)
        self.port = str(port)
        print self.port
        print "tcp://%s:%s" % (self.ipaddress,self.port)
        self.socket.bind("tcp://%s:%s" % (self.ipaddress,self.port))
        self.publisher = publishname
        time.sleep(0.2)

    def emit(self, record, *args, **kwargs):
        self.socket.send_pyobj([self.publisher, record.levelno, record.message])

class QPlainTextEditLogger(logging.Handler):
    def __init__(self, tableWidget):
        super(QPlainTextEditLogger, self).__init__()
        self.tableWidget = tableWidget
        self.debugColour = 'gray'
        self.infoColour = 'black'
        self.warningColour = 'deeppink'
        self.errorColour = 'red'
        self.criticalColor = 'red'

    def emit(self, record, *args, **kwargs):
        newRowNumber = self.tableWidget.rowCount()
        self.tableWidget.insertRow(newRowNumber)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setColumnWidth(0,140)#TIM EDIT"""
        self.tableWidget.setColumnWidth(1,40)#TIM EDIT"""
        self.tableWidget.setColumnWidth(2,40)# TIM EDIT"""
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setWordWrap(True)
        msg = self.format(record)
        color = ''
        if(record.levelname == 'DEBUG'):
            color = '<font style=\"color:'+getColour(self.debugColour)+'\">'
        elif(record.levelname == 'INFO'):

            color = '<font color=\"Green\">'
            color = '<font style=\"color:'+getColour(self.infoColour)+'\">'
            
        elif(record.levelname == 'WARNING'):
            color = '<font style=\"color:'+getColour(self.warningColour)+'\">'
        elif(record.levelname == 'ERROR'):
            color = '<font style=\"color:'+getColour(self.errorColour)+'\">'
        elif(record.levelname == 'CRITICAL'):
            color = '<font style="color:'+getColour(self.criticalColor)+'; font-weight:bold">'
        try:
            record.sender
        except:
            record.sender = record.name
        logdata = [record.asctime, record.sender, record.levelname, record.message]
        for i in range(4):
            self.textbox = QtGui.QPlainTextEdit()
            self.textbox.setReadOnly(True)
            self.textbox.appendHtml(color+str(logdata[i])+'</font>')
            self.tableWidget.setCellWidget(newRowNumber, i, self.textbox)

class loggerNetwork(QtCore.QObject):
    def __init__(self, logger=None, **kwargs):
        super(loggerNetwork,self).__init__()
        self.networkLogger = zmqPublishLogger(**kwargs)
        if(logger != None):
            if(isinstance(logger, list)):
                for log in logger:
                    self.addLogger(log)
            else:
                self.addLogger(logger)
        self.networkLogger.setFormatter(logging.Formatter(' %(asctime)s - %(name)s - %(levelno)s - %(message)s'))
        self.addLogger(widgetLogger)

    def addLogger(self, logger):
        logger.addHandler(self.networkLogger)
        logger.setLevel(logging.DEBUG)


class loggerWidget(QtGui.QWidget):
    def __init__(self, logger=None, zmq=False, parent=None):
        super(loggerWidget,self).__init__(parent)
        self.tablewidget = QtGui.QTableWidget()
        layout = QtGui.QGridLayout()
        saveButton = QtGui.QPushButton('Save Log')
        saveButton.setFixedSize(74,20)
        saveButton.setFlat(True)
        saveButton.clicked.connect(self.saveLog)
        layout.addWidget(self.tablewidget,0,0,10,3)
        layout.addWidget(saveButton,10,1,1,1)
        self.logTextBox = QPlainTextEditLogger(self.tablewidget)
        self.setLayout(layout)
        if(logger != None):
            if(isinstance(logger, list)):
                for log in logger:
                    self.addLogger(log)
            else:
                self.addLogger(logger)
        self.logTextBox.setFormatter(logging.Formatter(' %(asctime)s - %(name)s - %(levelno)s - %(message)s'))
        self.addLogger(widgetLogger)

    def setDebugColour(self, colour):
        try:
            getColour(colour)
        except:
            colour = 'gray'
        finally:
            self.logTextBox.debugColour = colour

    def setInfoColour(self, colour):
        try:
            getColour(colour)
        except:
            colour = 'black'
        finally:
            self.logTextBox.infoColour = colour

    def setWarningColour(self, colour):
        try:
            getColour(colour)
        except:
            colour = 'deeppink'
        finally:
            self.logTextBox.warningColour = colour

    def setErrorColour(self, colour):
        try:
            getColour(colour)
        except:
            colour = 'red'
        finally:
            self.logTextBox.errorColour = colour

    def setCriticalColour(self, colour):
        try:
            getColour(colour)
        except:
            colour = 'red'
        finally:
            self.logTextBox.criticalColor = colour

    def setLogColours(self, debugcolour='gray', infocolour='black', warningcolour='deeppink', errorcolour='red',criticalcolour='red'):
        self.setDebugColour(debugcolour)
        self.setInfoColour(infocolour)
        self.setWarningColour(warningcolour)
        self.setErrorColour(errorcolour)
        self.setCriticalColour(criticalcolour)

    def addLogger(self, logger):
        logger.addHandler(self.logTextBox)
        logger.setLevel(logging.DEBUG)

    def setLoggerLevel(self, logger, level=logging.DEBUG):
        logger.setLevel(level)

    def saveLog(self):
        rows = self.tablewidget.rowCount()
        saveData = range(rows);
        for r in range(rows):
            row = range(4)
            for i in range(4):
                widg = self.tablewidget.cellWidget(r, i)
                row[i] = widg.toPlainText()
            saveData[r] = row
        # print saveData
        saveFileName = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Log', filter="TXT files (*.txt);;", selectedFilter="TXT files (*.txt)"))
        filename, file_extension = os.path.splitext(saveFileName)
        if file_extension == '.txt':
        #     print "csv!"
            fmt='%s \t %s \t %s \t %s'
            target = open(saveFileName,'w')
            for row in saveData:
                target.write((fmt % tuple(row))+'\n')
        widgetLogger.info('Log Saved to '+saveFileName)


class redirectLogger(object):
    """File-like object to log text using the `logging` module."""

    def __init__(self, widget=None, name=None):
        self.logger = logging.getLogger(name)
        widget.addLogger(self.logger)

    def write(self, msg, level=logging.INFO):
        if msg != '\n':
            self.logger.log(level, msg)

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()
