#https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import ctypes
import gc
import os
import sys
from pathlib import Path
import Orange.data
import optuna
from Orange.widgets import widget
from PyQt5 import QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from orangewidget.utils.signals import Input, Output
from Orange.data import Table
from Orange.base import Learner, Model
import numpy as np
class ExecuteThread(QThread):
    my_signal = pyqtSignal()

    def __init__(self, target=None, args=()):
        super().__init__()
        self._target = target
        self._args = args

    def emit_signal(self):
        self.my_signal.emit()

    def run(self):
        try:
            self.my_signal.emit()
            if self._target:
                self._target(self._args)
        finally:
            del self._target, self._args
        pass

    def __del__(self):
        print("--------------------> destructor of ExecuteThread")
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
            self.widgets = {}
            chemin_courant = os.path.expanduser("~")
            study_name = 'exemple'
            # Constantes ...
            # Définir le chemin de la base de données dans le dossier actuel
            self.DATABASE_URL = f'sqlite:///{os.path.join(chemin_courant, study_name + ".db")}'
            self.SCORE_FILENAME = 'tableau_score.xlsx'
            liste_domain = []
            liste_data = []
            parameters = None
    @Inputs.MIN
    def set_MIN(self, MIN):
        self.MIN = MIN
        #self.run()

    @Inputs.MAX
    def set_MAX(self, MAX):
        self.MAX = MAX
        #self.run()

    """
       Get a dictionary of widgets with their corresponding captions as keys.
       Returns:
           widgets (dict): A dictionary of widgets with their captions as keys.
       """

    def get_widgets(self):
        # Create an empty dictionary to store the widgets
        # Iterate through all objects in the garbage collector
        self.widgets=None

        return self.widgets

    """
    Set n itération to val after a TPE optimization
    Params:
        - widgetCreateInstance: OWCreateAttributes
        - int: val
    """

    def set_n_iteration(self, widgetCreateInstance, val=0):
        data = widgetCreateInstance.data
        values = widgetCreateInstance._get_values()
        values["n itération"] = val
        widgetCreateInstance.model.removeRows(0, widgetCreateInstance.model.rowCount())
        widgetCreateInstance.model.set_data(data, values)
        widgetCreateInstance.model.dataChanged.connect(widgetCreateInstance._OWCreateInstance__table_data_changed)
        widgetCreateInstance.commit.now()

    """
    Set the create instance for the given widget with the provided data and table reference.

    Args:
        widget: The widget to set the create instance for.
        data: The data to set in the widget model.
        table_creat_ref: The table reference to set in the widget.

    Returns:
        None
    """

    def chiffres_apres_virgule(self, nombre):
        # Convertir le nombre en chaîne de caractères
        chaine = str(nombre)

        # Rechercher l'indice du point décimal
        indice_point = chaine.find('.')

        # Si le point décimal n'est pas trouvé, retourner 0
        if indice_point == -1:
            return 0

        # Retourner le nombre de chiffres après le point décimal
        return len(chaine) - indice_point - 1

    def set_createinstance(self, widget, data, table_creat_ref, study):
        try:
            # Clear the existing rows in the model
            widget.model.removeRows(0, widget.model.rowCount())
            # Set the data in the widget model
            widget.model.set_data(data)
            widget.data = data
            # Set the table reference in the widget
            widget.set_reference(table_creat_ref)
            # Find all the QPushButton children of the widget
            buttons = widget.findChildren(QtWidgets.QPushButton)
            # Loop through each button
            for button in buttons:
                # Click the button if the text is "Input"
                if button.text() == "Input":
                    button.click()
            # Connect the dataChanged signal to the table_data_changed slot
            widget.model.dataChanged.connect(widget._OWCreateInstance__table_data_changed)
            # If auto_commit is False, defer the commit
            if not widget.auto_commit:
                print('je fonctionne en décalé')
                widget.commit.deferred()
            else:
                print('je fonctionne en direct')
                widget.commit.call()

        except AttributeError as e:
            print(f"Erreur d'attribut: {e}")
            # Vous pouvez ajouter d'autres actions appropriées en cas d'erreur ici.
        except Exception as e:
            print(f"Une erreur s'est produite: {e}")
            # Gérer d'autres exceptions spécifiques si nécessaire.

    def convert_data_for_optuna(self, domain, data, minlist, maxlist, listparam, study):
        listname = [(str(domain[i]), listparam[i]) for i in range(len(domain))]
        distributions = {str(domain[i]): optuna.distributions.FloatDistribution(minlist[i], maxlist[i]) for i in
                         range(len(domain))}
        params = {str(domain[i]): data.X[0][i] for i in range(len(data.domain)) if
                  str(data.domain[i]) in (name for name, _ in listname)}
        print(data.Y)
        try:
            scores = data.Y
        except:
            scores = [data.X[0][i] for i in range(len(data.domain)) if
                      "Score" in str(data.domain[i]) or "score" in str(data.domain[i])]
        for name, param_value in listname:
            index = [i for i, var in enumerate(data.domain) if str(var) == name][0]
            print(round(param_value, self.chiffres_apres_virgule(data.X[0][index])), data.X[0][index])
            if round(param_value, self.chiffres_apres_virgule(data.X[0][index])) != data.X[0][index]:
                study.add_trial(
                    optuna.trial.create_trial(
                        params=params,
                        distributions=distributions,
                        values=scores,
                    )
                )
                return "?"

        print("End of the objective_function")
        print(scores)
        return scores

    """
    Load data from a pkl file
    Params:
        - filepath: str
    Returns:
        - Table
    """

    def load_pkl(self, filepath):
        data=None
        return data

    """
    Thread to run TPE optimization
    """

    def detect_change(self):
        timestamp = os.path.getmtime(self.score_filepath)
        while True:
            nouvel_timestamp = os.path.getmtime(self.score_filepath)
            if nouvel_timestamp != timestamp:
                timestamp = nouvel_timestamp
                return True