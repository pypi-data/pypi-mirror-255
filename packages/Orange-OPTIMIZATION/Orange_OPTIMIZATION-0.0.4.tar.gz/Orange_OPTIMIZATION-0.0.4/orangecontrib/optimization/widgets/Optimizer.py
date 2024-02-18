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

"""
Goes through garbage collection to return the important widgets
Returns: 
    - Dictionnary (key = Orange type of widget)
"""
chemin_courant = os.path.expanduser("~")
study_name = 'exemple'
# Constantes ...
# Définir le chemin de la base de données dans le dossier actuel
DATABASE_URL = f'sqlite:///{os.path.join(chemin_courant, study_name + ".db")}'
SCORE_FILENAME = 'tableau_score.xlsx'

liste_domain = []
liste_data = []
parameters = None

min_explo = in_datas[1]
max_explo = in_datas[2]
domain = in_datas[1].domain
min_explo = None
max_explo = None

for i, data_i in enumerate(in_datas):
    for j, data_j in enumerate(in_datas):
        if i != j and data_i.domain == data_j.domain:
            if min_explo is None or data_i[0][0] < min_explo[0]:
                min_explo = data_i[0]
            if max_explo is None or data_i[0][0] > max_explo[0]:
                max_explo = data_i[0]

if in_object != None:
    storage = RDBStorage(url=DATABASE_URL)
    study = optuna.create_study(study_name=study_name, storage=storage, load_if_exists=True)
    meilleures_combinaisons = study.trials_dataframe().drop(
        columns=['datetime_start', 'datetime_complete', 'duration', 'state'])
    # Filtrer les colonnes qui contiennent le mot 'params'
    colonnes_params = meilleures_combinaisons.filter(like='params')


def is_study_table_exists(engine):
    insp = sql_inspect(engine)
    return 'studies' in insp.get_table_names()


def recu_in_data(in_datas):
    liste_char_iteration = ["n_iteration", "iteration", "n itération", "n itérations", "itération"]
    max_explo = None
    min_explo = None
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
                        max_explo = in_datas[i]
                        min_explo = in_datas[j]
                    else:
                        max_explo = in_datas[j]
                        min_explo = in_datas[i]
        if not metaparameters:
            widgets["Python Script"].Error.add_message("data", "'n itération' is required in metaparameters !")
            getattr(widgets["Python Script"].Error, "data")()
            raise ValueError("'%s' is not in metaparameters, it is required" % "n itération")

        # Gestion erreurs si min explo pas défini
        if min_explo == None:
            widgets["Python Script"].Error.add_message("data", "'min explo' is required in metaparameters !")
            getattr(widgets["Python Script"].Error, "data")()
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
                        max_explo = in_datas[i]
                        min_explo = in_datas[j]
                    else:
                        max_explo = in_datas[j]
                        min_explo = in_datas[i]


file_object = in_object

print("\nDomain", domain, "\nMin explo", min_explo, "\nMax explo", max_explo)

"""
Get a dictionary of widgets with their corresponding captions as keys.
Returns:
    widgets (dict): A dictionary of widgets with their captions as keys.
"""


def get_widgets():
    # Create an empty dictionary to store the widgets
    widgets = dict()
    # Iterate through all objects in the garbage collector
    for obj in gc.get_objects():
        # Check if the object is an instance of OWSave and has the captionTitle "Sauvegarde du score"
        if isinstance(obj, OWSave) and obj.captionTitle == "Sauvegarde du score":
            widgets["Save Data"] = obj
        # Check if the object is an instance of OWPythonScript and has the captionTitle "Gestionnaire"
        if isinstance(obj, OWPythonScript) and obj.captionTitle == "Optimizer":
            widgets["Python Script"] = obj
        # Check if the object is an instance of OWCreateInstance and has the captionTitle "Réglage des métaparamètres"
        if isinstance(obj, OWCreateInstance) and obj.captionTitle == "Réglage des métaparamètres":
            widgets["Create Instance"] = obj
        # Check if the object is an instance of OWCreateInstance and has the captionTitle "Réglage des variables"
        if isinstance(obj, OWCreateInstance) and obj.captionTitle == "Réglage des variables":
            widgets["Réglage des variables"] = obj
    return widgets


"""
Set n itération to val after a TPE optimization
Params:
    - widgetCreateInstance: OWCreateAttributes
    - int: val
"""


def set_n_iteration(widgetCreateInstance, val=0):
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


def chiffres_apres_virgule(nombre):
    # Convertir le nombre en chaîne de caractères
    chaine = str(nombre)

    # Rechercher l'indice du point décimal
    indice_point = chaine.find('.')

    # Si le point décimal n'est pas trouvé, retourner 0
    if indice_point == -1:
        return 0

    # Retourner le nombre de chiffres après le point décimal
    return len(chaine) - indice_point - 1


def set_createinstance(widget, data, table_creat_ref, study):
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


def convert_data_for_optuna(domain, data, minlist, maxlist, listparam, study):
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
        print(round(param_value, chiffres_apres_virgule(data.X[0][index])), data.X[0][index])
        if round(param_value, chiffres_apres_virgule(data.X[0][index])) != data.X[0][index]:
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


