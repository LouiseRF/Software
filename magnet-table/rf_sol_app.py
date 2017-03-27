#!python2
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui, uic
from rf_sol_tracking import RFSolTracker
import pyqtgraph as pg
import numpy as np
import os
import VELA_CLARA_MagnetControl as MagCtrl

os.environ["EPICS_CA_AUTO_ADDR_LIST"] = "NO"
os.environ["EPICS_CA_MAX_ARRAY_BYTES"] = "10000000"

## Switch to using dark grey background and white foreground
pg.setConfigOption('background', 0.2)
pg.setConfigOption('foreground', 'w')

image_credits = {
    'Offline.png': 'http://www.iconarchive.com/show/windows-8-icons-by-icons8/Network-Disconnected-icon.html',
    'Virtual.png': 'https://thenounproject.com/search/?q=simulator&i=237636',
    'Physical.png': 'http://www.flaticon.com/free-icon/car-compact_31126#term=car&page=1&position=19',
    'mountain-summit.png': 'http://www.flaticon.com/free-icon/mountain-summit_27798#term=peak&page=1&position=6'}
qtCreatorFile = "rf_sol_gui.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

def noFeedback(method):
    """Wrapper to prevent feedback loops - don't keep cycling through (e.g.) current <-> field calculations."""
    def feedbackless(*args, **kw):
        if sys._getframe(1).f_code.co_name == '<module>':
            return method(*args, **kw)
    return feedbackless


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        #TODO: get initial parameters from INI file, and save them as we go
        self.gun = RFSolTracker('Gun-10')
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.E_field_plot.setLabels(title='Electric field', left='E [MV/m]', bottom='z [m]')
        self.B_field_plot.setLabels(title='Magnetic field', left='B [T]', bottom='z [m]')
        self.momentum_plot.setLabels(title='Momentum', left='p [MeV/c]', bottom='z [m]')
        self.larmor_angle_plot.setLabels(title='Larmor angle', left='&theta;<sub>L</sub> [&deg;]', bottom='z [m]')
        self.E_field_plot.setLabels(title='E field', left='E [MV/m]', bottom='z [m]')
        self.xy_plot.setLabels(title='Particle position', left='x, y [mm]', bottom='z [m]')
        self.xy_plot.addLegend()
        self.xdash_ydash_plot.setLabels(title='Particle angle', left="x', y' [mrad]", bottom='z [m]')
        self.xdash_ydash_plot.addLegend()
        for plot in (self.E_field_plot, self.B_field_plot, self.momentum_plot,
                     self.larmor_angle_plot, self.E_field_plot, self.xy_plot, self.xdash_ydash_plot):
            plot.showGrid(True, True)

        self.peak_field_spin.valueChanged.connect(self.gunParamsChanged)
        self.phase_spin.valueChanged.connect(self.gunParamsChanged)
        self.crest_button.clicked.connect(self.crestButtonClicked)
        self.bc_spin.valueChanged.connect(self.solCurrentsChanged)
        self.sol_spin.valueChanged.connect(self.solCurrentsChanged)
        self.cathode_field_spin.valueChanged.connect(self.cathodeFieldChanged)
        self.sol_field_spin.valueChanged.connect(self.solPeakFieldChanged)
        self.momentum_spin.valueChanged.connect(self.momentumChanged)
        self.larmor_angle_spin.valueChanged.connect(self.larmorAngleChanged)
        for spin in (self.x_spin, self.xdash_spin, self.y_spin, self.ydash_spin):
            spin.valueChanged.connect(self.ustartChanged)

        self.magInit = MagCtrl.init()
        self.machine_mode_dropdown.activated.connect(self.machineModeChanged)
        self.machineModeChanged()
        self.update_period = 100  # milliseconds
        self.startMainViewUpdateTimer()
        self.gunParamsChanged()

    # these functions update the GUI and (re)start the timer
    def startMainViewUpdateTimer(self):
        self.widgetUpdateTimer = QtCore.QTimer()
        self.widgetUpdateTimer.timeout.connect(self.mainViewUpdate)
        self.widgetUpdateTimer.start(self.update_period)
    def mainViewUpdate(self):
        # conceivably the timer could restart this function before it complete - so guard against that
        try:
            if not self.machine_mode == 'Offline':
                if not self.bc_spin.hasFocus():
                    self.bc_spin.setValue(self.bc_ref.siWithPol)
                if not self.sol_spin.hasFocus():
                    self.sol_spin.setValue(self.sol_ref.siWithPol)
        finally:
            self.widgetUpdateTimer.start(self.update_period)

    def gunParamsChanged(self, value=None):
        """The gun parameters have been modified - rerun the simulation and update the GUI."""
        self.gun.setRFPeakField(self.peak_field_spin.value())
        self.gun.setRFPhase(self.phase_spin.value())
        self.E_field_plot.plot(self.gun.getZRange(), self.gun.getRFFieldMap() / 1e6, pen='r', clear=True)
        self.momentum_plot.plot(self.gun.getZRange(), self.gun.getMomentumMap(), pen='r', clear=True)
        self.momentum_spin.setValue(self.gun.getFinalMomentum())
        self.solCurrentsChanged()

    def crestButtonClicked(self):
        """Find the crest of the RF cavity."""
        self.phase_spin.setValue(self.gun.crestCavity())

    def solCurrentsChanged(self, value=None):
        """The bucking coil or solenoid parameters have been modified - rerun the simulation and update the GUI."""
        self.gun.setBuckingCoilCurrent(self.bc_spin.value())
        self.gun.setSolenoidCurrent(self.sol_spin.value())
        if not self.machine_mode == 'Offline':
            self.controller.setSI('BSOL', self.bc_spin.value())
            self.controller.setSI('SOL', self.sol_spin.value())
        self.cathode_field_spin.setValue(self.gun.getMagneticField(0))
        self.B_field_plot.plot(self.gun.getZRange(), self.gun.getMagneticFieldMap(), pen='r', clear=True)
        self.larmor_angle_plot.plot(self.gun.getZRange(), self.gun.getLarmorAngleMap(), pen='r', clear=True)
        self.larmor_angle_spin.setValue(self.gun.getFinalLarmorAngle())
        self.ustartChanged()

    @noFeedback
    def cathodeFieldChanged(self, value=None):
        """The cathode field has been modified - find the bucking coil current that gives this field."""
        self.bc_spin.setValue(self.gun.setCathodeField(value))

    @noFeedback
    def solPeakFieldChanged(self, value=None):
        """The solenoid peak field has been modified - find the solenoid current that gives this field."""
        self.sol_spin.setValue(self.gun.setPeakMagneticField(value))

    @noFeedback
    def momentumChanged(self, value=None):
        """The momentum has been modified - find the gun peak field that gives this value."""
        self.peak_field_spin.setValue(self.gun.setFinalMomentum(value))

    @noFeedback
    def larmorAngleChanged(self, value=None):
        """The Larmor angle has been modified - find the solenoid current that gives this value."""
        self.sol_spin.setValue(self.gun.setLarmorAngle(value))

    def ustartChanged(self, value=None):
        """The particle start position has been modified - track the particle through the fields."""
        uend = self.gun.trackBeam(1e-3 * np.matrix([spin.value() for spin in (self.x_spin, self.xdash_spin, self.y_spin, self.ydash_spin)], dtype='float').T)
        self.xy_plot.plotItem.legend.items = []
        self.xy_plot.plot(self.gun.getZRange(), 1e3 * self.gun.u_array[:, 0], pen='r', name='x', clear=True)
        self.xy_plot.plot(self.gun.getZRange(), 1e3 * self.gun.u_array[:, 2], pen='g', name='y')
        self.xdash_ydash_plot.plotItem.legend.items = []
        self.xdash_ydash_plot.plot(self.gun.getZRange(), 1e3 * self.gun.u_array[:, 1], pen='r', name="x'", clear=True)
        self.xdash_ydash_plot.plot(self.gun.getZRange(), 1e3 * self.gun.u_array[:, 3], pen='g', name="y'")
        self.uend_label.setText("<b>Final particle position</b> x {0:.3f} mm, x' {1:.3f} mrad; y {2:.3f} mm, y' {3:.3f} mrad".format(*uend.flat))

    def machineModeChanged(self, index=None):
        mode = str(self.machine_mode_dropdown.currentText())
        self.setMachineMode(mode)
        self.bc_ref = self.controller.getMagObjConstRef('BSOL')
        self.sol_ref = self.controller.getMagObjConstRef('SOL')

    def setMachineMode(self, mode=None):
        self.machine_mode = mode
        print('Setting machine mode:', mode)
        os.environ["EPICS_CA_ADDR_LIST"] = "192.168.83.255" if mode == 'Physical' else "10.10.0.12"
        self.controller = self.magInit.getMagnetController(MagCtrl.MACHINE_MODE.names[mode.upper()], MagCtrl.MACHINE_AREA.VELA_INJ)
        # self.settings.setValue('machine_mode', mode)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())