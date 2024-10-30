from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from calib_single_param import Calib_single_param_view

class Calib_selector_view(QMainWindow):
    def __init__(self):
        super(Calib_selector_view,self).__init__()
        loadUi("QtDesigner//gui_calib_selector.ui",self)
        self.setFixedSize(400, 300)
        self.calib_mode1_button.clicked.connect(self.go_single_param_calib)
        # tbc other modes...

    def go_single_param_calib(self):
        self.calib_single_param_window = Calib_single_param_view()
        self.calib_single_param_window.show()
        self.close()  