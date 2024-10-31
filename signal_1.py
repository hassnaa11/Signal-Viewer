import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import pyqtgraph as pg
class SignalProcessor:
    def __init__(self, graph_widget):
        self.data = None
        self.plot_widget = graph_widget
        self.current_index = 0
        self.signals = {}  

    def open_file(self, parent_widget):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        
        if file_path:
            df = pd.read_csv(file_path)
            self.data = df.iloc[:, 1].to_numpy()  
            self.current_index = 0
            self.total_length = len(self.data)

    def get_next_data(self, window_width):
        if self.data is not None and self.current_index + window_width <= len(self.data):
            self.current_index += 1  
            data_segment = self.data[0:self.current_index]
            return data_segment
        else:
            return None 
        
    def get_previous_data(self):
        if self.data is not None:
            data_segment = self.data[0:self.current_index]
            return data_segment
        else:
            return None  
    def get_data(self):
        return self.data
    

    def rewind_graph(self):
        self.current_index = 0  