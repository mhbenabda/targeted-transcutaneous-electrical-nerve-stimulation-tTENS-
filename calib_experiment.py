# Author: Mohamed Habib Ben Abda
# Date: Fall semester 2024
# Calibration parameters setup window

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.uic import loadUi
import sys
from API.d128_controller import D128Controller
import serial
import time
import csv
import datetime
import numpy as np


class Experiment_view(QMainWindow):
    def __init__(self, fixed_param_hw, fixed_param_algo, variable_param):
        super(Experiment_view,self).__init__()
        loadUi("QtDesigner//gui_experiment_win2.ui",self)
        #self.setFixedSize(450, 170)

        # Initialize the attribute
        self.setFixedParamHW(fixed_param_hw)
        self.setFixedParamAlgo(fixed_param_algo)
        self.setVariableParam(variable_param)
        #print(self.variable_param)
        #print(self.fixed_param_hw)
        #print(self.fixed_param_algo)

        # Set the constant parameters on the DS8R
        self.init_DS8R_values()
        # Initialize serial connection to uC
        self.init_uC_comm()
        # Create csv file with header
        self.create_csv()
        # Setup
        self.setup_comment_section()
        self.new_row = {
            '#': None,
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
            'feelSomething': None,
            'where': None,
            'pain': None,
            'comment': None
        }
        # Start experiment
        self.experiment()
 
 # Initialization
    def setFixedParamHW(self, value):
        self.fixed_param_hw = value

    def setFixedParamAlgo(self, value):
        self.fixed_param_algo = value

    def setVariableParam(self, value):
        self.variable_param = value

    def init_uC_comm(self):
        '''
        Establish serial communication with uC
        '''
        try:
            # Attempt to open the serial port
            self.uC = serial.Serial('COM5', 115200, timeout=1)  # Replace 'COM3' with your port
            
            # Allow time for the connection to establish
            time.sleep(1.5)  
            
            # Check if the port is open
            if self.uC.is_open:
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

        header = ['#','polarity','mode','source','amplitude[mA]','pulsewidth[us]','interpulse[us]','recovery[%]','frequency[Hz]',
                  'stimuDuration[ms]','numTriggers','numRepetition',
                  'feelSomething', 'where', 'pain', 'comment']   # The outputs are at the end of the header
        with open(self.filename, mode='w', newline='', encoding='utf-8') as datafile:
            writer = csv.writer(datafile)
            writer.writerow(header)
    
    def init_DS8R_values(self):
        controller = D128Controller()
        # Open device and return status
        success, d128 = controller.D128ctrl('open')
        if success:
            print("Device opened successfully.")
        else:
            print("Failed to open the device.")

        success, d128 = controller.D128ctrl('enable', d128, False)
        for parameter in self.fixed_param_hw.keys():
            if parameter != 'frequency':
                success, d128 = controller.D128ctrl(parameter, d128, self.fixed_param_hw[parameter])
        if self.variable_param.keys() != 'frequency':
            success, d128 = controller.D128ctrl(self.variable_param['variable'], d128, self.variable_param['min'])
        # Upload all parameters to the device
        success = controller.D128ctrl('upload', d128)   

    def setup_comment_section(self):
        '''
        Stop the user from inputting commas in the comment box
        '''
        regex = QRegExp("[^,]*")  # Any character except @, #, $
        validator = QRegExpValidator(regex)
        self.LineEdit.setValidator(validator)

