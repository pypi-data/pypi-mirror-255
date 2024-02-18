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
class Exctract_domain(widget.OWWidget):

    name = "Extract Domain"
    description = "Extract the domain form a model"
    #category =
    icon = "icons/extract.png"
    priority = 3150
    keywords = "program, function"

    class Inputs:
        data = Input("Data", Table, replaces=["in_data"], default=True)
        learner = Input("Learner", Learner, replaces=["in_learner"], default=True)
        classifier = Input("Classifier", Model, replaces=["in_classifier"], default=True)
        object = Input("Object", object, replaces=["in_object"], default=False, auto_summary=False)

    class Outputs:
        data_from_data = Output("Domain from Data", Table, replaces=["data_from_data"])
        data_from_learner = Output("Domain from Learner", Table, replaces=["data_from_learner"])
        data_from_classifier = Output("Domain from Classifier", Table, replaces=["data_from_classifier"])
        data_from_object = Output("Domain from Object", Table, replaces=["data_from_object"])

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
            self.data = None
            self.learner = None
            self.classifier = None
            self.object = None
    @Inputs.data
    def set_data(self, data):
        self.data = data
        self.run()

    @Inputs.learner
    def set_learner(self, learner):
        self.learner = learner
        self.run()
    @Inputs.classifier
    def set_classifier(self, classifier):
        self.classifier = classifier
        self.run()
    @Inputs.object
    def set_object(self, object):
        self.object = object
        self.run()

    def run(self):
        """
        Process the data, learner, classifier, and object if they are not None.
        """

        # Process the data if it is not None
        if self.data is not None:
            self.process(self.data, 'data_from_data')

        # Process the learner if it is not None
        if self.learner is not None:
            self.process(self.learner, 'data_from_learner')

        # Process the classifier if it is not None
        if self.classifier is not None:
            self.process(self.classifier, 'data_from_classifier')

        # Process the object if it is not None
        if self.object is not None:
            self.process(self.object, 'data_from_object')

    def process(self, data_to_process, output_name):
        """
        Process the data and send it to the appropriate output channel.

        Args:
            data_to_process: The data to be processed.
            output_name: The name of the output channel.

        Returns:
            None
        """
        # Initialize variables
        out_data = None

        try:
            # Get the original domain from the data
            out_domain = data_to_process.original_domain
            liste_de_zeros = [[0]*len(out_domain)]
            # Convert the domain to a table
            out_data = Table.from_list(out_domain, liste_de_zeros)
        except:
            # Print an error message if the domain is not available
            print("No domain")

        # Send the data to the appropriate output channel based on the output name
        if output_name == 'data_from_data':
            self.Outputs.data_from_data.send(out_data)
        if output_name == 'data_from_learner':
            self.Outputs.data_from_learner.send(out_data)
        if output_name == 'data_from_classifier':
            self.Outputs.data_from_classifier.send(out_data)
        if output_name == 'data_from_object':
            self.Outputs.data_from_object.send(out_data)