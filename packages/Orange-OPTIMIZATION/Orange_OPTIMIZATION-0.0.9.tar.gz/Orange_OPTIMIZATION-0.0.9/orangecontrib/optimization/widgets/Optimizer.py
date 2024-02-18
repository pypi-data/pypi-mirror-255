import gc
import os
# https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import sys
import time

import Orange.data
import Orange.data
import optuna
from Orange.data import Table
from Orange.widgets import widget
from Orange.widgets.data.owcreateinstance import OWCreateInstance
from Orange.widgets.data.owfile import OWFile
from Orange.widgets.data.owpythonscript import OWPythonScript
from Orange.widgets.data.owsave import OWSave
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from optuna.storages import RDBStorage
from orangewidget.utils.signals import Input, Output
from sqlalchemy import create_engine, inspect as sql_inspect
from torch.distributed.elastic.agent.server import Worker


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
        Min = Output("Min_Table", Table, replaces=["Min_Table"])
        Max = Output("Max_Table", Table, replaces=["Max_Table"])

    def __init__(self):
            """
            Initialize the class.
            """
            super().__init__()

            # Set the path to the UI file
            uic_path = os.path.join(os.path.dirname(__file__), 'widget_designer', 'Extract_domain.ui')

            # Load the UI file
            uic.loadUi(uic_path, self)

            # Initiali
            self.Min = None
            self.Max = None
            self.domain = None
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

    @Inputs.Min
    def set_data(self, data):
        self.Min = data
        self.domain = data.domain
        self.run()

    @Inputs.Max
    def set_learner(self, data):
        self.Max = data
        self.run()
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
        file = OWFile()
        file.add_path(filepath)
        file.load_data()
        data = file.data
        return data
    def objective_function(self,trial,study):
        try:
            self.i += 1
            # Extraction des valeurs minimales, maximales et noms des paramètres de l'Orange.data.Table d'entrée
            # data = get_parameters_status(self.widgets["Select Columns"])

            # Génération des valeurs des paramètres à tester dans cette itération
            listparam = []
            for i in range(len(self.domain)):
                if self.domain[i].is_continuous:
                    listparam.append(
                        trial.suggest_float(name=str(self.domain[i]), low=self.Min[i], high=self.Max[i],
                                            step=0.001))
                elif self.domain[i].is_discrete:
                    choices = self.domain[i].values
                    listparam.append(trial.suggest_categorical(name=str(self.domain[i]), choices=choices))
            out_table = Table.from_list(self.domain, [self.Min, self.Max])
            mesbornes = [self.Min, self.Max]
            table_creat_instance = Table.from_list(self.domain, mesbornes)
            table_creat_ref = Table.from_list(self.domain, [listparam])
            self.set_createinstance(self.widgets["Réglage des variables"], table_creat_instance,
                                    table_creat_ref, study)
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
            return self.convert_data_for_optuna(self.domain, data, self.Min, self.Max, listparam, study)
        except Exception as e:
            print(f"Erreur dans objective_function : {e}")
            raise
    def run(self):
        try:
            # Créer une connexion à la base de données
            engine = create_engine(self.DATABASE_URL)

            # Inspecter le moteur pour obtenir les noms des tables existantes
            inspector = sql_inspect(engine)
            table_names = inspector.get_table_names()

            # Vérifier si la table 'studies' existe dans la liste des tables
            if 'studies' in table_names:
                storage = RDBStorage(url=self.DATABASE_URL)
                study = optuna.load_study(study_name = self.study_name, storage = storage)
            else:
                # Si la table 'studies' n'existe pas, créer une nouvelle étude Optuna
                storage = RDBStorage(url=self.DATABASE_URL)
                study = optuna.create_study(directions=['minimize'], study_name=self.study_name, storage=storage,
                                            load_if_exists=True)

            # Optimiser l'étude avec la fonction objective_function
            study.optimize(self.objective_function, n_trials=self.n_trials)

            # Émettre un signal pour indiquer la fin de l'optimisation
            self.finished_signal.emit(study, None, self.widgets["Create Instance"], self.widgets["Python Script"])

        except FileNotFoundError as e:
            print(f"Erreur: Fichier non trouvé - {e}")
            # Gérer l'erreur de fichier non trouvé ici.

        except Exception as e:
            print(f"Une erreur s'est produite dans la création de l'étude: {e}")
            # Gérer d'autres exceptions spécifiques si nécessaire.
    def execute_thread(self):
        thread_n_2 = ExecuteThread(target=self.run)
        thread_n_2.start()
        #thread_n_2.finished.connect(finish_func)

if __name__ == "__main__":
    # ne pas utiliser cette méthode car elle ne permet pas d ecrire facilement des fichiers
    # WidgetPreview(OWDataSamplerA).run(set_data=data)
    # utiliser plutot ce qui est ci dessous
    from AnyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mon_objet = Optimizer()
    mon_objet.show()

    mon_objet.set_data([])
    mon_objet.handleNewSignals()
    app.exec_()
