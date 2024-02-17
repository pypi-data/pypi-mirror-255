#https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import os
import sys
from pathlib import Path
from statistics import median

import Orange.data
import numpy as np
from AnyQt.QtCore import QTimer
from Orange.widgets import widget
from kernel_function import Table_management
import WrapMessageBox, shared_variables, shared_functions, MetManagement

from Orange.widgets.utils.signals import Output
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon


class subworkflow_input(widget.OWWidget):
    # This part is executed when Orange is opened, whether the widget is used or not.
    # Useful for setting up trackers or other initialization tasks.
    name = "subworkflow_input"
    description = "This is the output of a subworkflow."
    icon = "icons/jcm_open_file_resize_alpha_channel.png"
    priority = 10
    # JCM's trick to get the path of the file in which the code is written.
    # Useful for loading images, etc.
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))

    # There are two areas in the window: the control area and the main area.
    # I've left both for the example, but I prefer to disable the control area.
    want_control_area = False
    want_main_area = True
    tab_to_read = ""
    vect_blabla = []

    ## End of the part executed at Orange opening
    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self):
        #On widget creation
        super().__init__()# Interact with parent class
        shared_functions.setup_shared_variables(self)
        self.data = None

        self.LoadAndUpdateMetFile()

        self.setFixedWidth(921)
        self.setFixedHeight(201)
        # QT Management
        uic.loadUi(self.dossier_du_script+'/widget_designer/subworkflow_input_ui.ui', self)

        self.button = self.findChild(QtWidgets.QPushButton, "button_link")
        self.button.clicked.connect(shared_functions.openlink)
        #self.setAutoFillBackground(True)
        # creating event/slot
        self.pushButton_select_tab = self.findChild(QtWidgets.QPushButton, 'pushButton_select_tabfile')
        self.pushButton_select_tab.clicked.connect(self.select_tabfile)
        self.label_show_link_to_tab= self.findChild(QtWidgets.QLabel, 'label')
        self.pushbutton_reload= self.findChild(QtWidgets.QPushButton, 'pushButton_reload')
        self.pushbutton_reload.clicked.connect(self.load_data)
        self.tablewidget_math_set= self.findChild(QtWidgets.QTableWidget, 'tableWidget')

        self.push_button = self.findChild(QtWidgets.QPushButton, 'pushButton_show_hkh_website')
        self.push_button.setIcon(QIcon(self.dossier_du_script+'/icons/Logo_HKH.svg'))
        self.push_button.setIconSize(QSize(65, 65))
        self.push_button.clicked.connect(shared_functions.openlink)

        self.refresh_label()
        MetManagement.force_save(self)
        QTimer.singleShot(500, self.load_data)

    def UpdateCowFile(self):
        vect_out_title = []
        vect_out_value = []
        vect_out_title.append("FileToLoad")
        vect_out_value.append("input_met.tab")

        if 0 != MetManagement.write_met_file(self, vect_out_title, vect_out_value):
            print("error writing cow file ", str(self.captionTitle))
            self.error("error writing cow file ", str(self.captionTitle))
            return


    def LoadAndUpdateMetFile(self):
        vect_out_title=[]
        vect_out_value=[]
        self.current_doc=''+str(shared_variables.current_ows)
        if MetManagement.is_caption_file_exist(self,str(self.captionTitle)):
            print("le caption existe")
            if 0!=MetManagement.read_met_file_from_caption(self,str(self.captionTitle),vect_out_title,vect_out_value):
                print("error reading loading ",str(self.captionTitle))
                self.error("error reading loading ",str(self.captionTitle))
                return self.UpdateCowFile()

            self.tab_to_read= MetManagement.current_met_directory(self)+"/input_met.tab"

        return self.UpdateCowFile()
    def load_area_of_area_validity_categorical(self, file_path):
        """
        Loads the area of area validity for categorical data from the specified file path.

        Parameters:
        - file_path: The path of the file to load.

        Action:
        - Calls loadTabWithSpecificExtention to load the Orange data table from the file.
        - Retrieves the names of attributes and metas from the loaded table.
        - Checks if the retrieved lists match the expected values, if not, prints an error message and returns.
        - Constructs a list of rows from the loaded table.
        - Initializes variables for displaying the table in the UI.
        - Populates the UI table (tableau_label_variable_cat) with the loaded data.
        """
        tab_in = Table_management.loadTabWithSpecificExtention(file_path)
        liste_domaine_attribut = []
        for element in tab_in.domain.attributes:
            liste_domaine_attribut.append(element.name)
        liste_domaine_meta = []
        for element in tab_in.domain.metas:
            liste_domaine_meta.append(element.name)
        if liste_domaine_meta != []:
            print("error liste_domaine_meta!=[]")
            return
        if liste_domaine_attribut != ['Name', 'Type', 'cste', 'Nominal', 'Categories']:
            print("error liste_domaine_attribut!=['Name', 'Type', 'cste', 'Nominal', 'Categories']")
            return
        nb_ligne = len(tab_in)
        nb_colonne_attribut = len(liste_domaine_attribut)
        rows = []
        for i in range(nb_ligne):
            row = []
            for j in range(nb_colonne_attribut):
                row.append(tab_in[i, j].value)
            rows.append(row)
        self.current_line_tableau_label_variable_cat = 0
        self.tableau_label_variable_cat.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableau_label_variable_cat.setRowCount(0)
        self.tableau_label_variable_cat.verticalHeader().setVisible(False)
        for i in range(len(rows)):
            if len(rows[i]) != 5:
                print("error nb element != 5")
                continue

            name_to_insert = rows[i][0]
            row = self.tableau_label_variable_cat.rowCount()

            self.tableau_label_variable_cat.insertRow(row)
            self.tableau_label_variable_cat.setItem(row, 0, QtWidgets.QTableWidgetItem(name_to_insert))
            self.tableau_label_variable_cat.setItem(row, 1, QtWidgets.QTableWidgetItem(rows[i][1]))
            self.tableau_label_variable_cat.setItem(row, 2, QtWidgets.QTableWidgetItem(rows[i][2]))
            self.tableau_label_variable_cat.setItem(row, 3, QtWidgets.QTableWidgetItem(str(rows[i][3])))
            self.tableau_label_variable_cat.setItem(row, 4, QtWidgets.QTableWidgetItem(str(rows[i][4])))

    def load_area_of_area_validity(self, file_path):
        """
        Loads the area of area validity for continuous data from the specified file path.

        Parameters:
        - file_path: The path of the file to load.

        Action:
        - Calls loadTabWithSpecificExtention to load the Orange data table from the file.
        - Retrieves the names of attributes and metas from the loaded table.
        - Checks if the retrieved lists match the expected values, if not, prints an error message and returns.
        - Constructs a list of rows from the loaded table.
        - Initializes variables for displaying the table in the UI.
        - Populates the UI table (tableau_label_variable) with the loaded data.
        """
        tab_in = Table_management.loadTabWithSpecificExtention(file_path)
        liste_domaine_attribut = []
        for element in tab_in.domain.attributes:
            liste_domaine_attribut.append(element.name)
        liste_domaine_meta = []
        for element in tab_in.domain.metas:
            liste_domaine_meta.append(element.name)
        if liste_domaine_meta != []:
            print("error liste_domaine_meta!=[]")
            return
        if liste_domaine_attribut != ['Name', 'Type', 'cste', 'Nominal', 'Min', 'Max', 'Step']:
            print("error liste_domaine_attribut!=['Name', 'Type', 'cste', 'Nominal', 'Min', 'Max', 'Step']")
            return
        nb_ligne = len(tab_in)
        nb_colonne_attribut = len(liste_domaine_attribut)
        rows = []
        for i in range(nb_ligne):
            row = []
            for j in range(nb_colonne_attribut):
                row.append(tab_in[i, j].value)
            rows.append(row)
        self.current_line_tableau_label_variable = 0
        self.tableau_label_variable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableau_label_variable.setRowCount(0)
        self.tableau_label_variable.verticalHeader().setVisible(False)
        for i in range(len(rows)):
            if len(rows[i]) != 7:
                print("error nb element != 7")
                continue

            name_to_insert = rows[i][0]
            row = self.tableau_label_variable.rowCount()
            self.tableau_label_variable.insertRow(row)
            self.tableau_label_variable.setItem(row, 0, QtWidgets.QTableWidgetItem(name_to_insert))
            self.tableau_label_variable.setItem(row, 1, QtWidgets.QTableWidgetItem(rows[i][1]))
            self.tableau_label_variable.setItem(row, 2, QtWidgets.QTableWidgetItem(rows[i][2]))
            self.tableau_label_variable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(rows[i][3])))
            self.tableau_label_variable.setItem(row, 4, QtWidgets.QTableWidgetItem(str(rows[i][4])))
            self.tableau_label_variable.setItem(row, 5, QtWidgets.QTableWidgetItem(str(rows[i][5])))
            self.tableau_label_variable.setItem(row, 6, QtWidgets.QTableWidgetItem(str(rows[i][6])))

    def save_area_of_validity(self):
        """
        Saves the area of validity for continuous data.

        Action:
        - Checks if the name_of_file_of_validity is empty, if yes, shows an error message and returns.
        - Constructs the full path of the file using the entered name and current directory.
        - Checks if the file already exists, if yes, asks for confirmation to overwrite.
        - Constructs a 2D array for the Orange data table from the displayed table in the UI.
        - Creates an Orange data table using CreateOrangeDataTableFrom2dArray.
        - Filters and permutates the columns of the table based on the desired order.
        - Saves the table using saveTabWithSpecificExtention.
        """
        if self.lineEdit_name_of_file_of_validity.text() == "":
            WrapMessageBox.create_message_box("Error you need to choose a name of the file", "error", "")
            return


        array_2D_no_header = []
        for row in range(self.tableau_label_variable.rowCount()):
            line_to_add = []
            line_to_add.append(float(self.tableau_label_variable.item(row, 3).text()))
            line_to_add.append(float(self.tableau_label_variable.item(row, 4).text()))
            line_to_add.append(float(self.tableau_label_variable.item(row, 5).text()))
            line_to_add.append(float(self.tableau_label_variable.item(row, 6).text()))
            line_to_add.append(self.tableau_label_variable.item(row, 0).text())
            line_to_add.append(self.tableau_label_variable.item(row, 1).text())
            line_to_add.append(self.tableau_label_variable.item(row, 2).text())
            array_2D_no_header.append(line_to_add)
        vect_name_continuous_variable = ["Nominal", "Min", "Max", "Step"]
        vect_number_of_decimal_continuous_variable = [6, 6, 6, 6]
        vect_name_discrete_variable = ["Name", "Type", "cste"]
        vect_value_of_discrete_variable = [
            Table_management.GetListDiscreteFromListWithDoublon([row[4] for row in array_2D_no_header]),
            Table_management.GetListDiscreteFromListWithDoublon([row[5] for row in array_2D_no_header]),
            ["True", "False"]]
        name = "toto"
        table_to_save = Table_management.CreateOrangeDataTableFrom2dArray(vect_name_continuous_variable,
                                                                          vect_number_of_decimal_continuous_variable,
                                                                          vect_name_discrete_variable,
                                                                          vect_value_of_discrete_variable,
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          array_2D_no_header)
        table_to_save = Table_management.filter_and_permutate_column_variable(table_to_save, [4, 5, 6, 0, 1, 2, 3])
        Table_management.saveTabWithSpecificExtention(table_to_save, name)

    def save_area_of_validity_cat(self):
        """
        Saves the area of validity for categorical data.

        Action:
        - Checks if the name_of_file_of_validity_cat is empty, if yes, shows an error message and returns.
        - Constructs the full path of the file using the entered name and current directory.
        - Checks if the file already exists, if yes, asks for confirmation to overwrite.
        - Constructs a 2D array for the Orange data table from the displayed table in the UI.
        - Creates an Orange data table using CreateOrangeDataTableFrom2dArray.
        - Saves the table using saveTabWithSpecificExtention.
        """


        array_2D_no_header = []
        for row in range(self.tableau_label_variable_cat.rowCount()):
            line_to_add = []
            line_to_add.append(self.tableau_label_variable_cat.item(row, 0).text())
            line_to_add.append(self.tableau_label_variable_cat.item(row, 1).text())
            line_to_add.append(self.tableau_label_variable_cat.item(row, 2).text())
            line_to_add.append(self.tableau_label_variable_cat.item(row, 3).text())
            line_to_add.append(self.tableau_label_variable_cat.item(row, 4).text())
            array_2D_no_header.append(line_to_add)
        vect_name_discrete_variable = ["Name", "Type", "cste", "Nominal", "Categories"]
        vect_value_of_discrete_variable = [
            Table_management.GetListDiscreteFromListWithDoublon([row[0] for row in array_2D_no_header]),
            Table_management.GetListDiscreteFromListWithDoublon([row[1] for row in array_2D_no_header]),
            ["True", "False"],
            Table_management.GetListDiscreteFromListWithDoublon([row[3] for row in array_2D_no_header]),
            Table_management.GetListDiscreteFromListWithDoublon([row[4] for row in array_2D_no_header]), ]
        name = "toto"
        table_to_save = Table_management.CreateOrangeDataTableFrom2dArray([],
                                                                          [],
                                                                          vect_name_discrete_variable,
                                                                          vect_value_of_discrete_variable,
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          [],
                                                                          array_2D_no_header)
        Table_management.saveTabWithSpecificExtention(table_to_save, name)

    def create_file_new_are_of_validity(self):
        """
        Creates a new file for the area of validity for continuous data.

        Action:
        - Calls refresh_tabular to update the tabular data.
        - Initializes the UI table (tableau_label_variable) for continuous data.
        - Populates the UI table based on the data in tablewidget_math_set.
        - Calculates default values for Nominal, Min, Max, and Step.
        - Saves the area of validity using save_area_of_validity method.
        """
        self.refresh_tabular()
        self.current_line_tableau_label_variable = 0
        self.tableau_label_variable.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableau_label_variable.setRowCount(0)
        self.tableau_label_variable.verticalHeader().setVisible(False)

        for i in range(self.tablewidget_math_set.columnCount()):
            name_to_insert = self.tablewidget_math_set.horizontalHeaderItem(i).text()
            row = self.tableau_label_variable.rowCount()
            self.tableau_label_variable.insertRow(row)

            if self.tablewidget_math_set.item(0, i) is not None:
                self.tableau_label_variable.setItem(row, 1, QtWidgets.QTableWidgetItem(
                    self.tablewidget_math_set.item(0, i).text()))
            if self.tablewidget_math_set.rowCount() > 2:
                tab_en_cours = []
                for j in range(self.tablewidget_math_set.rowCount()):
                    tab_en_cours.append(self.tablewidget_math_set.item(j, i).text())
                # here we search for the values of min, max, step default of each column
                strNominal = "0"
                strMin = "0"
                strMax = "0"
                strStep = "0.1"

                if len(tab_en_cours) >= 2 and tab_en_cours[0] == 'ContinuousVariable':
                    continuous_variables = [float(element) for element in tab_en_cours[1:]]

                    fMin = min(continuous_variables)
                    fMax = max(continuous_variables)

                    strMin = str(fMin)
                    strMax = str(fMax)
                    dec = strMax[::-1].find('.')
                    strNominal = str(median(continuous_variables))
                    diffs = list(set(continuous_variables))
                    diffs = np.abs(np.diff(sorted(diffs)))
                    if len(diffs) > 0:
                        fStep = np.min(diffs)
                    else:
                        fStep = 0.001
                    if fStep < 0.00001:
                        fStep = 0.001
                    fStep1 = (int((fMax - fMin) / fStep))
                    if fStep1 < 0.00001:
                        fStep1 = 0.001
                    fStep = round(((fMax - fMin) / fStep1), dec)
                    strStep = str(fStep)
                    # here handle rounding to avoid subsequent rounding
            else:
                tab_en_cours = []
                for j in range(self.tablewidget_math_set.rowCount()):
                    tab_en_cours.append(self.tablewidget_math_set.item(j, i).text())
                # here we search for the values of min, max, step default of each column
                strNominal = "0"
                strMin = "0"
                strMax = "0"
                strStep = "0"

                if len(tab_en_cours) >= 2 and tab_en_cours[0] == 'ContinuousVariable':
                    continuous_variables = [float(element) for element in tab_en_cours[1:]]

                    fMin = min(continuous_variables)
                    fMax = max(continuous_variables)

                    strMin = str(fMin)
                    strMax = str(fMax)
                    dec = strMax[::-1].find('.')
                    strNominal = str(median(continuous_variables))
                    # here handle rounding to avoid subsequent rounding

            # print(strNominal,strMin,strMax,strStep)

            self.tableau_label_variable.setItem(row, 0, QtWidgets.QTableWidgetItem(name_to_insert))
            self.tableau_label_variable.setItem(row, 2, QtWidgets.QTableWidgetItem("False"))
            self.tableau_label_variable.setItem(row, 3, QtWidgets.QTableWidgetItem(strNominal))
            self.tableau_label_variable.setItem(row, 4, QtWidgets.QTableWidgetItem(strMin))
            self.tableau_label_variable.setItem(row, 5, QtWidgets.QTableWidgetItem(strMax))
            self.tableau_label_variable.setItem(row, 6, QtWidgets.QTableWidgetItem(strStep))

        self.save_area_of_validity()
        return

    def create_file_new_are_of_validity_cat(self):
        """
        Creates a new file for the area of validity for categorical data.

        Action:
        - Calls refresh_tabular_cat to update the tabular data.
        - Initializes the UI table (tableau_label_variable_cat) for categorical data.
        - Populates the UI table based on the data in tablewidget_math_set_cat.
        - Calculates default values for Nominal and Categories.
        - Saves the area of validity using save_area_of_validity_cat method.
        """
        self.refresh_tabular_cat()
        self.current_line_tableau_label_variable_cat = 0
        self.tableau_label_variable_cat.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.tableau_label_variable_cat.setRowCount(0)
        self.tableau_label_variable_cat.verticalHeader().setVisible(False)

        for i in range(self.tablewidget_math_set_cat.columnCount()):
            name_to_insert = self.tablewidget_math_set_cat.horizontalHeaderItem(i).text()
            row = self.tableau_label_variable_cat.rowCount()
            self.tableau_label_variable_cat.insertRow(row)

            if self.tablewidget_math_set_cat.item(0, i) is not None:
                self.tableau_label_variable_cat.setItem(row, 1, QtWidgets.QTableWidgetItem(
                    self.tablewidget_math_set_cat.item(0, i).text()))
            if self.tablewidget_math_set_cat.rowCount() >= 2:
                tab_en_cours = []
                for j in range(self.tablewidget_math_set_cat.rowCount()):
                    tab_en_cours.append(self.tablewidget_math_set_cat.item(j, i).text())
                # here we search for the values of min, max, step default of each column
                strNominal = "0"
                strCategories = "0"
                discrete_variables = []
                categories = []

                if len(tab_en_cours) >= 2 and tab_en_cours[0] == 'DiscreteVariable':
                    discrete_variables = [str(element) for element in tab_en_cours[1:]]
                    categories = list(dict.fromkeys(discrete_variables))

                    strNominal = max(set(discrete_variables),
                                     key=discrete_variables.count)  # Find element with most occurrences in list
                    if self.categories.get(name_to_insert) == None:
                        strCategories = ";".join(categories)
                    else:
                        strCategories = ";".join(self.categories.get(name_to_insert))
                    # here handle rounding to avoid subsequent rounding
            else:
                tab_en_cours = []
                for j in range(self.tablewidget_math_set_cat.rowCount()):
                    tab_en_cours.append(self.tablewidget_math_set_cat.item(j, i).text())
                # here we search for the values of min, max, step default of each column
                strNominal = "0"
                strCategories = "0"

                if len(tab_en_cours) >= 2 and tab_en_cours[0] == 'DiscreteVariable':
                    discrete_variables = [str(element) for element in tab_en_cours[1:]]
                    categories = list(dict.fromkeys(discrete_variables))

                    strNominal = "0"
                    strNominal = max(set(discrete_variables),
                                     key=discrete_variables.count)  # Find element with most occurrences in list
                    strCategories = ";".join(categories)
                    # here handle rounding to avoid subsequent rounding

            # print(strNominal,strMin,strMax,strStep)

            self.tableau_label_variable_cat.setItem(row, 0, QtWidgets.QTableWidgetItem(name_to_insert))
            self.tableau_label_variable_cat.setItem(row, 2, QtWidgets.QTableWidgetItem("False"))
            self.tableau_label_variable_cat.setItem(row, 3, QtWidgets.QTableWidgetItem(strNominal))
            self.tableau_label_variable_cat.setItem(row, 4, QtWidgets.QTableWidgetItem(strCategories))
        self.save_area_of_validity_cat()
        return

    def refresh_tabular(self):
        # Refreshes the tabular view with data from the specified table

        # Check if there is a table to read
        if self.tab_to_read == "":
            print("nothing to read")
            return

        # Initialize lists for domain and index variables
        liste_domaine = []
        liste_index_var_cont = []

        # Clear existing data from the table widget
        self.tablewidget_math_set.clear()
        self.tablewidget_math_set.setRowCount(0)
        self.tablewidget_math_set.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Load data from the specified table
        data_data = Orange.data.Table(self.tab_to_read)

        # Check if the dataset is None
        if data_data is None:
            print("dataset = None")
            return

        # Extract index of continuous variables
        for element in data_data.domain:
            if type(element).__name__ == "ContinuousVariable":
                liste_index_var_cont.append(data_data.domain.index(element))

        # Filter and permute columns based on continuous variables
        data_data = Table_management.filter_and_permutate_column_variable(data_data, liste_index_var_cont)

        # Set column count in the table widget
        self.tablewidget_math_set.setColumnCount(len(data_data.domain))

        # Populate horizontal header with variable names
        compteur = 0
        for element in data_data.domain:
            self.tablewidget_math_set.setHorizontalHeaderItem(compteur, QtWidgets.QTableWidgetItem(element.name))
            compteur += 1
            liste_domaine.append(element.name)

        # Insert a row for data type information
        header = self.tablewidget_math_set.horizontalHeader()
        row = self.tablewidget_math_set.rowCount()
        self.tablewidget_math_set.insertRow(row)
        compteur = 0

        # Populate the data type information in the last inserted row
        for element in data_data.domain:
            self.tablewidget_math_set.setItem(row, compteur, QtWidgets.QTableWidgetItem(type(element).__name__))
            compteur += 1

        # Populate the table widget with data
        for i in range(len(data_data)):
            row = self.tablewidget_math_set.rowCount()
            self.tablewidget_math_set.insertRow(row)
            for j in range(len(data_data.domain)):
                self.tablewidget_math_set.setItem(row, j,
                                                  QtWidgets.QTableWidgetItem(str(data_data[i, liste_domaine[j]])))

    def refresh_tabular_cat(self):
        # Refreshes the categorical tabular view with data from the specified table

        # Check if there is a table to read
        if self.tab_to_read == "":
            print("nothing to read")
            return


        # Initialize lists for domain and index variables
        liste_domaine = []
        liste_index_var_cat = []

        # Clear existing data from the categorical table widget
        self.tablewidget_math_set_cat.clear()
        self.tablewidget_math_set_cat.setRowCount(0)
        self.tablewidget_math_set_cat.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Load data from the specified table
        data_data = Orange.data.Table(self.tab_to_read)

        # Check if the dataset is None
        if data_data is None:
            print("dataset = None")
            return

        # Extract index of categorical variables
        for element in data_data.domain:
            if type(element).__name__ == "DiscreteVariable":
                liste_index_var_cat.append(data_data.domain.index(element))

        # Filter and permute columns based on categorical variables
        data_data = Table_management.filter_and_permutate_column_variable(data_data, liste_index_var_cat)

        # Populate categories dictionary with variable values
        for element in data_data.domain:
            assert type(element).__name__ == "DiscreteVariable"
            if self.categories.get(element.name) is None:
                self.categories[element.name] = [value for value in element.values]

        # Set column count in the categorical table widget
        self.tablewidget_math_set_cat.setColumnCount(len(data_data.domain))

        # Populate horizontal header with variable names
        compteur = 0
        for element in data_data.domain:
            self.tablewidget_math_set_cat.setHorizontalHeaderItem(compteur, QtWidgets.QTableWidgetItem(element.name))
            compteur += 1
            liste_domaine.append(element.name)

        # Insert a row for data type information
        header = self.tablewidget_math_set_cat.horizontalHeader()
        row = self.tablewidget_math_set_cat.rowCount()
        self.tablewidget_math_set_cat.insertRow(row)
        compteur = 0

        # Populate the data type information in the last inserted row
        for element in data_data.domain:
            self.tablewidget_math_set_cat.setItem(row, compteur, QtWidgets.QTableWidgetItem(type(element).__name__))
            compteur += 1

        # Populate the categorical table widget with data
        for i in range(len(data_data)):
            row = self.tablewidget_math_set_cat.rowCount()
            self.tablewidget_math_set_cat.insertRow(row)
            for j in range(len(data_data.domain)):
                self.tablewidget_math_set_cat.setItem(row, j,
                                                      QtWidgets.QTableWidgetItem(str(data_data[i, liste_domaine[j]])))

    def refresh_label(self):
        # Refreshes the label to display the path to the Orange data table (tab)

        if self.tab_to_read == "":
            self.label_show_link_to_tab.setText("Path to Orange data table (tab)")
        else:
            # Check if the specified file exists
            if os.path.isfile(self.tab_to_read):
                self.label_show_link_to_tab.setText(self.tab_to_read)
            else:
                self.label_show_link_to_tab.setText("Path to Orange data table (tab)")

        # Return from the method
        return

    def select_tabfile(self):
        # Selects a tab file, duplicates it, and updates the label

        # Prompt user to select a tab file
        fichier_in = WrapMessageBox.get_file_windows(self, "*.tab")

        # Check if no file is selected
        if fichier_in == "":
            return

        # Set the path to the tab file
        self.tab_to_read = MetManagement.current_met_directory(self) + "/input_met.tab"

        # Load data from the selected tab file
        la_data = Orange.data.Table(fichier_in)

        # Check if the loaded data is None
        if la_data is None:
            return

        # Check if the loaded data is empty
        if la_data == []:
            return

        # Save the duplicated tab file
        la_data.save(self.tab_to_read)

        # Refresh the label to display the new tab file path
        self.refresh_label()

    def load_data(self):
        # Loads data from the specified tab file and sends it through the Outputs.data signal

        print("on load!!!")
        self.LoadAndUpdateMetFile()
        # Check if a tab file is selected
        if self.tab_to_read == "":
            self.error("you need to select a tab file")
            self.Outputs.data.send(None)
            return

        # Check if the selected tab file exists
        if not os.path.isfile(self.tab_to_read):
            self.error("input file doesn't exist")
            self.Outputs.data.send(None)
            return

        # Clear any previous error messages
        self.error("")

        # Load data from the tab file
        self.data = Orange.data.Table(self.tab_to_read)

        # Send the loaded data through the Outputs.data signal
        self.Outputs.data.send(self.data)

        print("Loaded ")


if __name__ == "__main__":
    # This section allows obtaining a relative path for the files to open
    mod_path = Path(__file__).parent.parent

    # Set the current Open Workflows (OW) file path
    shared_variables.current_ows = os.path.dirname(__file__) + "/dataset_devellopper/fakeows.ows"

    # Import necessary modules
    from AnyQt.QtWidgets import QApplication

    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create an instance of the subworkflow_output class
    mon_objet = subworkflow_input()

    # Show the subworkflow_output widget
    mon_objet.show()

    # Handle new signals for the widget
    mon_objet.handleNewSignals()

    # Start the application event loop
    app.exec_()

