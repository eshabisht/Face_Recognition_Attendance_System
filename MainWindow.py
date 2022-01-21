import sys
from PyQt5.uic import loadUi
#from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow

# from model import Model
from OutputWindow import Ui_OutputWindow

class Ui_MainWindow(QMainWindow):
    
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        loadUi("MainWindow.ui", self)

        self.Start_Button.clicked.connect(self.Start)
        self._new_window = None
        

    @pyqtSlot()
    def Start(self):
        """
        Called when the user presses the Run button
        """
        ui.hide()  # hide the main window
        self.outputWindow_()  # Create and open new output window

    def outputWindow_(self):
        """
        Created new window for vidual output of the video in GUI
        """
        self._new_window = Ui_OutputWindow()
        self._new_window.show()
        self._new_window.startVideo()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())