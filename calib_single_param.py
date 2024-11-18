# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# Calibration parameters setup window

from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QButtonGroup
from PyQt5.uic import loadUi
from calib_experiment import Experiment_view
import numpy as np

max_PA = 10.0 # [mA] define max amplitude here for safety reasons

class Calib_single_param_view(QMainWindow):
    def __init__(self):
        super(Calib_single_param_view,self).__init__()
        loadUi("QtDesigner//gui_calib_single_param.ui",self)
        #self.setFixedSize(800, 550)
        # This variable is for error handeling
        self.error = 0
        # Setting up acceptable input parameters
        self.setup_param_ranges()
        # IP spin boxes need special treatement to go always 1-10...
        self.setup_IP_special_requirement()
        # Only one parameter checkbox checked at a time
        self.param_checkbox_group = QButtonGroup(self)
        self.duration_checkbox_group = QButtonGroup(self)
        self.exclusive_checkboxes()
        # Initialize the paramters
        self.init_param_values()

        # Calculate length experiement array & check validity
        self.param_checkboxes = [self.C_PA, self.C_PW, self.C_IP, self.C_RP, self.C_F]
        self.timing_checkboxes = [self.C_SD, self.C_NT]
        self.connect_checkboxes()
        self.connect_spinboxes()

        # Start button clicked -> check parameters are valid -> if yes launch experiement , else error messege
        self.PB_START.clicked.connect(self.start_experiment)

    def setup_param_ranges(self):
        '''
        Set ranges of parameters as allowed in the specifications of the DS8R 
        '''
        self.SB_F_PA.setRange(0.0, max_PA) 
        self.SB_F_PA.setDecimals(1)
        self.SB_F_PA.setSingleStep(0.1)
        self.SB_PA_min.setRange(0.0, max_PA) 
        self.SB_PA_min.setDecimals(1)
        self.SB_PA_min.setSingleStep(0.1)
        self.SB_PA_max.setRange(0.0, max_PA) 
        self.SB_PA_max.setDecimals(1)
        self.SB_PA_max.setSingleStep(0.1)
        self.SB_PA_step.setRange(0.1, max_PA) 
        self.SB_PA_step.setDecimals(1)
        self.SB_PA_step.setSingleStep(0.1)
        
        self.SB_F_PW.setRange(50, 2000)
        self.SB_F_PW.setSingleStep(10)
        self.SB_PW_min.setRange(50, 2000)
        self.SB_PW_min.setSingleStep(10)
        self.SB_PW_max.setRange(50, 2000)
        self.SB_PW_max.setSingleStep(10)
        self.SB_PW_step.setRange(10, 1950)
        self.SB_PW_step.setSingleStep(10)
        self.SB_PW_step.editingFinished.connect(self.enforce_multiple_PW_step)
        
        self.SB_F_IP.setRange(1, 990)
        self.SB_IP_min.setRange(1, 990)
        self.SB_IP_max.setRange(1, 990)
        self.SB_IP_step.setRange(10, 990)

        self.SB_F_RP.setRange(10, 100)
        self.SB_F_RP.setSingleStep(1)
        self.SB_RP_min.setRange(10, 100)
        self.SB_RP_min.setSingleStep(1)
        self.SB_RP_max.setRange(10, 100)
        self.SB_RP_max.setSingleStep(1)
        self.SB_RP_step.setRange(1, 100)
        self.SB_RP_step.setSingleStep(1)

        self.SB_F_F.setRange(0, 1000)
        self.SB_F_F.setSingleStep(1)
        self.SB_F_min.setRange(0, 1000)
        self.SB_F_min.setSingleStep(1)
        self.SB_F_max.setRange(0, 1000)
        self.SB_F_max.setSingleStep(1)
        self.SB_F_step.setRange(1, 1000)
        self.SB_F_step.setSingleStep(1)

        self.SB_NR.setRange(1,1000)
        self.SB_NR.setSingleStep(1)

        self.SB_SD.setRange(1, 50000)
        self.SB_SD.setSingleStep(1)

        self.SB_NT.setRange(1, 500000)
        self.SB_NT.setSingleStep(1)

    def enforce_multiple_PW_step(self):
        '''
        PW step must be multiple of 10
        '''
        value = self.SB_PW_step.value()
        if value % 10 != 10:
            new_value = round(value / 10) * 10
            self.SB_PW_step.setValue(new_value)

    def setup_IP_special_requirement(self):
        '''
        Sets necessary constrains on interpulse values and connects the associated spinboxes
        '''
        self.enforce_IP_value_constraint(self.SB_F_IP)
        self.enforce_IP_value_constraint(self.SB_IP_min)
        self.enforce_IP_value_constraint(self.SB_IP_max)
        self.enforce_IP_value_constraint(self.SB_IP_step)
        
        self.SB_F_IP.editingFinished.connect(lambda: self.enforce_IP_value_constraint(self.SB_F_IP))
        self.SB_IP_min.editingFinished.connect(lambda: self.enforce_IP_value_constraint(self.SB_IP_min))
        self.SB_IP_max.editingFinished.connect(lambda: self.enforce_IP_value_constraint(self.SB_IP_max))
        self.SB_IP_step.editingFinished.connect(lambda: self.enforce_IP_value_constraint(self.SB_IP_step))

    def enforce_IP_value_constraint(self, spinBox):
        '''
        Restriction on Interphase Interval: 1µs - 990µs in 10µs steps
        Args:
            spinBox (self.SB...): The spin box that called this function 
        '''
        value = spinBox.value()
        reminder = value % 10
        if(reminder != 0):
            if value < 10:
                spinBox.setValue(value - reminder + 1)
            else:
                spinBox.setValue(value - reminder)
        
        if (value == 1):
            spinBox.setSingleStep(9)
        else:    
            spinBox.setSingleStep(10)

    def exclusive_checkboxes(self):
        '''
        Can only check on box at a time per group
        '''
        self.param_checkbox_group.addButton(self.C_PA)
        self.param_checkbox_group.addButton(self.C_PW)
        self.param_checkbox_group.addButton(self.C_IP)
        self.param_checkbox_group.addButton(self.C_RP)
        self.param_checkbox_group.addButton(self.C_F)

        self.param_checkbox_group.setExclusive(True)

        self.duration_checkbox_group.addButton(self.C_SD)
        self.duration_checkbox_group.addButton(self.C_NT)

        self.duration_checkbox_group.setExclusive(True)

    def init_param_values(self):
        '''
        Set up initial parameter values when window opens
        '''
        self.CB_M.setCurrentIndex(1)
        self.CB_POL.setCurrentIndex(0)
        self.CB_S.setCurrentIndex(0)

        self.SB_F_PA.setValue(1)
        self.SB_F_PW.setValue(1000)
        self.SB_F_IP.setValue(1)
        self.SB_F_RP.setValue(100)
        self.SB_F_F.setValue(1)

        self.SB_PA_min.setValue(0)
        self.SB_PW_min.setValue(50)
        self.SB_IP_min.setValue(1)
        self.SB_RP_min.setValue(10)
        self.SB_F_min.setValue(1)

        self.SB_PA_max.setValue(max_PA)
        self.SB_PW_max.setValue(2000)
        self.SB_IP_max.setValue(990)
        self.SB_RP_max.setValue(100)
        self.SB_F_max.setValue(1000)

        self.SB_PA_step.setValue(0.1)
        self.SB_PW_step.setValue(10)
        self.SB_IP_step.setValue(10)
        self.SB_RP_step.setValue(1)
        self.SB_F_step.setValue(1)

        self.SB_NR.setValue(1)
        self.SB_SD.setValue(1)
        self.SB_NT.setValue(1)

        self.C_PA.setChecked(True)
        self.C_SD.setChecked(True)

        # Update Number of experiment points
        self.update_expriment_pts(self.SB_PA_min.value(), self.SB_PA_max.value(), self.SB_PA_step.value())

        # Only spinboxes from variable parameter are enabled
        self.SB_F_PA.setEnabled(False)
        self.SB_PA_min.setEnabled(True)
        self.SB_PA_max.setEnabled(True)
        self.SB_PA_step.setEnabled(True)

        self.SB_PW_min.setEnabled(False)
        self.SB_PW_max.setEnabled(False)
        self.SB_PW_step.setEnabled(False)

        self.SB_IP_min.setEnabled(False)
        self.SB_IP_max.setEnabled(False)
        self.SB_IP_step.setEnabled(False)

        self.SB_RP_min.setEnabled(False)
        self.SB_RP_max.setEnabled(False)
        self.SB_RP_step.setEnabled(False)

        self.SB_F_min.setEnabled(False)
        self.SB_F_max.setEnabled(False)
        self.SB_F_step.setEnabled(False)

        self.SB_SD.setEnabled(True)
        self.SB_NT.setEnabled(False)

    def connect_checkboxes(self):
        '''
        When check box clicked
        '''
        for cbox in self.param_checkboxes:
            cbox.stateChanged.connect(self.on_param_cbox_change)
        for cbox in self.timing_checkboxes:
            cbox.stateChanged.connect(self.on_timing_cbox_change)

    def on_param_cbox_change(self):
        '''
        Enable/disable spinboxes depending on variable parameter 
        '''
        sender = self.sender()
        self.change_enable_SB(sender, True)
        if sender.isChecked():
            for cbox in self.param_checkboxes:
                if cbox != sender:
                    cbox.setChecked(False)
                    self.change_enable_SB(cbox, False)
        self.cbox_update_experiment_points(sender.text())

    def on_timing_cbox_change(self):
        '''
        Enable/disable spinboxes depending on timing parameter 
        '''
        sender = self.sender()
        if sender == self.C_SD:
            self.SB_SD.setEnabled(True)
            self.SB_NT.setEnabled(False)
        else:
            self.SB_SD.setEnabled(False)
            self.SB_NT.setEnabled(True)

    def change_enable_SB(self, cbox, state):
        '''
        Enables/Disables the variable/fixed parameter spinboxes 
        '''
        match cbox:
            case self.C_PA:
                self.SB_PA_min.setEnabled(state)
                self.SB_PA_max.setEnabled(state)
                self.SB_PA_step.setEnabled(state)
                self.SB_F_PA.setEnabled(not(state))
            case self.C_PW:
                self.SB_PW_min.setEnabled(state)
                self.SB_PW_max.setEnabled(state)
                self.SB_PW_step.setEnabled(state)
                self.SB_F_PW.setEnabled(not(state))
            case self.C_IP:
                self.SB_IP_min.setEnabled(state)
                self.SB_IP_max.setEnabled(state)
                self.SB_IP_step.setEnabled(state)
                self.SB_F_IP.setEnabled(not(state))
            case self.C_RP:
                self.SB_RP_min.setEnabled(state)
                self.SB_RP_max.setEnabled(state)
                self.SB_RP_step.setEnabled(state)
                self.SB_F_RP.setEnabled(not(state))
            case self.C_F:
                self.SB_F_min.setEnabled(state)
                self.SB_F_max.setEnabled(state)
                self.SB_F_step.setEnabled(state)
                self.SB_F_F.setEnabled(not(state))

    def cbox_update_experiment_points(self, cbox):
        '''
        Detect when parameter checkbox changed update the experiment-array and its length
        '''
        match cbox:
            case 'Pulse Amplitude [mA]':
                self.update_expriment_pts(self.SB_PA_min.value(), self.SB_PA_max.value(), self.SB_PA_step.value())
            case 'Pulse Width [us]':
                self.update_expriment_pts(self.SB_PW_min.value(), self.SB_PW_max.value(), self.SB_PW_step.value())
            case 'Interpulse [us]':
                self.update_expriment_pts(self.SB_IP_min.value(), self.SB_IP_max.value(), self.SB_IP_step.value())
            case 'Recovery Phase [%]':
                self.update_expriment_pts(self.SB_RP_min.value(), self.SB_RP_max.value(), self.SB_RP_step.value())
            case 'Frequency [Hz]':
                self.update_expriment_pts(self.SB_F_min.value(), self.SB_F_max.value(), self.SB_F_step.value())

    def connect_spinboxes(self):
        '''
        Dectect changes in parameter spinbox values & update exeriment array
        '''
        self.SB_PA_min.editingFinished.connect(self.on_param_SB_changed)
        self.SB_PA_max.editingFinished.connect(self.on_param_SB_changed)
        self.SB_PA_step.editingFinished.connect(self.on_param_SB_changed)

        self.SB_PW_min.editingFinished.connect(self.on_param_SB_changed)
        self.SB_PW_max.editingFinished.connect(self.on_param_SB_changed)
        self.SB_PW_step.editingFinished.connect(self.on_param_SB_changed)
        
        self.SB_IP_min.editingFinished.connect(self.on_param_SB_changed)
        self.SB_IP_max.editingFinished.connect(self.on_param_SB_changed)
        self.SB_IP_step.editingFinished.connect(self.on_param_SB_changed)

        self.SB_RP_min.editingFinished.connect(self.on_param_SB_changed)
        self.SB_RP_max.editingFinished.connect(self.on_param_SB_changed)
        self.SB_RP_step.editingFinished.connect(self.on_param_SB_changed)

        self.SB_F_min.editingFinished.connect(self.on_param_SB_changed)
        self.SB_F_max.editingFinished.connect(self.on_param_SB_changed)
        self.SB_F_step.editingFinished.connect(self.on_param_SB_changed)

        self.SB_NR.valueChanged.connect(self.update_L_TM)

    def on_param_SB_changed(self):
        '''
        Update experiment-array & length depending on which SB changed
        '''
        sender = self.sender()
        if sender in [self.SB_PA_min, self.SB_PA_max, self.SB_PA_step]:
                self.update_expriment_pts(self.SB_PA_min.value(), self.SB_PA_max.value(), self.SB_PA_step.value())
        elif sender in [self.SB_PW_min, self.SB_PW_max, self.SB_PW_step]:
                self.update_expriment_pts(self.SB_PW_min.value(), self.SB_PW_max.value(), self.SB_PW_step.value())
        elif sender in [self.SB_IP_min, self.SB_IP_max, self.SB_IP_step]:
                self.update_expriment_pts(self.SB_IP_min.value(), self.SB_IP_max.value(), self.SB_IP_step.value())
        elif sender in [self.SB_RP_min, self.SB_RP_max, self.SB_RP_step]:
                self.update_expriment_pts(self.SB_RP_min.value(), self.SB_RP_max.value(), self.SB_RP_step.value())
        elif sender in [self.SB_F_min, self.SB_F_max, self.SB_F_step]:
                self.update_expriment_pts(self.SB_F_min.value(), self.SB_F_max.value(), self.SB_F_step.value())

    def update_expriment_pts(self, min, max, step):
        '''
        Calculate experiment-array length whenever new values in spinboxs are entered
        This gives an idea on how long the experiment is
        '''
        if self.error == 11:
            self.error = 0   
        if max < min:
            self.error = 11
        if self.error == 0:
            self.generate_array(min, max, step)
            self.update_L_TM()
        self.update_error_msg() 

    def generate_array(self, min, max, step):
        '''
        Generate array & measure its length
        '''
        nb_points = int( ( max - min ) / step + 1) 
        self.experiment_pts = [min + i * step for i in range(nb_points)] # np.linspace(min, max, nb_points)
        self.len_array_calib_param = len(self.experiment_pts)

    def update_L_TM(self):
        '''
        update text on window with array length
        '''
        self.num_rep = self.len_array_calib_param * self.SB_NR.value()
        self.L_TM.setText('Total number of measurements: {}'.format(self.num_rep))

