# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# Calibration parameters setup window

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.uic import loadUi
import sys
from API.ds8r_controller import DS8RController
from API.d188_controller import D188Controller
import serial
import time
import csv
import datetime

'''
The hardware instances are created globally because they need to be accessed by multiple classes in multiple threads.
This was the best method found so that all hw communications are running correctly. 
No locks or synchronization mechanisms are required for this specific usage
'''
stimulator = DS8RController()
selector = D188Controller()
uC = None # Will take serial instance

class Experiment_view(QMainWindow):
    '''
    Experiment GUI and functions
    '''
    def __init__(self, fixed_param_hw, algo_settings, variable_param, subject_info):
        super(Experiment_view,self).__init__()

        # Initialize the attribute
        self.setFixedParamHW(fixed_param_hw)
        self.setAlgoSettings(algo_settings)
        self.setVariableParam(variable_param)
        self.setSubjectInfo(subject_info)
        
        self.new_row = {
            '#': None,
            'subject_reference': None, # to be replaced by an anonynous reference
            'gender': None,
            'age': None,
            'hand_side': None,
            'polarity': None,
            'mode': None,
            'source': None,
            'demand': None,
            'pulsewidth': None,
            'dwell': None,
            'recovery': None,
            'frequency': None,
            'stimuDuration[ms]': None,
            'numTriggers': None,
            'numRepetition': None,
            'currentChannel': None, 
            'nbInversionPoints': None,
            'feelSomething': None,
            'where': None,
            'pain': None,
            'comment': None
        }

        self.init_DS8R_values()     # Set the constant parameters on the DS8R
        self.init_selector()
        self.init_uC_comm()         # Initialize serial connection to uC
        self.create_csv()           # Create csv file with header

        # Launch GUI
        loadUi("QtDesigner//gui_experiment_win2.ui",self)    
        self.setup_comment_section()
        #self.setFixedSize(450, 170)

        # Start experiment
        self.experiment()
 
 # Initialization
    def setFixedParamHW(self, value):
        self.fixed_param_hw = value

    def setAlgoSettings(self, value):
        self.algo_settings = value

    def setVariableParam(self, value):
        self.variable_param = value
    
    def setSubjectInfo(self, value):
        self.subject_info = value

    def init_uC_comm(self):
        '''
        Establish serial communication with uC
        '''
        try:
            # Attempt to open the serial port
            global uC
            uC = serial.Serial('COM5', 115200, timeout=1)  # Replace 'COM3' with your port
            
            # Allow time for the connection to establish
            time.sleep(1.5)  
            
            # Check if the port is open
            if uC.is_open:
                print("Serial port opened successfully.")
            else:
                print("Failed to open the serial port.")
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def create_csv(self):
        '''
        Create csv file with the propper title and header
        title format: date_time_NameOfVariableParameter
        '''
        # Create file name
        match self.variable_param['variable']:
            case 'demand':
                variable_param_s = 'PA_variable'
            case 'pulsewidth':
                variable_param_s = 'PW_variable'
            case 'dwell':
                variable_param_s = 'IP_variable'
            case 'recovery':
                variable_param_s = 'RP_variable'
            case 'frequency':
                variable_param_s = 'F_variable'
        now = datetime.datetime.now()
        timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
        self.filename = 'recorded_data\\' + timestamp + '_' + variable_param_s + '.csv'

        #header = ['#','subject_reference','gender','age','hand_side',
        #          'polarity','mode','source','amplitude[mA]','pulsewidth[us]','interpulse[us]','recovery[%]','frequency[Hz]',
        #          'stimuDuration[ms]','numTriggers','numRepetition',
        #          'currentChannel','nbInversionPoints',
        #          'feelSomething', 'where', 'pain', 'comment']   # The outputs are at the end of the header
        header = list(self.new_row.keys())
        # Create file with proper name and header
        with open(self.filename, mode='w', newline='', encoding='utf-8') as datafile:
            writer = csv.writer(datafile)
            writer.writerow(header)
    
    def init_DS8R_values(self):
        '''
        Set the fixed parameters on the DS8R
        '''
        stimulator.Load()
        stimulator.Initialize()
        time.sleep(0.1)

        stimulator.Enable(False)
        time.sleep(0.1)
        for parameter in self.fixed_param_hw.keys():
            if parameter != 'frequency':
                stimulator.Cmd(parameter, self.fixed_param_hw[parameter])
                time.sleep(0.1)
        if self.variable_param.keys() != 'frequency':
            stimulator.Cmd(self.variable_param['variable'], self.variable_param['start'])
            time.sleep(0.1)

        stimulator.Close()  
        time.sleep(0.1)

    def init_selector(self):
        selector.Load()
        selector.Initialize()
        time.sleep(0.1)
        selector.SetMode('USB')
        time.sleep(0.1)
        selector.SetIndicator('ON')
        time.sleep(0.1)
        selector.SetDelay(1) # 1ms (can go up to 0.1ms but don't need to here)
        time.sleep(0.1)
        selector.SetChannel(8)
        time.sleep(0.1)
        selector.Close()
        time.sleep(0.1)

    def setup_comment_section(self):
        '''
        Stop the user from inputting commas in the comment box. 
        This is because commas are used to seperate colomuns in the csv file
        '''
        regex = QRegExp("[^,]*")  # Any character except @, #, $
        validator = QRegExpValidator(regex)
        self.LineEdit.setValidator(validator)

