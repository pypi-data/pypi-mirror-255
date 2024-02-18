#https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html
import ctypes
import os
import sys
import time
import Orange.data
from Orange.widgets import widget
from kernel_function import Utils_box
import shared_variables, shared_functions, MetManagement
#from kernel_function import Utils_box
#from Orange.widgets.dev_workflow import shared_variables, shared_functions, MetManagement

from Orange.widgets.utils.signals import Input, Output
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QSize

#widget.OWWidget
from PyQt5.QtGui import QIcon


class OrangeSubWorflow(widget.OWWidget):
    refresh_signal = pyqtSignal()
    name = "orange_sub_workflow"
    description = "Call an other sub workflow Orange"
    icon = "icons/workflow.svg"
    priority = 1
    script_directory=os.path.dirname(os.path.abspath(__file__))
    want_control_area = False
    want_main_area = True
    run_ows=""
    concurrent_python=""
    main_tab=[]
    ## fin de la partie executee a l ouverture d Orange
    class Inputs:
        data_in = Input("Data", Orange.data.Table)# le flux d entree va s'appeler data sur le trait dans Orange

    class Outputs:
        data_out = Output("Data", Orange.data.Table,auto_summary=False)# le flux de sortie va envoyer le nom du fichier
        object = Output("Value", Orange.data.Value,auto_summary=False)# le flux de sortie va d appeler Data sur le trait d Orange
    # c est ce decorateur qui est appelle lorsque l on recoit de la donnee

    @Inputs.data_in
    def set_data(self, dataset):
        if dataset is None:
            self.error("no input data")
            self.send(None)
        self.error("")
        if self.transform_tab_to_file!= "":
            dataset.save(self.transform_tab_to_file)
            if self.run_in_Orange==False:
                self.subworkflow_cmd_line()
                return
            self.subworkflow_in_orange()
            return

        else:
            print("no data-> maybe an error")

    def update_metdir(self):
        tab_out_title=[]
        tab_out_value=[]
        tab_out_title.append("OwsToCall")
        tab_out_value.append(str(self.run_ows))
        if 0!= MetManagement.write_met_file(self,tab_out_title,tab_out_value):
            print("error writing ows file ", str(self.captionTitle))
            self.error("error writing ows file ", str(self.captionTitle))
            return

    def load_update_metdir(self):
        tab_out_title=[]
        tab_out_value=[]
        if MetManagement.is_caption_file_exist(self,str(self.captionTitle)):
            if 0!= MetManagement.read_met_file_from_caption(self,str(self.captionTitle),tab_out_title,tab_out_value):
                print("error reading loading ",str(self.captionTitle))
                self.error("error reading loading ",str(self.captionTitle))
                return self.update_metdir()
            if len(tab_out_title)!=4:
                print("error number of element in  ",str(self.captionTitle))
                self.error("error number of element in ",str(self.captionTitle))
                return self.update_metdir()
            self.run_ows=tab_out_value[3]
        return self.update_metdir()

    def __init__(self):
        super().__init__()
        shared_functions.setup_shared_variables(self)
        self.refresh_signal.connect(self.refresh_canvas)
        self.result_score=False
        self.received_output_data=False
        self.main_tab.append("")
        self.main_tab.append("")
        self.main_tab.append("")
        self.main_tab.append("")
        self.main_tab.append("")
        self.transform_tab_to_file= ""
        self.transform_file_to_tab= ""
        self.run_in_Orange=False
        active_python=sys.executable
        py_dir=os.path.dirname(active_python)
        py_exe=os.path.basename(active_python)
        if py_exe=="pythonw.exe":
            py_exe="python.exe"
        if py_exe == "pythonw":
            py_exe = "python"

        self.active_python=py_dir+"/"+py_exe
        self.active_python.replace("\\","/")

        self.main_tab[0]= "python to use -> " + active_python
        uic.loadUi(self.script_directory + '/widget_designer/orange_sub_workflow.ui', self)


        self.setAutoFillBackground(True)
        self.checkBox_launchinOrangeGui=self.findChild(QtWidgets.QCheckBox, 'checkBox_launchinOrangeGui')
        self.checkBox_launchinOrangeGui.clicked.connect(self.launch_in_Orange_Gui_on_checked)
        self.pushButton_select_ows = self.findChild(QtWidgets.QPushButton, 'pushButton_select_ows')
        self.pushButton_select_ows.clicked.connect(self.chose_ows)
        self.label_show_link_to_ows= self.findChild(QtWidgets.QLabel, 'label')
        self.plainTextEdit=self.findChild(QtWidgets.QPlainTextEdit,'plainTextEdit')

        self.push_button = self.findChild(QtWidgets.QPushButton, 'pushButton_show_hkh_website')
        self.push_button.setIcon(QIcon(self.script_directory + '/icons/Logo_HKH.svg'))
        self.push_button.setIconSize(QSize(65, 65))
        self.push_button.clicked.connect(shared_functions.openlink)
        self.load_update_metdir()
        if self.run_ows!="":
            self.validate_OWS_input_output()
        self.reload_label()
        MetManagement.force_save(self)
        self.Outputs.object.send(self.captionTitle)

    def launch_in_Orange_Gui_on_checked(self,bool_value):
        self.run_in_Orange=bool_value
        alert_manager=False
        if self.run_in_Orange:
            alert_manager=True
            for i in range(len(shared_variables.vect_doc_ptr)):
                if shared_variables.vect_doc_ptr[i][0] == self.run_ows:
                    alert_manager=False
                    break
        if alert_manager:
            if Utils_box.create_message_box_question_yes_no("WARNING: The file " + self.run_ows + " is not open, which will cause a crash if we execute the module without opening it. Do you want to open it?"):
                ctypes.cast(shared_variables.ptr_current_canvas_main, ctypes.py_object).value.open_scheme_file(self.run_ows)

    def validate_OWS_input_output(self):
        self.Outputs.object.send(self.captionTitle)
        self.main_tab[3] = ""
        self.main_tab[4] = ""

        if not self.run_ows:
            return

        ows_dir_of_ows_file = f"{self.run_ows[:-3]}metdir"

        if not os.path.isdir(ows_dir_of_ows_file):
            self.main_tab[3] = "No input data in the OWS"
            self.main_tab[4] = "No output data in ows"
            self.transform_tab_to_file = ""
            self.transform_file_to_tab = ""
            return

        response_input_tab = []
        response_output_tab = []

        for file in os.listdir(ows_dir_of_ows_file):
            if file.endswith('.met'):
                if file[:-4] == "dict_variable":
                    continue
                tab_out_title = []
                tab_out_value = []
                if 0 != MetManagement.read_met_file_from_absolute_path(os.path.join(ows_dir_of_ows_file, file), tab_out_title, tab_out_value):
                    continue
                if tab_out_value[1] == "subworkflow_input":
                    response_input_tab.append(os.path.join(ows_dir_of_ows_file, file))
                if tab_out_value[1] == "orange_sub_workflow":
                    response_output_tab.append(os.path.join(ows_dir_of_ows_file, file))

        if len(response_input_tab) == 0:
            self.main_tab[3] = f"Warning!! No input data in ows of {ows_dir_of_ows_file}"
            self.transform_tab_to_file = ""

        elif len(response_input_tab) == 1:
            self.main_tab[3] = f"OK -> One input data in ows {response_input_tab[0]}"
            self.transform_tab_to_file = os.path.join(ows_dir_of_ows_file, "input_met.tab")
            tab_out_title = []
            tab_out_value = []
            if 0 != MetManagement.read_met_file_from_absolute_path(response_input_tab[0], tab_out_title, tab_out_value):
                print("Error reading ", response_input_tab[0])
                self.transform_tab_to_file = ""

            tab_out_value[3] = "input_met.tab"

            try:
                with open(response_input_tab[0], 'w') as f:
                    for i in range(len(tab_out_title)):
                        f.write(f'"{tab_out_title[i]}" "{tab_out_value[i]}"')
                        if i != len(tab_out_title) - 1:
                            f.write("\n")
                f.close()
            except Exception as e:
                print(e, file=sys.stderr)
                print(f"Error in file : {response_input_tab[0]}", file=sys.stderr)
                return
        else:
            self.main_tab[3] = f"Error!! Several inputs data in =({len(response_input_tab)}) -> Ignoring input data updating"
            self.transform_tab_to_file = ""

        if len(response_output_tab) == 0:
            self.main_tab[4] = f"Warning!! No output data ows in {ows_dir_of_ows_file}"
            self.transform_file_to_tab = ""
        elif len(response_output_tab) == 1:
            self.main_tab[4] = f"OK -> One output data in ows {response_output_tab[0]}"
            self.transform_file_to_tab = os.path.join(ows_dir_of_ows_file, "output_met.tab")

            tab_out_title = []
            tab_out_value = []

            if 0 != MetManagement.read_met_file_from_absolute_path(response_output_tab[0], tab_out_title, tab_out_value):
                print("Error ", response_output_tab[0])
                self.transform_file_to_tab = ""

            tab_out_value[3] = self.transform_file_to_tab

            try:
                with open(response_output_tab[0], 'w') as f:
                    for i in range(len(tab_out_title)):
                        f.write(f'"{tab_out_title[i]}" "{tab_out_value[i]}"')
                        if i != len(tab_out_title) - 1:
                            f.write("\n")
                f.close()
            except Exception as e:
                print(e, file=sys.stderr)
                print(f"Error in writing file : {response_input_tab[0]}", file=sys.stderr)
                return
        else:
            self.main_tab[4] = f"Error!! Several outputs data in =({len(response_output_tab)}) -> Ignoring output data updating"
            self.transform_file_to_tab = ""

    def reload_label(self):
        # Check if the path to OWS is empty
        if self.run_ows == "":
            self.label_show_link_to_ows.setText("Path to OWS")
        else:
            # Set the label to display the path to the OWS
            self.label_show_link_to_ows.setText(self.run_ows)
        # Update the information in the main_tab about the OWS file
        self.main_tab[1] = "OWS file is: " + self.run_ows
        # Check if the length of the OWS path is greater than 4
        if len(self.run_ows) > 4:
            # Check if the corresponding metdir directory exists
            if not os.path.isdir(self.run_ows[:-3] + "metdir"):
                # Display a warning if the directory doesn't exist
                self.main_tab[2] = "Warning: OWS directory does not exist for the chosen OWS file"
                print("Error: The OWS directory does not exist")
            else:
                # Update main_tab indicating that the OWS directory is found
                self.main_tab[2] = "OWS directory found"
        text=""
        for element in self.main_tab:
            text+=str(element)+"\n"
        self.plainTextEdit.setPlainText(text)
        self.update_metdir()
        self.Outputs.object.send(self.captionTitle)


    def chose_ows(self):
        self.run_ows=Utils_box.get_file_windows(self,"*.ows")
        self.validate_OWS_input_output()
        self.reload_label()
        self.Outputs.object.send(self.captionTitle)

    def subworkflow_cmd_line(self):
        # Check if an OWS is selected
        if not self.run_ows:
            self.error("You need to select an OWS")
            return
        # Clear any previous error messages
        self.error("")
        # Append "cmd_line" to shared variables indicating subworkflow execution
        shared_variables.ptr_master_external_orange.append("cmd_line")
        shared_variables.ptr_master_external_orange.pop()
        # Check if transformation from file to tab is specified
        if self.transform_file_to_tab:
            # Convert file to Orange Table
            data_data = Orange.data.Table(self.transform_file_to_tab)
            # Send the resulting data to the specified output
            self.Outputs.data_out.send(data_data)

    def refresh_canvas(self):
        ctypes.cast(self.refresh_id, ctypes.py_object).value.set_signal_freeze(True)
        ctypes.cast(self.refresh_id, ctypes.py_object).value.set_signal_freeze(False)


    def subworkflow_in_orange(self):
        self.result_score = False
        self.received_output_data = False

        if not self.run_ows:
            self.error("You need to select an ows")
            return

        liste_input = MetManagement.get_all_captions_with_specific_class(ClassName="subworkflow_input", ows_path=self.run_ows)

        self.error("")

        if len(liste_input) != 1:
            self.error("Number of inputs is not equal to 1")
            print("Number of inputs is not equal to 1", file=sys.stderr)
            return

        absolute_path_of_owsfiletoread = f"{self.run_ows[:-3]}metdir/{liste_input[0]}.met"

        tab_out_title = []
        tab_out_value = []

        if 0 != MetManagement.read_met_file_from_absolute_path(absolute_path_of_owsfiletoread, tab_out_title, tab_out_value):
            print(f"Error reading {absolute_path_of_owsfiletoread}", file=sys.stderr)
            self.error(f"Error reading {absolute_path_of_owsfiletoread}")
            print(f"Error reading {absolute_path_of_owsfiletoread}", file=sys.stderr)
            return

        refresh_id = -333

        for i, (ows, doc_id) in enumerate(shared_functions.vect_doc_ptr):
            if ows == self.run_ows:
                refresh_id = doc_id
                break

        if refresh_id == -333:
            self.error("You need to open ows before!")
            return

        print("On ajoute le ptr du widget")
        shared_functions.ptr_master_external_orange.append(str(id(self)))
        execute_data_id = tab_out_value[2]

        ctypes.cast(int(execute_data_id), ctypes.py_object).value.load_data()
        time.sleep(2)

        self.refresh_id = int(refresh_id)
        self.refresh_signal.emit()
        ctypes.cast(refresh_id, ctypes.py_object).value.set_signal_freeze(True)
        ctypes.cast(refresh_id, ctypes.py_object).value.set_signal_freeze(False)

        test = 0
        while True:
            ctypes.cast(int(execute_data_id), ctypes.py_object).value.load_data()
            time.sleep(0.5)
            test += 1
            print("Wait for sub ows")
            if test == 5:
                print("test timeout")
                break
            if self.received_output_data:
                print("Data reçue")
            if self.result_score:
                print("Score reçu")
                if self.received_output_data:
                    print("Sub ows finished")
                    break
        self.result_score = False
        self.received_output_data = False
        shared_functions.ptr_master_external_orange.pop()