# Start button pushed
    def start_experiment(self):
        '''
        When START button pushed check for errors. If there is none format data to be sent to next window 
        and open experiment window 
        '''
        stimuli_T = self.calc_max_stimuli_period()
        self.check_trigger_freq(stimuli_T)
        if self.C_SD.isChecked():
            self.check_stimulation_duration(stimuli_T)
        elif self.C_NT.isChecked():
            if self.error == 3:
                self.error = 0

        if self.error == 0:
            self.update_error_msg()
            print('Parameter setup successful')
            
            fixed_param_hw = {}
            fixed_param_algo = {}
            variable_param = {}
            self.format_param(fixed_param_hw, fixed_param_algo, variable_param)
            # Open Experiment window
            self.experiment_window = Experiment_view(fixed_param_hw, fixed_param_algo, variable_param)
            self.experiment_window.show()
            # Close this window
            self.close() 
            
        else:
            self.update_error_msg()

    def calc_max_stimuli_period(self):
        '''
        Return the maximum period of the stimuli in [s]
        '''
        if self.C_PW.isChecked():
            maxPW = self.SB_PW_max.value()
        else:
            maxPW = self.SB_F_PW.value()
        if self.CB_M.currentIndex() == 1:
            if self.C_IP.isChecked():
                maxIP = self.SB_IP_max.value()
            else:
                maxIP = self.SB_F_IP.value()
            if self.C_RP.isChecked():
                maxRP = self.SB_RP_max.value()
            else:
                maxRP = self.SB_F_RP.value()
        else:
            maxIP = 0
            maxRP = 0
        return ( maxPW + maxIP + maxPW * maxRP * 0.01 ) * 10**-6
            
    def check_trigger_freq(self, stimuli_T):
        '''
        Check trigger period longer that stimuli period
        '''
        if self.error == 5:
            self.error = 0
        if self.C_F.isChecked():
            T = 1 / self.SB_F_max.value()
        else:
            T = 1 / self.SB_F_F.value()
        if T <= stimuli_T:
            self.error = 5

    def check_stimulation_duration(self, stimuli_T):
        '''
        Check stimulation time longer that stimuli period
        '''
        if self.error == 3:
            self.error = 0
        if (self.SB_SD.value() * 10**-3) < stimuli_T:
            self.error = 3

    def update_error_msg(self):
        '''
        List of text errors
        '''
        if self.error == 1:
            self.L_ERROR.setText('<b>Error: NOT USED, can be added if needed</b>')
        elif self.error == 2:
            self.L_ERROR.setText('<b>Error: NOT USED, can be added if needed</b>')
        elif self.error == 11:
            self.L_ERROR.setText('<b>Error: min value must be smaller than max value</b>')
        elif self.error == 3:
            self.L_ERROR.setText('<b>Error: Stimulation duration shorter than stimuli period</b>')
        elif self.error == 4:
            self.L_ERROR.setText('<b>Error: Number of triggers must be > 0</b>')
        elif self.error == 5:
            self.L_ERROR.setText('<b>Error: frequency faster than stimuli</b>')
        elif self.error == 0:
            self.L_ERROR.setText('')

    def format_param(self, fixed_param_hw, fixed_param_algo, variable_param):
        fixed_param_hw.update({
            'polarity': self.CB_POL.currentText(), 
            'mode': self.CB_M.currentText(),
            'source':self.CB_S.currentText(),
        })
        fixed_param_algo['numRepetition'] = self.SB_NR.value()
        for cbox in [self.C_SD, self.C_NT]:
            if cbox.isChecked():
                if cbox == self.C_SD:
                    fixed_param_algo.update({
                        'stimuDuration[ms]': self.SB_SD.value(), 
                        'numTriggers': 0
                    })
                else:
                    fixed_param_algo.update({
                        'stimuDuration[ms]': 0, 
                        'numTriggers': self.SB_NT.value()
                    })
        for cbox in self.param_checkboxes:
            if cbox.isChecked():
                match cbox:
                    case self.C_PA:
                        variable = 'demand'
                        min = self.SB_PA_min.value() 
                        max = self.SB_PA_max.value() 
                        step = self.SB_PA_step.value() 
                    case self.C_PW:
                        variable = 'pulsewidth'
                        min = self.SB_PW_min.value() 
                        max = self.SB_PW_max.value()
                        step = self.SB_PW_step.value()
                    case self.C_IP:
                        variable = 'dwell'
                        min = self.SB_IP_min.value() 
                        max = self.SB_IP_max.value()
                        step = self.SB_IP_step.value()
                    case self.C_RP:
                        variable = 'recovery'
                        min = self.SB_RP_min.value() 
                        max = self.SB_RP_max.value()
                        step = self.SB_RP_step.value()
                    case self.C_F:
                        variable = 'frequency'
                        min = self.SB_F_min.value() 
                        max = self.SB_F_max.value()
                        step = self.SB_F_step.value()
                variable_param.update({
                    'variable': variable,
                    'min': min,
                    'max': max,
                    'step': step
                })
            else:
                match cbox:
                    case self.C_PA:
                        fixed_param_hw['demand'] = self.SB_F_PA.value() 
                    case self.C_PW:
                        fixed_param_hw['pulsewidth'] = self.SB_F_PW.value()
                    case self.C_IP:
                        fixed_param_hw['dwell'] = self.SB_F_IP.value()
                    case self.C_RP:
                        fixed_param_hw['recovery'] = self.SB_F_RP.value()
                    case self.C_F:
                        fixed_param_hw['frequency'] = self.SB_F_F.value()
        
        
        
                    