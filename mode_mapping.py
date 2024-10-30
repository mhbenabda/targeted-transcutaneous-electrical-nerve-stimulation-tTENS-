from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from PyQt5.uic import loadUi
from API.d128_controller import D128Controller
import serial
import time

class Mapping_view(QMainWindow):
    def __init__(self):
        super(Mapping_view,self).__init__()
        loadUi("QtDesigner//gui_mapping.ui",self)
        # Setting up acceptable parameters
        self.setup_param_ranges()
        self.update_SB_IP_setup(self.SB_IP.value())
        self.SB_IP.valueChanged.connect(self.update_SB_IP_setup)
        # Initialize the D128Controller
        self.init_DS8RController()
        # Initialize the uC
        self.init_uC_comm()
        # Initialize the paramters
        self.init_param_values()
        self.update_DS8R()
        # Initialise the trigger value
        self.trigger = False

        self.PB_UPDATE.clicked.connect(self.update_DS8R)
        self.PB_START_STOP.clicked.connect(self.start_stop)

        

    def setup_param_ranges(self):
        self.SB_PA.setRange(0.0, 50.0) # Stop user from intering dangerous current amplitude here
        self.SB_PA.setDecimals(1)
        self.SB_PA.setSingleStep(0.1)
        
        self.SB_PW.setRange(50, 2000)
        self.SB_PW.setSingleStep(10)
        
        self.SB_IP.setRange(1, 990)
        
        self.SB_RP.setRange(10, 100)
        self.SB_RP.setSingleStep(1)

        self.SB_F.setRange(0, 1000)
        self.SB_F.setSingleStep(1)
    
    '''
    Update the singleStep based on the current value of the spin box.
    '''
    def update_SB_IP_setup(self, value):
        if (value == 1):
            self.SB_IP.setSingleStep(9)
        else:    
            self.SB_IP.setSingleStep(10)

    def init_param_values(self):
        self.CB_M.setCurrentIndex(1)
        self.CB_POL.setCurrentIndex(0)
        self.CB_S.setCurrentIndex(0)
        self.SB_PA.setValue(1)
        self.SB_PW.setValue(1000)
        self.SB_IP.setValue(1)
        self.SB_RP.setValue(100)
        self.SB_F.setValue(1)

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
        
    def update_DS8R(self):
        success, self.d128 = self.controller.D128ctrl('mode', self.d128, self.CB_M.currentText())
        success, self.d128 = self.controller.D128ctrl('polarity', self.d128, self.CB_POL.currentText())
        success, self.d128 = self.controller.D128ctrl('source', self.d128, self.CB_S.currentText())
        success, self.d128 = self.controller.D128ctrl('demand', self.d128, self.SB_PA.value())
        success, self.d128 = self.controller.D128ctrl('pulsewidth', self.d128, self.SB_PW.value())
        success, self.d128 = self.controller.D128ctrl('dwell', self.d128, self.SB_IP.value())
        success, self.d128 = self.controller.D128ctrl('recovery', self.d128, self.SB_RP.value())
        # Upload all parameters to the device
        success = self.controller.D128ctrl('upload', self.d128)

    def start_stop(self):
        freq = self.SB_F.value()
        if self.trigger == False:
            # Enable the device
            success, self.d128 = self.controller.D128ctrl('enable', self.d128, True)
            # Upload all parameters to the device
            success = self.controller.D128ctrl('upload', self.d128)
            command = 'start' + str(freq) + '\n'
            self.uC.write(command.encode())
            self.trigger = True
        else:
            command = 'stop\n'
            self.uC.write(command.encode())
            # disable the device
            success, self.d128 = self.controller.D128ctrl('enable', self.d128, False)
            # Upload all parameters to the device
            success = self.controller.D128ctrl('upload', self.d128)
            self.trigger = False

    def close_uC_comm(self):
        if self.trigger == True:
            command = 'stop\n'
            self.uC.write(command.encode())
            # disable the device
            success, self.d128 = self.controller.D128ctrl('enable', self.d128, False)
            # Upload all parameters to the device
            success = self.controller.D128ctrl('upload', self.d128)
            self.trigger = False
        if self.uC.is_open:
            self.uC.close()
    
    def closeEvent(self, event):
        self.close_uC_comm()  # Call your function before closing
        event.accept()  # Accept the close event