import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from view import View
from model import Model
from nerUtilities import NerUtilities
import logging


class Controller:
    
    #region Ctor
    def __init__(self):
        """
        constructor
        """
        self.model = Model()        
        self.backend = NerUtilities()        
        self.init()              

    widgets = {
    "input":[], 
    "buttons": [],
    "labels":[]   
    }  
    #endregion Ctor
    #region GUI  

    def init(self):
        """
        init application
        """
        logging.basicConfig(filename='NerSystem.log', format='%(asctime)s %(message)s', filemode='a')    
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Start NER application")       
        #load dictionaries for rule-based NER
        dict_510k, dict_PMA, dict_estab_reg = self.model.load_dictionaries()
        self.backend.init(dict_510k, dict_PMA, dict_estab_reg)     
        self.path_to_model = self.model.read_settings("model_path") 
        self.backend.remove_wrong_concepts = self.model.read_settings("remove_wrong_concepts") 
        self.backend.wrong_concepts = self.model.load_wrong_concepts()
        self.backend.is_strict_eval = self.model.read_settings("is_strict_eval")          
        self.backend.is_ener = self.model.read_settings("is_ener")
        self.transformer = self.model.load_model() 

        #build application
        app = QApplication(sys.argv)        
        window = QWidget()        
        View.setup_window(window)   
        self.grid = QGridLayout()
        View.setup_grid(window, self.grid)
        self.create_main_frame()
        window.show()
        sys.exit(app.exec())       
      
    
    def clear(self):
        """
        delete all widgets        
        """
        for widget in self.widgets:
            if self.widgets[widget] != []:
                items = self.widgets[widget]
                for item in items:
                    item.hide()
                for i in range(0, len(self.widgets[widget])):
                    self.widgets[widget].pop()

    def create_main_frame(self):  
        self.logger.debug("Creating main frame")      
        self.clear() 
        #intro label
        intro_label = QLabel()
        View.setup_intro_label(intro_label, "Please select a task:")    
        self.widgets["labels"].append(intro_label) 
        self.grid.addWidget(self.widgets["labels"][-1], 0, 0) 

        #ner task button
        ner_task = QPushButton("NER task")
        View.setup_task_button(ner_task)   
        ner_task.clicked.connect(self.create_ner_frame) 
        self.widgets["buttons"].append(ner_task) 
        self.grid.addWidget(self.widgets["buttons"][-1], 0, 1)  

        eval_task = QPushButton("NER Evaluation")
        View.setup_task_button(eval_task)         
        eval_task.clicked.connect(self.create_eval_frame) 
        self.widgets["buttons"].append(eval_task) 
        self.grid.addWidget(self.widgets["buttons"][-1], 0, 2) 

    def create_ner_frame(self):
        self.logger.debug("Creating NER frame")      
        self.clear()   
        #intro label
        intro_label = QLabel()
        View.setup_intro_label(intro_label, "Please enter text data to start NER")    
        self.widgets["labels"].append(intro_label) 
        self.grid.addWidget(self.widgets["labels"][-1], 0, 0) 

        #blank label
        blank_label = QLabel() 
        self.widgets["labels"].append(blank_label)   
        self.grid.addWidget(self.widgets["labels"][-1], 1, 1)  

        #select file label
        select_label = QLabel()
        View.setup_select_label(select_label)         
        self.widgets["labels"].append(select_label) 
        self.grid.addWidget(self.widgets["labels"][-1], 2 , 0)  

        #select file button
        select_button = QPushButton("Select")
        View.setup_task_button(select_button)       
        select_button.clicked.connect(self.ner_dialog) 
        self.widgets["buttons"].append(select_button) 
        self.grid.addWidget(self.widgets["buttons"][-1], 2, 1)  
       
        #input field
        input_field = QPlainTextEdit()  
        View.setup_input_field(input_field)          
        self.widgets["input"].append(input_field) 
        self.grid.addWidget(self.widgets["input"][-1], 3, 1) 

        #back button
        back_button = QPushButton("Back")
        View.setup_start_back_button(back_button, True)
        back_button.clicked.connect(self.create_main_frame)           
        self.widgets["buttons"].append(back_button) 
        self.grid.addWidget(self.widgets["buttons"][-1], 4, 0)  

        #start ner button
        start_ner_button = QPushButton("Start")
        View.setup_start_back_button(start_ner_button, True) 
        start_ner_button.clicked.connect(self.start_ner)          
        self.widgets["buttons"].append(start_ner_button) 
        self.grid.addWidget(self.widgets["buttons"][-1], 4, 2) 

        #check if a model for NER selected
        error_message = "Transformer model for NER is not defined in settings.json"
        if self.path_to_model == "":
            input_field.appendPlainText(error_message)
            start_ner_button.setEnabled(False)
        else:
            input_field.clear()
            start_ner_button.setEnabled(True)


    def create_eval_frame(self):    
        self.logger.debug("Creating Evaluation frame")       
        self.clear()   
        #intro label
        intro_label = QLabel()
        View.setup_intro_label(intro_label, "Please enter text data to start NER Evaluation")       
        self.widgets["labels"].append(intro_label)
        self.grid.addWidget(self.widgets["labels"][-1], 0, 0) 

        #blank label
        blank_label = QLabel()
        self.widgets["labels"].append(blank_label)
        self.grid.addWidget(self.widgets["labels"][-1], 1, 1)    

        #select file label
        select_label = QLabel()
        View.setup_select_label(select_label)           
        self.widgets["labels"].append(select_label)
        self.grid.addWidget(self.widgets["labels"][-1], 2, 0)    

        #select file dialog
        select_button = QPushButton("Select")
        View.setup_task_button(select_button)                   
        select_button.clicked.connect(self.eval_dialog) 
        self.widgets["buttons"].append(select_button)    
        self.grid.addWidget(self.widgets["buttons"][-1], 2, 1) 

        #input field
        input_field = QPlainTextEdit()   
        input_field.clear()        
        View.setup_input_field(input_field)          
        self.widgets["input"].append(input_field)   
        self.grid.addWidget(self.widgets["input"][-1], 3, 1)         

        #back button
        back_button = QPushButton("Back")
        View.setup_start_back_button(back_button, True)                 
        back_button.clicked.connect(self.create_main_frame)         
        self.widgets["buttons"].append(back_button) 
        self.grid.addWidget(self.widgets["buttons"][-1], 4, 0)  

        #start eval button
        start_ner_button = QPushButton("Start")
        View.setup_start_back_button(start_ner_button, True)  
        start_ner_button.clicked.connect(self.start_eval)         
        self.widgets["buttons"].append(start_ner_button) 
        self.grid.addWidget(self.widgets["buttons"][-1], 4, 2)  

        #check if a model for NER selected
        error_message = "Transformer model is not defined in settings.json"
        if self.path_to_model == "":
            input_field.appendPlainText(error_message)
            start_ner_button.setEnabled(False)
        else:
            input_field.clear()
            start_ner_button.setEnabled(True) 

        #check if an eval method selected
        error_message_2 = "Parameter is_strict_eval is not defined in settings.json \nSelect value \"true\" or \"false\""
        if self.backend.is_strict_eval not in ["true", "false"]:
            input_field.appendPlainText(error_message_2)
            start_ner_button.setEnabled(False)
        else:
            input_field.clear()
            start_ner_button.setEnabled(True) 
    #endregion GUI
    #region NER
    def ner_dialog(self):
        """
        open a window to select a TXT file
        """
        file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()", ".\storage\pubmed texts", "Text Files (*.txt)")        
        if check:
            self.year  = self.model.determine_text_year(file)
            if self.year == 0:
                self.logger.warning("Publication year not found in the vocabulary, recognition of Emerging NEs  will not be run")  
                self.backend.is_ener = "false"
            if self.widgets["input"] != []:
                View.display_text(self.widgets, file)
            
    def start_ner(self):  
        self.logger.debug("Start NER") 
        error_message = "Fail to start NER. Text field is empty."  
        if self.widgets["input"] != []:
            input_field = self.widgets["input"][-1]
            file_path = input_field.toPlainText()
            with open(file_path, encoding="utf8") as f:
                text = f.read()
                if text == "":
                    self.logger.error(error_message) 
                    input_field.appendPlainText(error_message) 
                    return
                if text == error_message:
                    return                   
                doc = self.backend.run_ner(self.transformer, text, self.year) 
                if doc == None:
                    self.logger.error("Something went wrong with NER. Failed to create an NLP document")                 
                else:
                    file_name = file_path.split('/')[-1]
                    html_path = self.model.write_html(doc, file_name)   
                    View.show_results(html_path)   
            self.logger.debug("done")     
    #endregion NER
    #region Evaluation
    def eval_dialog(self):
        """
        open a window to select a JSON-file
        """       
        #path to the file
        file , check = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",".\storage\\test data", "JSON files (*.json)")   
        if check:   
            self.year  = self.model.determine_text_year(file)     
            if self.year == 0:               
                self.logger.debug("Publication year not available")                  
            View.display_text(self.widgets, file)  
    
    def start_eval(self):
        """
        evaluate a model
        """       
        self.logger.debug("Start NER-Evaluation") 
        self.logger.debug("Settings: model [{}], use filter [{}], strict eval [{}], find eNER [{}]".format(self.path_to_model, self.backend.remove_wrong_concepts, self.backend.is_strict_eval, self.backend.is_ener) )
        error_message = "Fail to start NER evaluation. Text field is empty." 
        if self.widgets["input"] != []:
            input_field = self.widgets["input"][-1]
            json_file = input_field.toPlainText()
            if json_file == "":
                self.logger.error(error_message) 
                input_field.appendPlainText(error_message)
                return  
            if json_file == error_message:
                self.logger.error("stop evaluating")
                return  

            #evaluate the model with a single file
            self.logger.debug("File with data: " + json_file) 
            if not json_file.endswith("all_data.json"):                
                json_content = self.model.load_content(json_file)
                #run eval            
                content = str(json_content) 
                if content == "":
                    input_field.appendPlainText(error_message)
                    return 
                if content == error_message:
                    return                   
                doc, results = self.backend.run_eval(json_content, self.transformer, self.year) 
                self.logger.debug("Found entities: [{}]".format(doc.ents))
                self.logger.debug(result)
                if doc != None:                    
                    html_path = self.model.write_eval_html(doc, results, json_file) 
                    View.show_results(html_path) 
                    return
            #run evaluation with all test data
            else:
                all_texts = self.model.get_all_texts(json_file)    
                #help variables to count metrics for all test data
                mt_prec = 0     #medTech precision
                mt_rec = 0      #medTech recall   
                mt_f1 = 0       #medTech f1
                emt_prec = 0    #eMedTech precision
                emt_rec = 0     #eMedTech recall
                emt_f1 = 0      #eMedTech f1
                all_prec = 0    #medTech + eMedTech precision
                all_rec = 0     #medTech + eMedTech recall
                all_f1 = 0      #medTech + eMedTech f1
                counter = 0
                for f in all_texts:
                    #ignore the empty file
                    if f.endswith("all_data.json"):
                        continue
                    self.logger.debug("TEXT ID: {}".format(f))                
                    json_content = self.model.load_content(f)                    
                    if(json_content == ""):
                        self.logger.debug("file {} is empty".format(f))                        
                        continue
                    counter += 1
                    self.year  = self.model.determine_text_year(f)
                    if self.year == 0:
                        self.logger.debug("Publication year not available. Recognition of eNEs won't be run")                          
                        self.backend.is_ener = "false"
                    doc, results = self.backend.run_eval(json_content, self.transformer, self.year)
                    self.logger.debug("Found entities: [{}]".format(doc.ents))
                    self.logger.debug(results)                    
                    #read eval. results
                    total = (results["ents_p"], results["ents_r"], results["ents_f"])
                    per_type = results["ents_per_type"]
                    med_tech = (0, 0, 0, 0)
                    emed_tech = (1, 1, 1, 1)
                    if per_type != None:
                        for key in per_type:
                            vals = per_type[key]
                            result = (vals["p"], vals["r"], vals["f"])
                            if key == "MedTech":
                                med_tech = result
                            else:
                                emed_tech = result
                    #medTech results            
                    mt_prec += med_tech[0]
                    mt_rec += med_tech[1]
                    mt_f1 += med_tech[2]

                    #eMedTech results
                    if self.backend.is_ener == "true":
                        emt_prec += emed_tech[0]
                        emt_rec += emed_tech[1]
                        emt_f1 += emed_tech[2]
                    else:
                        emt_prec = "-"
                        emt_rec = "-"
                        emt_f1 = "-"

                    
                    #medTech + eMedTech results
                    if total[0] != None:
                        all_prec += total[0]
                        all_rec += total[1]
                        all_f1 += total[2]

                total_medtech = (mt_prec, mt_rec, mt_f1)
                total_e_medtech = (emt_prec, emt_rec, emt_f1)
                if self.backend.is_ener == "true":
                    total_all = (all_prec, all_rec, all_f1)
                else:
                    total_all = (mt_prec, mt_rec, mt_f1)

                html_path = self.model.write_total_eval_html(total_medtech, total_e_medtech, total_all, counter) 
                View.show_results(html_path) 

#endregion Evaluation
                
if __name__ == '__main__':
    c = Controller()
    

 


    