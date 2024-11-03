from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

from API.d128_controller import D128Controller
import serial
import time
import csv
import datetime
import numpy as np

class Calib_subject_view(QMainWindow):
    def __init__(self, fixed_param_hw, fixed_param_algo, variable_param):
        super(Calib_subject_view,self).__init__()
        loadUi("QtDesigner//gui_calib_subject_win.ui",self)
        #self.setFixedSize(450, 170)

        # Initialize the attribute
        self.setFixedParamHW(fixed_param_hw)
        self.setFixedParamAlgo(fixed_param_algo)
        self.setVariableParam(variable_param)

        print(self.variable_param)
        print(self.fixed_param_hw)
        print(self.fixed_param_algo)

        # Initialize the D128Controller
        self.init_DS8RController()
        # Initialize the uC
        self.init_uC_comm()
        # Set constant parameters
        self.init_DS8R()

        self.create_csv()
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
            'pain': None,
            'accuracy': None
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

    def init_DS8RController(self):
        # Store controller object for DS8R control
        self.controller = D128Controller()
        # Open device and return status
        success, self.d128 = self.controller.D128ctrl('open')
        if success:
            print("Device opened successfully.")
        else:
            print("Failed to open the device.")

    def init_uC_comm(self):
        try:
            # Attempt to open the serial port
            self.uC = serial.Serial('COM5', 115200, timeout=1)  # Replace 'COM3' with your port
            
            # Allow time for the connection to establish
            time.sleep(2)  
            
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
        header = ['#','polarity','mode','source','amplitude[mA]','pulsewidth[us]','interpulse[us]','recovery[%]','frequency[Hz]','stimuDuration[ms]','numTriggers','numRepetition','pain','accuracy']
        with open(self.filename, mode='w', newline='', encoding='utf-8') as datafile:
            writer = csv.writer(datafile)
            writer.writerow(header)
    
    def init_DS8R(self):
        success, d128 = self.controller.D128ctrl('enable', self.d128, False)
        for parameter in self.fixed_param_hw.keys():
            if parameter != 'frequency':
                success, self.d128 = self.controller.D128ctrl(parameter, self.d128, self.fixed_param_hw[parameter])
        if self.variable_param.keys() != 'frequency':
            success, self.d128 = self.controller.D128ctrl(self.variable_param['variable'], self.d128, self.variable_param['min'])
        # Upload all parameters to the device
        success = self.controller.D128ctrl('upload', self.d128)    

    def enable_DS8R(self, state):
        success, d128 = self.controller.D128ctrl('enable', self.d128, state)

# Experiement algorithm
    def experiment(self):
        self.init_fixed_row_items()
        self.var_param_array= self.generate_array(self.variable_param['min'], self.variable_param['max'], self.variable_param['step'])
        self.exp_count = 0
        self.PB_STIMULATE.clicked.connect(self.on_stimulate_clicked)


    def init_fixed_row_items(self):
        for parameter in self.fixed_param_hw.keys():
            self.new_row[parameter] = self.fixed_param_hw[parameter]
        for parameter in self.fixed_param_algo.keys():
            self.new_row[parameter] = self.fixed_param_algo[parameter]

    def generate_array(self, min, max, step):
        self.nb_points = int( ( max - min ) / step + 1) 
        return [min + i * step for i in range(self.nb_points)]

    def on_stimulate_clicked(self):
        self.SB_P.setEnabled(False)
        self.SB_A.setEnabled(False)

        if self.exp_count == self.nb_points:
            self.pain = self.SB_P.value()
            self.accuracy = self.SB_A.value()
            self.append_csv()
            self.close_window()
        elif self.exp_count == 0:
            self.stimulate()
            self.exp_count += 1
        else:
            self.pain = self.SB_P.value()
            self.accuracy = self.SB_A.value()
            self.append_csv()
            
            self.stimulate()
            self.exp_count += 1
            
        self.SB_P.setEnabled(True)
        self.SB_A.setEnabled(True)

    def stimulate(self):
        time.sleep(1.5)
        # Set DS8R fixed parameters
        for parameter in self.fixed_param_hw.keys():
            if parameter != 'frequency':
                success, self.d128 = self.controller.D128ctrl(parameter, self.d128, self.fixed_param_hw[parameter])
            else:
                freq = self.fixed_param_hw[parameter]
        # Set variable parameter
        if self.variable_param.keys() != 'frequency':
            success, self.d128 = self.controller.D128ctrl(self.variable_param['variable'], self.d128, self.var_param_array[self.exp_count])
        else:
            freq = self.var_param_array[self.exp_count]
        # Enable and upload parameters
        success, d128 = self.controller.D128ctrl('enable', self.d128, True)
        success = self.controller.D128ctrl('upload', self.d128)
        time.sleep(1)
        '''
        # Trigger the device
        success = self.controller.D128ctrl('trigger', self.d128)
        '''
        # Trigger
        if self.variable_param.keys() == 'frequency':
            self.uC_trigger(self.var_param_array[self.exp_count])
        else:
            self.uC_trigger(self.fixed_param_hw['frequency'])
        # Wait until stimulation finished
        if self.new_row['stimuDuration[ms]'] != 0 and self.new_row['numTriggers'] == 0:
            time.sleep(self.new_row['stimuDuration[ms]'] + 0.5) 
        elif self.new_row['stimuDuration[ms]'] == 0 and self.new_row['numTriggers'] != 0:
            T = 1 / freq + 1    
            time.sleep(T)
        # Disable for safety & time margin
        time.sleep(0.5)
        success, d128 = self.controller.D128ctrl('enable', self.d128, False)
        success = self.controller.D128ctrl('upload', self.d128)
        

    def uC_trigger(self, freq):
        print('dur ', self.new_row['stimuDuration[ms]'])
        print('num ', self.new_row['numTriggers'])
        if self.new_row['stimuDuration[ms]'] != 0 and self.new_row['numTriggers'] == 0:
            #command = 'trigger' + str(freq) + '\n'
            duration = self.new_row['stimuDuration[ms]']
            command = 'triggerD:' + str(freq) + ':' + str(duration) + '\n'
            print(command)
            self.uC.write(command.encode())
        elif self.new_row['stimuDuration[ms]'] == 0 and self.new_row['numTriggers'] != 0:
            #command = 'trigger' + str(freq) + '\n'
            numTriggers = self.new_row['numTriggers']
            command = 'triggerN:' + str(freq) + ':' + str(numTriggers) + '\n'
            print(command)
            self.uC.write(command.encode())

    def append_csv(self):
        self.new_row['#'] = self.exp_count - 1
        self.new_row[self.variable_param['variable']] = self.var_param_array[self.exp_count - 1]
        self.new_row['pain'] = self.SB_P.value()
        self.new_row['accuracy'] = self.SB_A.value()

        with open(self.filename, mode='a', newline='') as file:
            # Create a DictWriter object
            writer = csv.DictWriter(file, fieldnames = self.new_row.keys())
            
            # Write the header if the file is empty
            if file.tell() == 0:
                writer.writeheader()  # Write the header only if the file is new

            # Write the new row
            writer.writerow(self.new_row)


# Closing communication
    def close_window(self):
        self.close()  # This will close the window

    def close_hw_comm(self):
        if self.uC.is_open:
            self.uC.close()
    
    def closeEvent(self, event):
        self.close_hw_comm()  # Call your function before closing
        event.accept()  # Accept the close event