from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets
from Orange.widgets.data.owfile import OWFile
from Orange.widgets.data.owpythonscript import OWPythonScript, Script
from Orange.widgets.data.owselectcolumns import OWSelectAttributes
from Orange.widgets.data.owcreateinstance import OWCreateInstance
from Orange.widgets.data.owconcatenate import OWConcatenate
from Orange.widgets.data.owsave import OWSave
from Orange.widgets.widget import Output
from orangecontrib.educational.widgets.owrandomdata import OWRandomData
from Orange.data import Table, ContinuousVariable, DiscreteVariable, Domain
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
from sqlalchemy import create_engine, inspect as sql_inspect
import Orange.data
import optuna
import pathlib
import time
import copy
import gc
import os
import re
import inspect
import pandas as pd
import numpy as np
from pprint import pprint
from optuna.storages import RDBStorage
class Optimizer(widget.OWWidget):
    name = "Optimizer"
    description = "Optimize a problem"
    # category =
    icon = "icons/extract.png"
    priority = 3150
    keywords = "optimizer"

    class Inputs:
        Min = Input("Min_Table", Table, replaces=["Min_Table"], default=True)
        Max = Input("Max_Table", Table, replaces=["Max_Table"], default=True)

    class Outputs:
        Out_table = Output("Result_Table", Table, replaces=["Result_Table"])

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
        self.Min = None
        self.Max = None
        self.domain = None
        self.widgets={}
        chemin_courant = os.path.expanduser("~")
        study_name = 'exemple'
        # Constantes ...
        # Définir le chemin de la base de données dans le dossier actuel
        self.DATABASE_URL = f'sqlite:///{os.path.join(chemin_courant, study_name + ".db")}'
        self.SCORE_FILENAME = 'tableau_score.xlsx'
        liste_domain = []
        liste_data = []
        parameters = None

    @Inputs.Min
    def set_data(self, data):
        self.Min = data
        self.run()

    @Inputs.Max
    def set_learner(self, learner):
        self.Max = learner
        self.run()


    """
    Goes through garbage collection to return the important widgets
    Returns: 
        - Dictionnary (key = Orange type of widget)
    """



    def is_study_table_exists(self,engine):
        insp = sql_inspect(engine)
        return 'studies' in insp.get_table_names()


    def recu_in_data(self,in_datas):
        liste_char_iteration = ["n_iteration", "iteration", "n itération", "n itérations", "itération"]
        Max = None
        Min = None
        try:
            for in_data in in_datas:
                for elem in in_data:
                    if elem[0] == "maximize":
                        direction = elem[0]
                    if elem[0] == "minimize":
                        direction = elem[0]
                for x in liste_char_iteration:
                    if x in in_data.domain:
                        metaparameters = in_data
                        break
                    else:
                        parameters = in_data
            for i in range(len(in_datas)):
                for j in range(len(in_datas)):
                    if in_datas[i].domain == in_datas[j].domain:
                        domain = in_datas[i].domain
                        if in_datas[i][0][1] > in_datas[j][0][1]:
                            Max = in_datas[i]
                            Min = in_datas[j]
                        else:
                            Max = in_datas[j]
                            Min = in_datas[i]
            if not metaparameters:
                self.widgets["Python Script"].Error.add_message("data", "'n itération' is required in metaparameters !")
                getattr(self.widgets["Python Script"].Error, "data")()
                raise ValueError("'%s' is not in metaparameters, it is required" % "n itération")

            # Gestion erreurs si min explo pas défini
            if Min == None:
                self.widgets["Python Script"].Error.add_message("data", "'min explo' is required in metaparameters !")
                getattr(self.widgets["Python Script"].Error, "data")()
                raise ValueError("'%s' is not in metaparameters, it is required" % "min explo")
            if metaparameters[0][1] != 0:
                return (metaparameters)
            else:
                return (None)

        except:
            for elem in in_datas:
                if elem == "maximize":
                    direction = elem
                if elem == ("minimize"):
                    direction = elem
            for i in range(len(in_datas.domain)):
                for j in range(len(in_datas.domain)):
                    if in_datas.domain[i] == in_datas.domain[j]:
                        domain = in_datas[i].domain
                        if in_datas[i][0] > in_datas[j][0]:
                            Max = in_datas[i]
                            Min = in_datas[j]
                        else:
                            Max = in_datas[j]
                            Min = in_datas[i]


    """
    Get a dictionary of widgets with their corresponding captions as keys.
    Returns:
        widgets (dict): A dictionary of widgets with their captions as keys.
    """


    def get_widgets(self):
        # Create an empty dictionary to store the widgets
        # Iterate through all objects in the garbage collector
        for obj in gc.get_objects():
            # Check if the object is an instance of OWSave and has the captionTitle "Sauvegarde du score"
            if isinstance(obj, OWSave) and obj.captionTitle == "Sauvegarde du score":
                self.widgets["Save Data"] = obj
            # Check if the object is an instance of OWPythonScript and has the captionTitle "Gestionnaire"
            if isinstance(obj, OWPythonScript) and obj.captionTitle == "Optimizer":
                self.widgets["Python Script"] = obj
            # Check if the object is an instance of OWCreateInstance and has the captionTitle "Réglage des métaparamètres"
            if isinstance(obj, OWCreateInstance) and obj.captionTitle == "Réglage des métaparamètres":
                self.widgets["Create Instance"] = obj
            # Check if the object is an instance of OWCreateInstance and has the captionTitle "Réglage des variables"
            if isinstance(obj, OWCreateInstance) and obj.captionTitle == "Réglage des variables":
                self.widgets["Réglage des variables"] = obj

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


    def chiffres_apres_virgule(self,nombre):
        # Convertir le nombre en chaîne de caractères
        chaine = str(nombre)

        # Rechercher l'indice du point décimal
        indice_point = chaine.find('.')

        # Si le point décimal n'est pas trouvé, retourner 0
        if indice_point == -1:
            return 0

        # Retourner le nombre de chiffres après le point décimal
        return len(chaine) - indice_point - 1


    def set_createinstance(self,widget, data, table_creat_ref, study):
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


    def convert_data_for_optuna(self,domain, data, minlist, maxlist, listparam, study):
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


    def load_pkl(self,filepath):
        file = OWFile()
        file.add_path(filepath)
        file.load_data()
        data = file.data
        return data


    """
    Thread to run TPE optimization
    """


    class Thread_TPE(QThread):
        finished_signal = pyqtSignal(optuna.study.Study, OWFile, OWCreateInstance, OWPythonScript)
        sleepsignal = pyqtSignal()

        def __init__(self, in_data, score_filepath, widgets, n_trials=0, direction="minimize", parent=None):
            super().__init__(parent)
            self.in_data = in_data
            self.score_filepath = score_filepath
            self.widgets = widgets
            self.n_trials = n_trials
            self.direction = direction
            self.i = 0

        def detect_change(self):
            timestamp = os.path.getmtime(self.score_filepath)
            while True:
                nouvel_timestamp = os.path.getmtime(self.score_filepath)
                if nouvel_timestamp != timestamp:
                    timestamp = nouvel_timestamp
                    return True

        def run(self):
            def objective_function(trial):
                try:
                    self.i += 1
                    # Extraction des valeurs minimales, maximales et noms des paramètres de l'Orange.data.Table d'entrée
                    # data = get_parameters_status(self.widgets["Select Columns"])

                    # Génération des valeurs des paramètres à tester dans cette itération
                    listparam = []
                    for i in range(len(self.domain)):
                        if self.domain[i].is_continuous:
                            listparam.append(
                                trial.suggest_float(name=str(self.domain[i]), low=self.Min[i], high=self.Max[i], step=0.001))
                        elif self.domain[i].is_discrete:
                            choices = self.domain[i].values
                            listparam.append(trial.suggest_categorical(name=str(self.domain[i]), choices=choices))
                    out_table = Table.from_list(self.domain, [self.Min, self.Max])
                    mesbornes = [self.Min, self.Max]
                    table_creat_instance = Table.from_list(self.domain, mesbornes)
                    table_creat_ref = Table.from_list(self.domain, [listparam])
                    self.set_createinstance(self.widgets["Réglage des variables"], table_creat_instance, table_creat_ref, study)
                    score_has_changed = self.detect_change()
                    while not score_has_changed:
                        score_has_changed = self.detect_change()
                        self.sleepsignal.emit()
                    try:
                        data = self.load_pkl(self.score_filepath)
                        self.sleepsignal.emit()
                    except:
                        data = self.load_pkl(self.score_filepath)
                        self.sleepsignal.emit()
                    scores = []
                    listname = []
                    listparam1 = []
                    params = {}
                    distributions = {}
                    print(self.convert_data_for_optuna(self.domain, data, self.Min, self.Max, listparam, study))
                    return (self.convert_data_for_optuna(self.domain, data, self.Min, self.Max, listparam, study))

                except Exception as e:
                    print(f"Erreur dans objective_function : {e}")
                    raise

            # self.sleepsignal.emit()

            # Création de l'étude Optuna pour l'optimisation
            try:
                # Créer une connexion à la base de données
                engine = create_engine(self.DATABASE_URL)

                # Inspecter le moteur pour obtenir les noms des tables existantes
                inspector = sql_inspect(engine)
                table_names = inspector.get_table_names()

                # Vérifier si la table 'studies' existe dans la liste des tables
                if 'studies' in table_names:
                    storage = RDBStorage(url=self.DATABASE_URL)
                    study = optuna.load_study(study_name=self.study_name, storage=storage)
                else:
                    # Si la table 'studies' n'existe pas, créer une nouvelle étude Optuna
                    storage = RDBStorage(url=self.DATABASE_URL)
                    study = optuna.create_study(directions=['minimize'], study_name=self.study_name, storage=storage,
                                                load_if_exists=True)

                # Émettre un signal pour indiquer le début de l'optimisation
                self.sleepsignal.emit()

                # Optimiser l'étude avec la fonction objective_function
                study.optimize(objective_function, n_trials=self.n_trials)

                # Émettre un signal pour indiquer la fin de l'optimisation
                self.finished_signal.emit(study, None, self.widgets["Create Instance"], self.widgets["Python Script"])

            except FileNotFoundError as e:
                print(f"Erreur: Fichier non trouvé - {e}")
                # Gérer l'erreur de fichier non trouvé ici.

            except Exception as e:
                print(f"Une erreur s'est produite dans la création de l'étude: {e}")
                # Gérer d'autres exceptions spécifiques si nécessaire.


    # Fonction pour recharger les données dans le widget Orange

    def sleepfunc(self):
        time.sleep(0.5)


    # Fonction exécutée après la fin de l'optimisation
    def finish_func(self,study, widgetFile, widgetCreateInstance, widgetPythonScript):
        # Préparation des meilleures combinaisons de paramètres trouvées
        self.set_n_iteration(widgetCreateInstance, val=1)
        self.metaparameters[0] = 0

    def run(self):
        widgets = self.get_widgets()
        print(widgets)
        #
        # Le self.send_signal.emit(out_table, self.widgets["Python Script"])
        # Doit être utilisé à travers un thread : utilisation de "self"
        n_trials = 1
        direction   = "minimize"
        optimizer = "TPE"
        if optimizer == "TPE":
            out_object = None
            if n_trials <= 0:
                widgets["Réglage des variables"].model.rowCount()
                widgets["Réglage des variables"].model.removeRows(0, widget.model.rowCount())
            else:
                try:
                    save_widget = widgets["Save Data"]
                    score_filepath = str(save_widget.filename)
                except:
                    score_filepath = None
                my_thread = self.Thread_TPE(in_data=None, score_filepath=score_filepath, widgets=widgets,
                                       n_trials=n_trials,
                                       direction=direction)
                my_thread.finished_signal.connect(self.finish_func)
                my_thread.sleepsignal.connect(self.sleepfunc)
                my_thread.start()

                try:
                    storage = RDBStorage(url=self.DATABASE_URL)
                    study = optuna.create_study(study_name=self.study_name, storage=storage, load_if_exists=True)
                    meilleures_combinaisons = study.trials_dataframe().drop(
                        columns=['datetime_start', 'datetime_complete', 'duration', 'state'])
                    out_domain = Orange.data.Domain(
                        [Orange.data.ContinuousVariable(col) for col in meilleures_combinaisons.columns])
                    # Append rows from Pandas DataFrame to Orange Table
                    list_row = []
                    for _, row in meilleures_combinaisons.iterrows():
                        list_row.append(list(row))

                    result_Table = Table.from_list(out_domain, list_row)
                    self.Outputs.Out_table.send(result_Table)
                except:
                    print("no database")

        else:
            out_data = Table.from_list(self.domain, [])
            out_object = Table.from_list(self.domain, [self.Min, self.Max])
if __name__ == "__main__":




    # ne pas utiliser cette méthode car elle ne permet pas d ecrire facilement des fichiers
    #WidgetPreview(OWDataSamplerA).run(set_data=data)
    # utiliser plutot ce qui est ci dessous
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    mon_objet = Optimizer()
    mon_objet.show()
    mon_objet.set_data([])
    mon_objet.handleNewSignals()
    app.exec_()