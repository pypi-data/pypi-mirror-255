# https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html


import ctypes
import os
import sys
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import Orange.data
from Orange.widgets import widget

from Orange.widgets.dev_workflow import MetManagement, shared_variables, shared_functions, VarManagement
from Orange.widgets.utils.signals import Input, Output
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon


class HKH_GOTO(widget.OWWidget):
    name = "Dev. Goto"
    description = "goto label"
    icon = "icons/goto.png"
    priority = 10
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))
    want_control_area = False
    partie_1 = ""
    partie_2 = ""
    operateur = ""
    CaptionDuLabelPourGoto = ""
    AddAcondition = 0
    input_domain = None
    brut_dataset = None


    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        data_out = Output("Data", Orange.data.Table)

    def UpdateMetFile(self):
        # Method for updating a metadata file

        # Parameters:
        # - self: Instance of the class, indicating that this method is part of the current class.

        # Variables used in the method:
        # - vect_out_title: List to store titles of metadata to be transmitted.
        # - vect_out_value: List to store corresponding values of metadata.
        # - self.CaptionDuLabelPourGoto: Value of the label to call.
        # - self.AddAcondition: Value of the condition to add.
        # - self.partie_1: Value of the 'VariableInf' variable.
        # - self.partie_2: Value of the 'VariableSup' variable.
        # - self.captionTitle: Value of the title to display in case of an error.

        # Actions:
        # - Adding titles and corresponding values to the lists vect_out_title and vect_out_value.
        # - Writing the metadata file using the write_met_file function of the MetManagement class.
        # - Displaying an error message in case of failure in writing the file.

        # Return:
        # - No explicit return. The method prints an error message in case of an issue.

        vect_out_title = []
        vect_out_value = []

        vect_out_title.append("LabelToCall")
        vect_out_value.append(str(self.CaptionDuLabelPourGoto))

        vect_out_title.append("CaptionDuLabelPourGoto")
        vect_out_value.append(str(self.AddAcondition))

        vect_out_title.append("VariableInf")
        vect_out_value.append(str(self.partie_1))

        vect_out_title.append("VariableSup")
        vect_out_value.append(str(self.partie_2))

        if 0 != MetManagement.write_met_file(self, vect_out_title, vect_out_value):
            print("error writing met file ", str(self.captionTitle))
            self.error("error writing met file ", str(self.captionTitle))
            return

    def LoadAndUpdateMetFile(self):
        # Method for loading and updating a metadata file

        # Parameters:
        # - self: Instance of the class, indicating that this method is part of the current class.

        # Variables used in the method:
        # - vect_out_title: List to store titles of metadata read from the file.
        # - vect_out_value: List to store corresponding values of metadata read from the file.
        # - self.captionTitle: Value of the title to display in case of an error.
        # - self.CaptionDuLabelPourGoto: Value of the label to call.
        # - self.AddAcondition: Value of the condition to add.
        # - self.partie_1: Value of the 'VariableInf' variable.
        # - self.partie_2: Value of the 'VariableSup' variable.

        # Actions:
        # - Checking if the metadata file with the specified title exists.
        # - Reading metadata from the file using the read_met_file_from_caption function of the MetManagement class.
        # - Checking the validity of the metadata (number of elements and specific titles).
        # - Updating the class variables with the loaded metadata.
        # - Calling the UpdateMetFile method to write the updated metadata.

        # Return:
        # - Calls the UpdateMetFile method to write the updated metadata.

        vect_out_title = []
        vect_out_value = []

        if MetManagement.is_caption_file_exist(self, str(self.captionTitle)):

            if 0 != MetManagement.read_met_file_from_caption(self, str(self.captionTitle), vect_out_title,
                                                             vect_out_value):
                print("error reading loading ", str(self.captionTitle))
                self.error("error reading loading ", str(self.captionTitle))
                return self.UpdateMetFile()

            if len(vect_out_title) != 7:
                print("error number of elements in ", str(self.captionTitle))
                self.error("error number of elements in ", str(self.captionTitle))
                return self.UpdateMetFile()

            if vect_out_title[3] != "LabelToCall":
                print("error need LabelToCall", file=sys.stderr)
                return self.UpdateMetFile()

            if vect_out_title[4] != "CaptionDuLabelPourGoto":
                print("error need LabelToCall", file=sys.stderr)
                return self.UpdateMetFile()

            if vect_out_title[5] != "VariableInf":
                print("error need VariableInf", file=sys.stderr)
                return self.UpdateMetFile()

            if vect_out_title[6] != "VariableSup":
                print("error need VariableSup", file=sys.stderr)
                return self.UpdateMetFile()

            self.CaptionDuLabelPourGoto = vect_out_value[3]
            self.AddAcondition = int(vect_out_value[4])
            self.partie_1 = vect_out_value[5]
            self.partie_2 = vect_out_value[6]

        # Writing the up-to-date file
        return self.UpdateMetFile()

    @Inputs.data
    def set_data(self, dataset):
        # Method to set the input data for the widget.

        # Parameters:
        # - self: Instance of the class, indicating that this method is part of the current class.
        # - dataset: Input data (Orange.data.Table) to be set for the widget.

        # Variables used in the method:
        # - self.input_domain: Stores the domain of the input dataset.
        # - self.brut_dataset: Stores the input dataset.
        # - self.checkBox_add_a_condition: Checkbox widget to add a condition.
        # - self.partie_1: Value of the 'VariableInf' variable.
        # - self.partie_2: Value of the 'VariableSup' variable.

        # Actions:
        # - Checking if the input dataset and its domain are not None.
        # - Setting the input domain and raw dataset attributes.
        # - Checking if the checkbox for adding a condition is not checked or if 'VariableInf' and 'VariableSup' are empty.
        # - If the condition is not met, update the shared_variables.orange_data_table with the input dataset.
        # - Call the appelle_call_on_me method.

        # Return:
        # - If the condition is met, the method returns early. Otherwise, it proceeds to update the shared_variables and calls appelle_call_on_me.

        if dataset is not None and dataset.domain is not None:
            self.input_domain = dataset.domain
            self.brut_dataset = dataset

        if self.checkBox_add_a_condition.isChecked() == False or self.partie_1 == "" or self.partie_2 == "":
            shared_variables.orange_data_table = dataset
            self.appelle_call_on_me()
            return

    def appelle_call_on_me(self):
        # Method to call the 'call_on_me' method of an object identified by an ID obtained from a file.

        # Parameters:
        # - self: Instance of the class, indicating that this method is part of the current class.

        # Variables used in the method:
        # - IdToCall: Stores the ID obtained from reading a file.
        # - self.CaptionDuLabelPourGoto: Stores a caption used for file reading.
        # - vect_out_title: List to store titles obtained from reading the file.
        # - vect_out_value: List to store values obtained from reading the file.

        # Actions:
        # - Initializing IdToCall with a default value.
        # - Checking if self.CaptionDuLabelPourGoto is an empty string, and returning early if true.
        # - Attempting to read the ID from a file using MetManagement.read_met_file_from_caption method.
        # - If the reading is successful, updating IdToCall with the obtained ID.
        # - Checking if IdToCall is still set to the default value, indicating a failure in obtaining the ID.
        # - If so, displaying an error message and returning early.
        # - Otherwise, clearing any previous errors and calling the 'call_on_me' method of the object identified by IdToCall.

        IdToCall = -666
        vect_out_title = []
        vect_out_value = []

        if self.CaptionDuLabelPourGoto == "":
            return

        if 0 == MetManagement.read_met_file_from_caption(self, self.CaptionDuLabelPourGoto, vect_out_title,
                                                         vect_out_value):
            IdToCall = int(vect_out_value[2])

        if IdToCall == -666:
            self.error("/!\\ Select a label")
            return

        self.error("")

        # Note: The following line attempts to call the 'call_on_me' method of the object identified by IdToCall.
        # It assumes that the object with the specified ID exists, and it may lead to a crash if the object is not found.
        # A warning message is printed to stderr to inform about this potential issue.
        ctypes.cast(IdToCall, ctypes.py_object).value.call_on_me()

    def __init__(self):
        super().__init__()
        shared_functions.setup_shared_variables(self)
        self.setFixedWidth(497)
        self.setFixedHeight(266)
        self.setAutoFillBackground(True)
        self.LoadAndUpdateMetFile()

        # QT Management
        uic.loadUi(self.dossier_du_script + '/widget_designer/goto.ui', self)
        self.setAutoFillBackground(True)

        self.label = self.findChild(QtWidgets.QLabel, 'label')
        self.checkBox_add_a_condition = self.findChild(QtWidgets.QCheckBox, 'checkBox_add_a_condition')

        self.comboBox_variable_inf = self.findChild(QtWidgets.QComboBox, 'comboBox_variable_inf')
        self.comboBox_variable_sup = self.findChild(QtWidgets.QComboBox, 'comboBox_variable_sup')
        self.applyButton = self.findChild(QtWidgets.QPushButton, 'applyButton')
        self.applyButton.clicked.connect(self.filter_dataframe)
        self.operator = self.findChild(QtWidgets.QComboBox, 'operator_2')

        self.checkBox_add_a_condition.clicked['bool'].connect(self.Enable_conditions)
        self.comboBox_variable_inf.currentIndexChanged['int'].connect(self.on_index_changed_inf_combo_box)
        self.comboBox_variable_supp.currentIndexChanged['int'].connect(self.on_index_changed_supp_combo_box)
        self.operator.currentIndexChanged['int'].connect(self.on_index_changed_operator)
        self.installEventFilter(self)


        self.push_button = self.findChild(QtWidgets.QPushButton, 'pushButton_show_hkh_website')
        self.push_button.setIcon(QIcon(self.dossier_du_script+'/icons/Logo_HKH.svg'))
        self.push_button.setIconSize(QSize(65, 65))
        self.push_button.clicked.connect(shared_functions.openlink)

        #QtCore.QMetaObject.connectSlotsByName(Form)
        self.refresh_all()


        MetManagement.force_save(self)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.refresh_all()
        # return super.eventFilter(obj,event) # True on filtre l element
        return super().eventFilter(source, event)


        # True ou False -> False on ne filtre pas

    def refresh_all(self):
        # Method to refresh various aspects of the current object.

        # Actions:
        # - Calling the 'LoadAndUpdateMetFile' method to load and update metadata file parameters.
        # - Clearing any previous error messages.
        # - Checking the value of 'AddAcondition' parameter.
        #   - If 'AddAcondition' is 0, unchecking the 'checkBox_add_a_condition' checkbox and disabling conditions.
        #   - If 'AddAcondition' is not 0, checking the checkbox, enabling conditions, and attempting to read a dictionary of variables.
        #     - If an error occurs during variable reading, the method returns early.
        # - Calling the 'UpdateMetFile' method to update metadata file parameters.

        self.LoadAndUpdateMetFile()
        self.error("")

        if self.AddAcondition == 0:
            self.checkBox_add_a_condition.setChecked(False)
            self.Enable_conditions(False)
        else:
            self.checkBox_add_a_condition.setChecked(True)
            self.Enable_conditions(True)

            if 0 != VarManagement.read_dict_variable(self):
                return

        self.UpdateMetFile()

    def Enable_conditions(self, booleen):
        # Method to enable or disable conditions based on the boolean parameter.

        # Parameters:
        # - booleen (bool): True to enable conditions, False to disable conditions.

        # Actions:
        # - If 'booleen' is True:
        #   - Sets 'AddAcondition' to 1.
        #   - Attempts to read a dictionary of variables. If an error occurs, prints a message.
        # - If 'booleen' is False:
        #   - Sets 'AddAcondition' to 0.
        # - Calls 'UpdateMetFile' to update metadata file parameters.
        # - Enables or disables various UI components based on 'booleen'.
        # - Calls methods to populate and configure combo boxes.

        if booleen == True:
            self.AddAcondition = 1
            if 0 != VarManagement.read_dict_variable(self):
                print("pas de fichier de variable")
        else:
            self.AddAcondition = 0

        self.UpdateMetFile()
        self.operator.setEnabled(booleen)
        self.comboBox_variable_inf.setEnabled(booleen)
        self.comboBox_variable_supp.setEnabled(booleen)
        self.label_formula.setEnabled(booleen)

        # Calls methods to populate combo boxes with relevant data.
        self.chargeCombo_box_inf()
        self.chargeCombo_box_sup()
        self.chargeCombo_box_operator()

    def chargeCombo_box_inf(self):
        # Method to populate the 'comboBox_variable_inf' combo box.

        # Actions:
        # - Clears the current items in 'comboBox_variable_inf'.
        # - Backs up the current value of 'self.partie_1'.
        # - Initializes variables for tracking the index to set and a counter.
        # - If 'input_domain' is not None, iterates through the domain:
        #   - Adds items to 'comboBox_variable_inf' using the string representation of the domain elements.
        #   - Checks if the current domain element matches the backed-up 'self.partie_1' and updates 'index_a_mettre' accordingly.
        # - Sets the current index of 'comboBox_variable_inf' to 'index_a_mettre'.
        # - Calls 'maj_formula' method.

        self.comboBox_variable_inf.clear()
        backup_self_partie_1 = self.partie_1
        index_a_mettre = -1
        compteur = 0

        if self.input_domain is not None:
            tab = self.input_domain
            for i in tab:
                self.comboBox_variable_inf.addItem(str(tab[i]))
                if str(i) == backup_self_partie_1:
                    index_a_mettre = compteur
                compteur += 1

        self.comboBox_variable_inf.setCurrentIndex(index_a_mettre)
        self.maj_formula()
        return

    def chargeCombo_box_sup(self):
        # Method to populate the 'comboBox_variable_supp' combo box.

        # Actions:
        # - Backs up the current value of 'self.partie_2'.
        # - Clears the current items in 'comboBox_variable_supp'.
        # - Initializes variables for tracking the index to set and a counter.
        # - If 'input_domain' is not None, iterates through the domain:
        #   - Adds items to 'comboBox_variable_supp' using the string representation of the domain elements.
        #   - Checks if the current domain element matches the backed-up 'self.partie_2' and updates 'index_a_mettre' accordingly.
        # - Sets the current index of 'comboBox_variable_supp' to 'index_a_mettre'.

        backup_self_partie_2 = self.partie_2
        self.comboBox_variable_supp.clear()
        index_a_mettre = -1
        compteur = 0

        if self.input_domain is not None:
            tab = self.input_domain
            for i in tab:
                self.comboBox_variable_supp.addItem(str(tab[i]))
                if str(i) == backup_self_partie_2:
                    index_a_mettre = compteur
                compteur += 1

        self.comboBox_variable_supp.setCurrentIndex(index_a_mettre)
        return


    def chargeCombo_box_operator(self):
        self.operator.clear()
        # lecture des
        index_a_mettre = -1
        compteur = 0
        tab_operator = ['<', '>', '=', '/=']
        for key in tab_operator:
            self.operator.addItem(str(key))

        self.operator.setCurrentIndex(index_a_mettre)
        self.maj_formula()
        return

    def on_index_changed_inf_combo_box(self, a):
        if self.checkBox_add_a_condition.isChecked() == False:
            return
        if a == -1:
            return
        self.partie_1 = self.comboBox_variable_inf.currentText()
        self.maj_formula()
        self.UpdateMetFile()

    def on_index_changed_supp_combo_box(self, a):
        if self.checkBox_add_a_condition.isChecked() == False:
            return
        if a == -1:
            return
        self.partie_2 = self.comboBox_variable_supp.currentText()
        self.maj_formula()
        self.UpdateMetFile()

    def on_index_changed_operator(self, a):
        if self.checkBox_add_a_condition.isChecked() == False:
            return
        if a == -1:
            return
        self.operateur = self.operator.currentText()
        self.maj_formula()
        self.UpdateMetFile()

    def maj_formula(self):
        if self.checkBox_add_a_condition.isChecked() == False:
            self.label_formula.setText("Formula :")
            self.UpdateMetFile()
            return
        if self.partie_1 == "" or self.partie_2 == "":
            self.label_formula.setText("Formula :")
        else:
            texte_a_afficher = "If "
            texte_a_afficher += self.partie_1 + self.operateur + self.partie_2
            texte_a_afficher += ' goto label Else "standard output"'
            self.label_formula.setText(texte_a_afficher)
        self.UpdateMetFile()

    def filter_dataframe(self):
        """
        Filtre un DataFrame en fonction de l'opérateur spécifié entre deux colonnes.

        Parameters:
        - df (pandas.DataFrame): Le DataFrame à filtrer.
        - column1 (str): Nom de la première colonne.
        - column2 (str): Nom de la deuxième colonne.
        - operator (str): Opérateur de comparaison (<'inferieur', 'superieur', 'egal', 'different'>).

        Returns:
        - pandas.DataFrame: Le DataFrame filtré.
        """
        _df = None
        if self.brut_dataset is not None:
            _df = table_to_frame(self.brut_dataset)

        column1 = self.partie_1
        column2 = self.partie_2
        operator = self.operateur
        result_df = 0

        if operator != "" and column1 != "" and column2 != "":
            if operator == '<':
                result_df = _df[_df[column1] < _df[column2]]
            elif operator == '>':
                result_df = _df[_df[column1] > _df[column2]]
            elif operator == '=':
                result_df = _df[_df[column1] == _df[column2]]
            elif operator == '/=':
                result_df = _df[_df[column1] != _df[column2]]
            else:
                raise ValueError("Opérateur invalide. Utilisez l'un des suivants : 'inferieur', 'superieur', 'egal', 'different'.")

        out_data = table_from_frame(result_df)
        self.Outputs.data_out.send(out_data)

if __name__ == "__main__":
    # sys.exit(main())
    from Orange.data.io import CSVReader

    shared_variables.current_doc = os.path.dirname(__file__) + "/dataset_devellopper/fakeows.ows"

    file = os.path.dirname(__file__) + "/dataset_devellopper/fake_input.csv"  #
    objet_csv_reader = CSVReader(file)
    objet_csv_reader.DELIMITERS = ';'
    data = objet_csv_reader.read()


    from AnyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    mon_objet = HKH_GOTO()
    mon_objet.show()


    mon_objet.handleNewSignals()
    app.exec_()
