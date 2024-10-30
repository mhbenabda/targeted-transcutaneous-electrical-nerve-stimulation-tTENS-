import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from API.d128_controller import D128Controller
from mode_mapping import Mapping_view
from mode_calibration import Calib_selector_view
from calib_experiment import Calib_subject_view

class OperationModeWin(QDialog):
    def __init__(self):
        super(OperationModeWin,self).__init__()
        loadUi("QtDesigner//gui_op_mode.ui",self)
        self.setFixedSize(400, 300)
        self.mapping_button.clicked.connect(self.go_mapping_mode)
        self.calib_button.clicked.connect(self.go_calib_mode)

    def go_mapping_mode(self):
        self.mapping_window = Mapping_view()
        self.mapping_window.show()
        self.close()  # Optionally close the dialog

    def go_calib_mode(self):
        
        self.mapping_window = Calib_selector_view()
        self.mapping_window.show()
        self.close()  # Optionally close the dialog
        '''
        self.mapping_window = Calib_subject_view()
        self.mapping_window.show()
        self.close()  # Optionally close the dialog
        '''


if __name__ == '__main__':
    # Start app
    app = QApplication(sys.argv)
    choseMode = OperationModeWin()
    choseMode.show()
    app.exec_()
