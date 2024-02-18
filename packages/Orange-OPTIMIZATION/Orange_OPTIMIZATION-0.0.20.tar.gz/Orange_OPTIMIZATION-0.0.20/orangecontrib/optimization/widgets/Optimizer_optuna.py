#https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import ctypes
import os
import sys
from pathlib import Path
import Orange.data
from Orange.widgets import widget
from PyQt5 import QtGui, QtWidgets
from PyQt5 import uic
from orangewidget.utils.signals import Input, Output
from Orange.data import Table
from Orange.base import Learner, Model
import numpy as np

class OPTIMIZER(widget.OWWidget):

    name = "Optimizer"
    description = "Optimizer Problems"
    #category =
    #category =
    icon = None
    priority = 3150
    keywords = "program, function"

    class Inputs:
        MIN = Input("MIN", Table, replaces=["MIN"], default=True)
        MAX = Input("MAX", Learner, replaces=["MAX"], default=True)

    class Outputs:
        data_from_data = Output("Domain from Data", Table, replaces=["data_from_data"])
    def __init__(self):
            """
            Initialize the class.
            """
            super().__init__()

            # Set the path to the UI file
            uic_path = os.path.join(os.path.dirname(__file__), 'widget_designer', 'Extract_domain.ui')

            # Load the UI file
            uic.loadUi(uic_path, self)

            # Initialize data, learner, classifier, and object variables
            self.MAX = None
            self.MIN = None

    @Inputs.MIN
    def set_MIN(self, MIN):
        self.MIN = MIN
        #self.run()

    @Inputs.MAX
    def set_MAX(self, MAX):
        self.MAX = MAX
        #self.run()


    # def run(self):
    #     """
    #     Process the data, learner, classifier, and object if they are not None.
    #     """
    #
    #     # Process the data if it is not None
    #     if self.data is not None:
    #         self.process(self.data, 'data_from_data')
    #
    #     # Process the learner if it is not None
    #     if self.learner is not None:
    #         self.process(self.learner, 'data_from_learner')
    #
    #     # Process the classifier if it is not None
    #     if self.classifier is not None:
    #         self.process(self.classifier, 'data_from_classifier')
    #
    #     # Process the object if it is not None
    #     if self.object is not None:
    #         self.process(self.object, 'data_from_object')
    #
    # def process(self, data_to_process, output_name):
    #     """
    #     Process the data and send it to the appropriate output channel.
    #
    #     Args:
    #         data_to_process: The data to be processed.
    #         output_name: The name of the output channel.
    #
    #     Returns:
    #         None
    #     """
    #     # Initialize variables
    #     out_data = None
    #
    #     try:
    #         # Get the original domain from the data
    #         try:
    #             out_domain = data_to_process.original_domain
    #         except:
    #             out_domain = data_to_process.domain
    #         liste_de_zeros = [[0]*len(out_domain)]
    #         # Convert the domain to a table
    #         out_data = Table.from_list(out_domain, liste_de_zeros)
    #     except:
    #         # Print an error message if the domain is not available
    #         print("No domain")
    #
    #     # Send the data to the appropriate output channel based on the output name
    #     if output_name == 'data_from_data':
    #         self.Outputs.data_from_data.send(out_data)
    #     if output_name == 'data_from_learner':
    #         self.Outputs.data_from_learner.send(out_data)
    #     if output_name == 'data_from_classifier':
    #         self.Outputs.data_from_classifier.send(out_data)
    #     if output_name == 'data_from_object':
    #         self.Outputs.data_from_object.send(out_data)