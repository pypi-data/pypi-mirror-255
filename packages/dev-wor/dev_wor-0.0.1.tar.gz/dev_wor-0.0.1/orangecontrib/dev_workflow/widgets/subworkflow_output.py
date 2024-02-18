#https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import ctypes
import os
import sys
from pathlib import Path

import Orange.data
from Orange.widgets import widget

#from Orange.widgets.dev_workflow import MetManagement
#from Orange.widgets.dev_workflow import shared_variables
#from Orange.widgets.dev_workflow import shared_functions

import MetManagement, shared_functions, shared_variables

from Orange.widgets.utils.signals import Input
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon


class subworkflow_output(widget.OWWidget):
    # This part is executed when Orange is opened, whether the widget is used or not.
    # Useful for tracking or initializing.
    name = "subworkflow_output"
    description = "This is the output of a subworkflow "
    icon = "icons/subworkflow_output.png"
    priority = 10
    # JCM's trick to know the path of the file in which you code (useful for loading images, etc.)
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))
    # There are two areas in the window: control area and main area.
    # I left both for the example, but I prefer to deactivate the control area.
    want_control_area = False
    want_main_area = True
    tab_to_write = ""
    vect_blabla = []

    class Inputs:
        data = Input("Data", Orange.data.Table)  # Input stream named 'data' on the trait in Orange

    @Inputs.data
    def set_data(self, dataset):
        # This method is called when receiving new data.
        # It performs actions such as special processing or writing an output file.
        # Useful for coding/debugging outside Orange.
        if dataset is None:
            self.error("No input data.")
        else:
            self.error("")  # Clear any previous error message
            dataset.save(self.tab_to_write)  # Save the dataset to the specified file
        # Emit a signal indicating that the data has been calculated
        if len(shared_variables.ptr_master_external_orange) == 0:
            return
        if shared_variables.ptr_master_external_orange == "cmd_line":
            return
        # Emit the signal that the data has been calculated
        print("Sending the signal that the data has been calculated.")
        print(shared_variables.ptr_master_external_orange)
        print("######")
        # Check the code for emitting the signal based on your actual implementation.
        if len(shared_variables.ptr_master_external_orange)==0:
            return
        if shared_variables.ptr_master_external_orange=="cmd_line":
            return
        print("----> $$$$$ ---> Sending calculated data")
        #ctypes.cast(int(mes_variables_partagees.ptr_master_external_orange[len(mes_variables_partagees.ptr_master_external_orange)-1]), ctypes.py_object).value.event_data_received()
        print("Done")




    def __init__(self):
        # This part is executed when the widget is created.
        super().__init__()  # Allows interaction with the parent class
        shared_functions.setup_shared_variables(self)
        self.data = None
        self.tab_to_write = MetManagement.current_met_directory(self) + "/output_met.tab"
        uic.loadUi(self.dossier_du_script+'/widget_designer/subworkflow_output_ui.ui', self)
        self.push_button = self.findChild(QtWidgets.QPushButton, 'pushButton_show_hkh_website')
        self.push_button.setIcon(QIcon(self.dossier_du_script+'/icons/Logo_HKH.svg'))
        self.push_button.setIconSize(QSize(65, 65))
        self.push_button.clicked.connect(shared_functions.openlink)

        # self.refresh_label()
        MetManagement.force_save(self)



if __name__ == "__main__":
    # Main block for testing the widget outside Orange.
    shared_variables.current_ows =os.path.dirname(__file__)+"/dataset_devellopper/fakeows.ows"
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    mon_objet = subworkflow_output()
    mon_objet.show()
    # mon_objet.set_data(data)
    mon_objet.handleNewSignals()
    app.exec_()
