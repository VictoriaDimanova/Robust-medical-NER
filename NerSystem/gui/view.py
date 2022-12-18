from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import webbrowser

class View:
           
    @staticmethod
    def setup_window(window):
        window.setWindowTitle("Medical NER")
        window.setFixedWidth(1300)
        window.setFixedHeight(500)
        window.setStyleSheet("background: #cccccc;")
        window.move(300, 100)

    @staticmethod
    def setup_grid(window, grid):
        window.setLayout(grid)
        grid.setContentsMargins(10,10,10,10)

    @staticmethod
    def setup_task_button(button):
        button.setStyleSheet(
            "*{border: 4px solid '#7f7979';" + 
            "border-radius: 35px;" +
            "font-size: 25px;" + 
            "color: '#595959';}" + 
            "*:hover{background:'#9a8c98';}")
        button.resize(100,32)

    @staticmethod
    def setup_intro_label(label, text):
        label.setText(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(      
            "font-size: 25px;" + 
            "color: '#d8572a';" )
        label.move(10, 10)

    @staticmethod
    def setup_select_label(label):
        label.setText("Select a file with a text:")
        label.setStyleSheet(      
            "*{font-size: 20px;" + 
            "color: '#595959';}")    
     

    @staticmethod
    def setup_input_field(field):
        field.setStyleSheet(
            "*{border: 4px solid '#7f7979';" + 
            "font-size: 20px;" +       
            "color: 'black';" +
            "border-color: '#7f7979';}")
        field.setDisabled(True)
        

    @staticmethod
    def setup_start_back_button(button, enabled: bool):        
        button.setStyleSheet(
            "*{border: 2px solid '#540d6e';" + 
            "border-radius: 25px;" +
            "font-size: 25px;" + 
            "color: '#540d6e';" + 
            "font-family: Arial;}" +
            "*:hover{background:'#540d6e'; color: '#cccccc';}") 
        button.setEnabled(enabled)
    
    @staticmethod
    def display_text(widgets, text):
        """
        display text in the input field
        """
        if widgets["input"] != []:
            input_field = widgets["input"][-1]
            input_field.clear()
            input_field.appendPlainText(text)

    @staticmethod
    def show_results(path:str):
        webbrowser.open(path)   


    


   

    
    
    