# Experiement algorithm
    def experiment(self):
        '''
        This function contains the high level steps of the experiment
        on both the GUI and the algorithm side
        '''
        self.set_fixed_row_items()
        self.CB_1.setEnabled(False)
        self.CB_2.setEnabled(False)
        self.SB_3.setEnabled(False)
        self.L_stimulationON.hide()
        self.L_LED.hide()
        
        self.total_channels = len(self.algo_settings['channels'])
        self.channel_idx = 0
        selector.Initialize()
        time.sleep(0.1)
        selector.SetChannel(self.algo_settings['channels'][self.channel_idx])   # Turn on fist channel in the list
        time.sleep(0.1)
        selector.Close()
        time.sleep(0.1)
        self.min_list = []
        self.exp_count = 0
        

        self.PB_STIMULATE.clicked.connect(self.min_threshold_detection)

    def set_fixed_row_items(self):
        '''
        Fill the new_row dictionary with the fixed parameters that will not change during the experiment
        '''
        for parameter in self.subject_info.keys():
            self.new_row[parameter] = self.subject_info[parameter]
        for parameter in self.fixed_param_hw.keys():
            self.new_row[parameter] = self.fixed_param_hw[parameter]
        for parameter in self.algo_settings.keys():
            if parameter != 'channels':
                self.new_row[parameter] = self.algo_settings[parameter]

    def min_threshold_detection(self):
        '''
        Finite State Machine to find the minimum detection threshold
        This function dynamically decides on the next stimulation point
        It cahnges the value of "self.stimuli" that will be used in "runLongTask_stimulation()"
        '''
        if self.exp_count == 0:
            self.count_inv_points = 0
            self.list_inv_points = []
            self.stimuli =  self.variable_param['start'] # {variable, value}
            # run stimulation
            self.runLongTask_stimulation()

        elif self.exp_count == 1: 
            self.append_csv()
            # During each button press read feedback from stimulation  t-1
            self.feelSomething_1 = self.CB_1.currentText() 
            self.where_1 = self.CB_2.currentText()
            self.pain_1 = self.SB_3.value()
            self.stimuli = self.stimuli +  self.variable_param['step'] # Increment
            # run stimulation
            self.runLongTask_stimulation()

        else:
            self.append_csv()
            if self.count_inv_points == algo_settings['nbInversionPoints']:
                print(self.list_inv_points)
                self.min_list.append(self.calculate_avg(self.list_inv_points)) # Calculate min poin for this channel
                print(self.min_list)
                if self.channel_idx + 1 < self.total_channels:
                    self.channel_idx += 1
                    selector.Initialize()
                    time.sleep(0.1)
                    selector.SetChannel(self.algo_settings['channels'][self.channel_idx])
                    time.sleep(0.1)
                    selector.Close()
                    time.sleep(0.1)

                    self.exp_count = 0
                    self.count_inv_points = 0
                    self.list_inv_points = []
                    self.stimuli =  self.variable_param['start']
                else:
                    self.close_window()
            else:
                # Save stimulation feedback from t-2 
                self.feelSomething_2 = self.feelSomething_1 
                self.where_2 = self.where_1
                # Read stimulation of t-1
                self.feelSomething_1 = self.CB_1.currentText() 
                self.where_1 = self.CB_2.currentText()
                self.pain_1 = self.SB_3.value()
                # Decide on next stimulation
                if self.feelSomething_1 == 'Yes' and self.where_1 == 'Referred area':
                    if self.feelSomething_2 == 'No' or (self.feelSomething_2 == 'Yes' and (self.where_2 == 'Near electrodes' or self.where_2 == 'Both')):
                        self.count_inv_points += 1
                        self.list_inv_points.append(self.stimuli)
                        self.stimuli = self.stimuli -  self.variable_param['step']  # Decrement
                    else:
                        self.stimuli = self.stimuli -  self.variable_param['step']  # Decrement
                else:
                    self.stimuli = self.stimuli +  self.variable_param['step']      # Increment
            
            if self.stimuli > self.variable_param['stop']:
                print('Stopped because cannot go beyond maximum threshold')
                self.close_window()
            # run stimulation
            self.runLongTask_stimulation()
    
    def calculate_avg(self, list_points):
        return sum(list_points) / len(list_points)     
 
            
    def runLongTask_stimulation(self):
        '''
        The stimulation task can take a relatively long time to execute with all the delays, hw communications,...
        This is why it must run in a parallel thread so that the GUI doesn't freeze
        '''
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(self)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()

        # Disable buttons then enable them again when finished
        self.PB_STIMULATE.setEnabled(False)        
        self.CB_1.setEnabled(False)
        self.CB_2.setEnabled(False)
        self.SB_3.setEnabled(False)
        self.L_stimulationON.show()
        self.L_LED.show()
        self.thread.finished.connect(
            lambda: self.PB_STIMULATE.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.CB_1.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.CB_2.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.SB_3.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.L_stimulationON.hide() 
            )
        self.thread.finished.connect(
            lambda: self.L_LED.hide() 
            )
        self.thread.finished.connect(
            lambda: self.increment_counter()
            )

    def increment_counter(self):
        self.exp_count += 1

    def append_csv(self):
        '''
        Adds one row of values to csv
        '''
        self.new_row['#'] = self.exp_count - 1
        self.new_row[self.variable_param['variable']] = self.stimuli
        self.new_row['currentChannel'] = self.algo_settings['channels'][self.channel_idx]
        self.new_row['feelSomething'] = self.CB_1.currentText()
        self.new_row['where'] = self.CB_2.currentText()
        self.new_row['pain'] = self.SB_3.value()
        if self.LineEdit.text().strip() == "":
            self.new_row['comment'] = 'None'
        else:
            self.new_row['comment'] = self.LineEdit.text()
        self.LineEdit.clear()
        print(self.new_row)
        with open(self.filename, mode='a', newline='') as file:
            # Create a DictWriter object
            writer = csv.DictWriter(file, fieldnames = self.new_row.keys())
            # Write the header if the file is empty
            if file.tell() == 0:
                writer.writeheader()  # Write the header only if the file is new
            # Write the new row
            writer.writerow(self.new_row)


