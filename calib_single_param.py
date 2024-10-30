from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QButtonGroup
from PyQt5.uic import loadUi
from calib_experiment import Calib_subject_view
import numpy as np

max_PA = 10.0 # [mA] define max amplitude here for safety reasons

class Calib_single_param_view(QMainWindow):
    def __init__(self):
        super(Calib_single_param_view,self).__init__()
        loadUi("QtDesigner//gui_calib_single_param.ui",self)
        self.setFixedSize(800, 550)
        # This variable is for error handeling
        self.error = 0
        # Setting up acceptable parameters
        self.setup_param_ranges()
        # IP spin boxes need special treatement to go always 1-10...
        self.update_SB_F_IP_setup(self.SB_F_IP.value())
        self.update_SB_IP_min_setup(self.SB_IP_min.value())
        self.update_SB_IP_max_setup(self.SB_IP_max.value())
        self.update_SB_IP_step_setup(self.SB_IP_step.value())
        self.SB_F_IP.valueChanged.connect(self.update_SB_F_IP_setup)
        self.SB_IP_min.valueChanged.connect(self.update_SB_IP_min_setup)
        self.SB_IP_max.valueChanged.connect(self.update_SB_IP_max_setup)
        self.SB_IP_step.valueChanged.connect(self.update_SB_IP_step_setup)
        # Only one parameter checkbox checked at a time
        self.param_checkbox_group = QButtonGroup(self)
        self.duration_checkbox_group = QButtonGroup(self)
        self.exclusive_checkboxes()
        # Initialize the paramters
        self.init_param_values()
        
        # Parameters
        self.checked_param = 'C_PA'
        self.len_array_calib_param = 0
        self.num_rep = 0
        self.experiment_pts = np.array([])
        
        # working on this.....
        #self.fixed_param = {}
        #self.variable_param = {}

        # Actions that generate experiement array
        self.param_checkboxes = [self.C_PA, self.C_PW, self.C_IP, self.C_RP, self.C_F]
        self.connect_checkboxes()
        self.connect_spinboxes()

        # Start button clicked -> check parameters are valid -> if yes generate csv and launch experiement , else error messege
        self.PB_START.clicked.connect(self.start_experiment)

    def setup_param_ranges(self):
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

        self.SB_SD.setRange(0, 50000)
        self.SB_SD.setSingleStep(1)

        self.SB_NT.setRange(0, 500000)
        self.SB_NT.setSingleStep(1)

    '''
    Update the singleStep based on the current value of the spin box.
    '''
    def update_SB_F_IP_setup(self, value):
        if (value == 1):
            self.SB_F_IP.setSingleStep(9)
        else:    
            self.SB_F_IP.setSingleStep(10)

    def update_SB_IP_min_setup(self, value):
        if (value == 1):
            self.SB_IP_min.setSingleStep(9)
        else:    
            self.SB_IP_min.setSingleStep(10)

    def update_SB_IP_max_setup(self, value):
        if (value == 1):
            self.SB_IP_max.setSingleStep(9)
        else:    
            self.SB_IP_max.setSingleStep(10)

    def update_SB_IP_step_setup(self, value):
        if (value == 1):
            self.SB_IP_step.setSingleStep(9)
        else:    
            self.SB_IP_step.setSingleStep(10)

    def exclusive_checkboxes(self):
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

        self.SB_NR.setValue(0)
        self.SB_SD.setValue(0)
        self.SB_NT.setValue(0)

        #self.C_PA.setChecked(True)
        #self.C_SD.setChecked(True)

        self.SB_PA_min.setEnabled(False)
        self.SB_PA_max.setEnabled(False)
        self.SB_PA_step.setEnabled(False)

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

    def connect_checkboxes(self):
        for cbox in self.param_checkboxes:
            cbox.stateChanged.connect(self.on_param_cbox_change)

    def connect_spinboxes(self):
        self.SB_PA_min.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_PA_max.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_PA_step.valueChanged.connect(self.SB_update_experiment_points)

        self.SB_PW_min.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_PW_max.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_PW_step.valueChanged.connect(self.SB_update_experiment_points)
        
        self.SB_IP_min.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_IP_max.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_IP_step.valueChanged.connect(self.SB_update_experiment_points)

        self.SB_RP_min.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_RP_max.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_RP_step.valueChanged.connect(self.SB_update_experiment_points)

        self.SB_F_min.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_F_max.valueChanged.connect(self.SB_update_experiment_points)
        self.SB_F_step.valueChanged.connect(self.SB_update_experiment_points)

        self.SB_NR.valueChanged.connect(self.update_L_TM)
        
    def on_param_cbox_change(self):
        sender = self.sender()
        self.change_enable_SB(sender, True)
        if sender.isChecked():
            for cbox in self.param_checkboxes:
                if cbox != sender:
                    cbox.setChecked(False)
                    self.change_enable_SB(cbox, False)

        self.cbox_update_experiment_points(sender.text())

    def change_enable_SB(self, cbox, state):
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
        self.verif_calib_array(cbox)
        if self.error == 0:
            match cbox:
                case 'Pulse Amplitude [mA]':
                    self.generate_array(self.SB_PA_min.value(), self.SB_PA_max.value(), self.SB_PA_step.value())
                    self.update_L_TM()
                case 'Pulse Width [us]':
                    self.generate_array(self.SB_PW_min.value(), self.SB_PW_max.value(), self.SB_PW_step.value())
                    self.update_L_TM()
                case 'Interpulse [us]':
                    self.generate_array(self.SB_IP_min.value(), self.SB_IP_max.value(), self.SB_IP_step.value())
                    self.update_L_TM()
                case 'Recovery Phase [%]':
                    self.generate_array(self.SB_RP_min.value(), self.SB_RP_max.value(), self.SB_RP_step.value())
                    self.update_L_TM()
                case 'Frequency [Hz]':
                    self.generate_array(self.SB_F_min.value(), self.SB_F_max.value(), self.SB_F_step.value())
                    self.update_L_TM()

    def SB_update_experiment_points(self):
        sender = self.sender()
        if sender in [self.SB_PA_min, self.SB_PA_max, self.SB_PA_step]:
            self.verif_min_max(self.SB_PA_min.value(), self.SB_PA_max.value())
            if self.error == 0:
                self.generate_array(self.SB_PA_min.value(), self.SB_PA_max.value(), self.SB_PA_step.value())
                self.update_L_TM()
        elif sender in [self.SB_PW_min, self.SB_PW_max, self.SB_PW_step]:
            self.verif_min_max(self.SB_PA_min.value(), self.SB_PA_max.value())
            if self.error == 0:
                self.generate_array(self.SB_PW_min.value(), self.SB_PW_max.value(), self.SB_PW_step.value())
                self.update_L_TM()
        elif sender in [self.SB_IP_min, self.SB_IP_max, self.SB_IP_step]:
            self.verif_min_max(self.SB_IP_min.value(), self.SB_IP_max.value())
            if self.error == 0:
                self.generate_array(self.SB_IP_min.value(), self.SB_IP_max.value(), self.SB_IP_step.value())
                self.update_L_TM()
        elif sender in [self.SB_RP_min, self.SB_RP_max, self.SB_RP_step]:
            self.verif_min_max(self.SB_RP_min.value(), self.SB_RP_max.value())
            if self.error == 0:
                self.generate_array(self.SB_RP_min.value(), self.SB_RP_max.value(), self.SB_RP_step.value())
                self.update_L_TM()
        elif sender in [self.SB_F_min, self.SB_F_max, self.SB_F_step]:
            self.verif_min_max(self.SB_F_min.value(), self.SB_F_max.value())
            if self.error == 0:
                self.generate_array(self.SB_F_min.value(), self.SB_F_max.value(), self.SB_F_step.value())
                self.update_L_TM()

    def generate_array(self, min, max, step):
        nb_points = int( ( max - min ) / step )
        self.experiment_pts = np.linspace(min, max, nb_points)
        self.len_array_calib_param = len(self.experiment_pts)

    def update_L_TM(self):
        self.num_rep = self.len_array_calib_param * self.SB_NR.value()
        self.L_TM.setText('Total number of measurements: {}'.format(self.num_rep))

    def start_experiment(self):
        self.error = 0
        param_cbox_checked = False
        for cbox in self.param_checkboxes:
            if cbox.isChecked():
                param_cbox_checked = True
                self.verif_calib_array(cbox.text())
                # define the variable parameter
                self.variable_param = cbox
        if not(param_cbox_checked):
            self.error = 1
        time_cbox_checked = False
        for cbox in [self.C_SD, self.C_NT]:
            if cbox.isChecked():
                time_cbox_checked = True
                if cbox == self.C_SD:
                    if self.SB_SD.value() == 0:
                        self.error = 3 
                elif cbox == self.C_NT:
                    if self.SB_NT.value() == 0:
                        self.error = 4 
        if not(time_cbox_checked):
            self.error = 2
        self.verif_trigger_freq()

        if self.error == 0:
            self.update_error_msg()
            print('Success')
            
            fixed_param_hw = {}
            fixed_param_algo = {}
            variable_param = {}
            self.format_param(fixed_param_hw, fixed_param_algo, variable_param)

            self.experiment_window = Calib_subject_view(fixed_param_hw, fixed_param_algo, variable_param)
            
            
            self.experiment_window.show()
            self.close()  # Optionally close the dialog
            
        else:
            self.update_error_msg()
        
        
    def verif_calib_array(self, cbox):
        match cbox:
            case 'Pulse Amplitude [mA]':
                if self.SB_PA_max.value() < self.SB_PA_min.value():
                    self.error = 11
            case 'Pulse Width [us]':
                if self.SB_PW_max.value() < self.SB_PW_min.value():
                    self.error = 11
            case 'Interpulse [us]':
                if self.SB_IP_max.value() < self.SB_IP_min.value():
                    self.error = 11
            case 'Recovery Phase [%]':
                if self.SB_RP_max.value() < self.SB_RP_min.value():
                    self.error = 11
            case 'Frequency [Hz]':
                if self.SB_F_max.value() < self.SB_F_min.value():
                    self.error = 11

    def verif_min_max(self, min, max):
        if max < min:
            self.error = 11

    def calc_max_one_stimuli_duration(self):
        if self.C_PW.isChecked():
            maxPW = self.SB_PW_max.value()
        else:
            maxPW = self.SB_F_PW.value()
        if self.C_IP.isChecked():
            maxIP = self.SB_IP_max.value()
        else:
            maxIP = self.SB_F_IP.value()
        if self.C_RP.isChecked():
            maxRP = self.SB_RP_max.value()
        else:
            maxRP = self.SB_F_RP.value()

        self.max_one_stimuli_time = ( maxPW + maxIP + maxPW * maxRP * 0.01 ) * 10**-6

    def verif_trigger_freq(self):
        self.calc_max_one_stimuli_duration()
        if self.C_F.isChecked():
            T = 1 / self.SB_F_max.value()
        else:
            T = 1 / self.SB_F_F.value()
        if T < self.max_one_stimuli_time:
            self.error = 5

    def update_error_msg(self):
        if self.error == 1:
            self.L_ERROR.setText('<b>Error: No variable checked</b>')
        elif self.error == 2:
            self.L_ERROR.setText('<b>Error: Please choose stimulation duration or number of triggers</b>')
        elif self.error == 11:
            self.L_ERROR.setText('<b>Error: min value must be smaller than max value</b>')
        elif self.error == 3:
            self.L_ERROR.setText('<b>Error: Stimulation duration must be > 0</b>')
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
        
        
        
                    