# Experiement algorithm
    def experiment(self):
        self.set_fixed_row_items()
        self.var_param_array= self.generate_array(self.variable_param['min'], self.variable_param['max'], self.variable_param['step'])
        self.exp_count = 0
        self.CB_1.setEnabled(False)
        self.CB_2.setEnabled(False)
        self.SB_3.setEnabled(False)
        self.L_stimulationON.hide()
        self.L_LED.hide()
        print('waiting for button start')
        print(self.var_param_array)
        self.PB_STIMULATE.clicked.connect(self.on_stimulate_clicked)

    def set_fixed_row_items(self):
        '''
        Fill the row dictionary with the fixed parameters
        '''
        for parameter in self.fixed_param_hw.keys():
            self.new_row[parameter] = self.fixed_param_hw[parameter]
        for parameter in self.fixed_param_algo.keys():
            self.new_row[parameter] = self.fixed_param_algo[parameter]

    def generate_array(self, min, max, step):
        '''
        Generate array with the specified step
        '''
        self.nb_points = int( ( max - min ) / step + 1) 
        print(self.nb_points)
        return [min + i * step for i in range(self.nb_points)]

    def on_stimulate_clicked(self):
        if self.exp_count == 0: # in case it's the first one just stimulate 
            self.runLongTask_stimulation()
        elif self.exp_count == self.nb_points: # I case stimulations done, save the last values and close
            self.append_csv()
            self.close_window()
        else: # save entered value and start next stimulation
            self.append_csv()
            self.runLongTask_stimulation()
            

    def runLongTask_stimulation(self):
        '''
        This will run the long stimulation task on a seperate thread
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
        self.new_row[self.variable_param['variable']] = self.var_param_array[self.exp_count - 1]
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
        Safely close the serial communication channel
        '''
        try:     
            if self.uC.is_open:
                self.uC.close()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
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
        # Delay after the stimulation button pressed
        #time.sleep(1)

        self.controller = D128Controller()
        # Open device and return status
        success, self.d128 = self.controller.D128ctrl('open')
        if success:
            print("DS8R opened successfully.")
        else:
            print("Failed to open the DS8R.")

        # Set fixed parameters each time
        for parameter in self.gui_inst.fixed_param_hw.keys():
            if parameter != 'frequency':
                success, self.d128 = self.controller.D128ctrl(parameter, self.d128, self.gui_inst.fixed_param_hw[parameter])
            else:
                freq = self.gui_inst.fixed_param_hw[parameter]
        # Set variable parameter
        if self.gui_inst.variable_param.keys() != 'frequency':
            success, self.d128 = self.controller.D128ctrl(self.gui_inst.variable_param['variable'], self.d128, self.gui_inst.var_param_array[self.gui_inst.exp_count])
        else:
            freq = self.gui_inst.var_param_array[self.gui_inst.exp_count]
        # Enable and upload parameters
        success, d128 = self.controller.D128ctrl('enable', self.d128, True)
        success = self.controller.D128ctrl('upload', self.d128)
        time.sleep(2)
        success = self.controller.D128ctrl('upload', self.d128)
        time.sleep(1)
        
        # Trigger
        if self.gui_inst.variable_param.keys() == 'frequency':
            self.uC_trigger(self.gui_inst.var_param_array[self.gui_inst.exp_count])
        else:
            self.uC_trigger(self.gui_inst.fixed_param_hw['frequency'])
        
        # Wait until stimulation finished
        if self.gui_inst.new_row['stimuDuration[ms]'] != 0 and self.gui_inst.new_row['numTriggers'] == 0:
            time.sleep(self.gui_inst.new_row['stimuDuration[ms]'] * 10**-3 + 0.5) 
        elif self.gui_inst.new_row['stimuDuration[ms]'] == 0 and self.gui_inst.new_row['numTriggers'] != 0:
            T = 1 / freq + 1    
            time.sleep(T)
        # Disable for safety & time margin
        time.sleep(0.5)
        success, d128 = self.controller.D128ctrl('enable', self.d128, False)
        success = self.controller.D128ctrl('upload', self.d128)

        #success = self.controller.D128ctrl('close', self.d128)

    def uC_trigger(self, freq):
        #print('dur ', self.gui_inst.new_row['stimuDuration[ms]'])
        #print('num ', self.gui_inst.new_row['numTriggers'])
        if self.gui_inst.new_row['stimuDuration[ms]'] != 0 and self.gui_inst.new_row['numTriggers'] == 0:
            duration = self.gui_inst.new_row['stimuDuration[ms]']
            command = 'triggerD:' + str(freq) + ':' + str(duration) + '\n'
            print(command)
            self.gui_inst.uC.write(command.encode())
        elif self.gui_inst.new_row['stimuDuration[ms]'] == 0 and self.gui_inst.new_row['numTriggers'] != 0:
            numTriggers = self.gui_inst.new_row['numTriggers']
            command = 'triggerN:' + str(freq) + ':' + str(numTriggers) + '\n'
            print(command)
            self.gui_inst.uC.write(command.encode())



if __name__ == '__main__':
    # dummy variables
    fixed_param_hw = {
        'polarity': 'Negative', 
        'mode': 'Bi-phasic',
        'source': 'Internal',
        'pulsewidth': 100,
        'dwell': 10,
        'recovery': 100,
        'frequency': 15,
    }
    fixed_param_algo = {
        'stimuDuration[ms]': 2000,
        'numTriggers': 0,
        'numRepetition':1
    } 
    variable_param = {
        'variable': 'demand',
        'min': 6.0,
        'max': 10.0,
        'step': 0.5
    }
    # Start app
    app = QApplication(sys.argv)
    window = Experiment_view(fixed_param_hw, fixed_param_algo, variable_param)
    window.show()
    app.exec_()