# Closing event
    def close_window(self):
        self.close_hw_comm()  
        self.close()  # This will close the window

    def close_hw_comm(self):
        '''
        Safely close the serial communication channel, the communiaction with the DS8R and the D188
        '''
        try:     
            if uC.is_open:
                uC.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        stimulator.Close()
        time.sleep(0.1)
        stimulator.Unload()
        selector.Close()
        time.sleep(0.1)
        selector.Unload()
    
    def closeEvent(self, event):
        self.close_hw_comm()  
        event.accept()  # Accept the close event


class Worker(QObject):
    '''
    The stimulation is a long running task and thus needs to be executed in a seperate
    thread so that the GUI doesn't freeze. 
    This work class contains the long stimulation function
    '''
    # Signals for finished and error handling
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, gui_inst):
        super().__init__()
        self.gui_inst = gui_inst
           
    def run(self):
        try:
            self.long_stimulate()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
    
    def long_stimulate(self):
        stimulator.Initialize()
        time.sleep(0.1)

        # Set fixed parameters each time
        if 'frequency' in self.gui_inst.fixed_param_hw.keys():
            freq = self.gui_inst.fixed_param_hw['frequency']
        
        # Set variable parameter
        if self.gui_inst.variable_param.keys() != 'frequency':
            stimulator.Cmd(self.gui_inst.variable_param['variable'], self.gui_inst.stimuli)
            time.sleep(0.1)
        else:
            freq = self.gui_inst.stimuli
        # Enable and upload parameters
        stimulator.Enable(True)
        time.sleep(0.1)
        
        # Trigger as specified 
        self.uC_trigger(freq)
        
        # Wait until stimulation finished
        if self.gui_inst.new_row['stimuDuration[ms]'] != 0 and self.gui_inst.new_row['numTriggers'] == 0:
            time.sleep(self.gui_inst.new_row['stimuDuration[ms]'] * 10**-3 + 0.5) 
        elif self.gui_inst.new_row['stimuDuration[ms]'] == 0 and self.gui_inst.new_row['numTriggers'] != 0:
            T = 1 / freq + 1    
            time.sleep(T)
        # Disable for safety & time margin
        time.sleep(0.5)
        stimulator.Enable(False)
        time.sleep(0.1)

        stimulator.Close()
        time.sleep(0.1)

    def uC_trigger(self, freq):
        if self.gui_inst.new_row['stimuDuration[ms]'] != 0 and self.gui_inst.new_row['numTriggers'] == 0:
            duration = self.gui_inst.new_row['stimuDuration[ms]']
            command = 'triggerD:' + str(freq) + ':' + str(duration) + '\n'
            print(command)
            #self.gui_inst.uC.write(command.encode())
            uC.write(command.encode())
        elif self.gui_inst.new_row['stimuDuration[ms]'] == 0 and self.gui_inst.new_row['numTriggers'] != 0:
            numTriggers = self.gui_inst.new_row['numTriggers']
            command = 'triggerN:' + str(freq) + ':' + str(numTriggers) + '\n'
            print(command)
            uC.write(command.encode())



if __name__ == '__main__':
    '''
    
    Notes:
    - Must start from a variable value ('start' key) that the subject doesn't feel
    '''
    # dummy variables
    subject_info = {
        'subject_reference': 'Habib', # to be replaced by an anonynous reference
        'gender': 'Male',
        'age': 24,
        'hand_side': 'left'
    }
    fixed_param = {
        'polarity': 'Negative', 
        'mode': 'Bi-phasic',
        'source': 'Internal',
        'pulsewidth': 50,
        'dwell': 10,
        'recovery': 100,
        'frequency': 15,
    }
    algo_settings = {
        'stimuDuration[ms]': 1000,
        'numTriggers': 0,
        'numRepetition':None,
        'channels': [1,2,3], # set connected channels
        'nbInversionPoints': 5
    } 
    variable_param = {
        'variable': 'demand',
        'start': 6.0,
        'stop': 20.0,
        'step': 0.5
    }
    # Start app
    app = QApplication(sys.argv)
    window = Experiment_view(fixed_param, algo_settings, variable_param, subject_info)
    window.show()
    app.exec_()