def load_pkl(filepath):
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
                for i in range(len(domain)):
                    if domain[i].is_continuous:
                        listparam.append(
                            trial.suggest_float(name=str(domain[i]), low=min_explo[i], high=max_explo[i], step=0.001))
                    elif domain[i].is_discrete:
                        choices = domain[i].values
                        listparam.append(trial.suggest_categorical(name=str(domain[i]), choices=choices))
                out_table = Table.from_list(domain, [min_explo, max_explo])
                mesbornes = [min_explo, max_explo]
                table_creat_instance = Table.from_list(domain, mesbornes)
                table_creat_ref = Table.from_list(domain, [listparam])
                set_createinstance(widgets["Réglage des variables"], table_creat_instance, table_creat_ref, study)
                score_has_changed = self.detect_change()
                while not score_has_changed:
                    score_has_changed = self.detect_change()
                    self.sleepsignal.emit()
                try:
                    data = load_pkl(self.score_filepath)
                    self.sleepsignal.emit()
                except:
                    data = load_pkl(self.score_filepath)
                    self.sleepsignal.emit()
                scores = []
                listname = []
                listparam1 = []
                params = {}
                distributions = {}
                print(convert_data_for_optuna(domain, data, min_explo, max_explo, listparam, study))
                return (convert_data_for_optuna(domain, data, min_explo, max_explo, listparam, study))

            except Exception as e:
                print(f"Erreur dans objective_function : {e}")
                raise

        # self.sleepsignal.emit()

        # Création de l'étude Optuna pour l'optimisation
        try:
            # Créer une connexion à la base de données
            engine = create_engine(DATABASE_URL)

            # Inspecter le moteur pour obtenir les noms des tables existantes
            inspector = sql_inspect(engine)
            table_names = inspector.get_table_names()

            # Vérifier si la table 'studies' existe dans la liste des tables
            if 'studies' in table_names:
                storage = RDBStorage(url=DATABASE_URL)
                study = optuna.load_study(study_name=study_name, storage=storage)
            else:
                # Si la table 'studies' n'existe pas, créer une nouvelle étude Optuna
                storage = RDBStorage(url=DATABASE_URL)
                study = optuna.create_study(directions=['minimize'], study_name=study_name, storage=storage,
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

def sleepfunc():
    time.sleep(0.5)


# Fonction exécutée après la fin de l'optimisation
def finish_func(study, widgetFile, widgetCreateInstance, widgetPythonScript):
    # Préparation des meilleures combinaisons de paramètres trouvées
    set_n_iteration(widgetCreateInstance, val=1)
    metaparameters[0][metaparameters.domain.index("n itération")] = 0


widgets = get_widgets()

#
# Le self.send_signal.emit(out_table, self.widgets["Python Script"])
# Doit être utilisé à travers un thread : utilisation de "self"
# Iici, tant que les métaparams sont pas définis, je passe dans le ELSE et j'envoie cela à travers le out_data
metaparameters = None
try:
    metaparameters = recu_in_data(in_datas)
except:
    metaparameters = recu_in_data(in_datas)
if metaparameters is not None:
    print(metaparameters)
    try:
        n_trials = metaparameters[0][metaparameters.domain.index("n itération")]
    except ValueError:
        raise ValueError("'%s' is not in metaparameters, it is required" % "n itération")
    try:
        print(metaparameters[0][0])
        for i in range(len(metaparameters[0])):
            print(metaparameters[0][i])
            if metaparameters[0][i] == "minimize":
                direction = metaparameters[0][i]
            if metaparameters[0][i] == "maximize":
                direction = "maximize"
    except ValueError:
        print("je suis dans le except")
        direction = "minimize"
        print("'%s' is not in metaparameters, using direction='minimize' by default" % "Optimizer direction")
    try:
        optimizer = "TPE"
    except ValueError:
        optimizer = "Plan d'expérience"
        print("'%s' is not in metaparameters, using Optimizer type='Plan d'expérience' by default" % "type optimiser")
    print("n trials :", n_trials)
    print("Optimizer direction :", direction)
    print("Exploration mode :", optimizer)

    if optimizer == "TPE":
        out_object = None
        if n_trials <= 0:
            out_object = parameters
            widgets["Réglage des variables"].model.rowCount()
            widgets["Réglage des variables"].model.removeRows(0, widget.model.rowCount())
        else:
            save_widget = widgets["Save Data"]
            score_filepath = str(save_widget.filename)
            my_thread = Thread_TPE(in_data=parameters, score_filepath=score_filepath, widgets=widgets,
                                   n_trials=n_trials,
                                   direction=direction)
            my_thread.finished_signal.connect(finish_func)
            my_thread.sleepsignal.connect(sleepfunc)
            my_thread.start()

            try:
                storage = RDBStorage(url=DATABASE_URL)
                study = optuna.create_study(study_name=study_name, storage=storage, load_if_exists=True)
                meilleures_combinaisons = study.trials_dataframe().drop(
                    columns=['datetime_start', 'datetime_complete', 'duration', 'state'])
                out_domain = Orange.data.Domain(
                    [Orange.data.ContinuousVariable(col) for col in meilleures_combinaisons.columns])
                # Append rows from Pandas DataFrame to Orange Table
                list_row = []
                for _, row in meilleures_combinaisons.iterrows():
                    list_row.append(list(row))

                result_Table = Table.from_list(out_domain, list_row)
                out_data = result_Table
            except:
                print("no database")

else:
    out_data = Table.from_list(domain, [])
    out_object = Table.from_list(domain, [min_explo, max_explo])