import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import pyqtgraph as pg

class SignalProcessor:
    def __init__(self, graph_widget):
        self.data = None
        self.plot_widget = graph_widget
        self.plot_data_item = self.plot_widget.plot()
        self.current_index = 0

    def open_file(self, parent_widget):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Open CSV File", "", "CSV Files (*.csv)", options=options)
    
        if file_path:
            df = pd.read_csv(file_path)
            self.emgx = df.iloc[:, 0].to_numpy()
            self.emgy = df.iloc[:, 1].to_numpy()
            self.data = self.emgy  # Use y-data for scrolling
            self.current_index = 0
            self.total_length = len(self.data)

    def get_next_data(self, window_width):
        if self.data is not None:
            if self.current_index + window_width <= len(self.data):
                data_segment = self.data[self.current_index:self.current_index + window_width]
                self.current_index += 1  # Increment by 1 for smooth scrolling
                return data_segment
            else:
                self.current_index = 0  # Reset to loop the signal
                return None

    
    # def generate_signal(self, x):
    #     ecg = np.sin(1.7*np.pi*x)
    #     ecg += 0.5 * np.sin(3.7 * np.pi *x)
    #     ecg += 0.2 * np.sin(0.7 * np.pi * x)
    #     return ecg


    
    # def get_next_data(self, window_width, x_data, y_data):
    #     self.plot_data_item.setXRange(self.x_data[self.current_index] - window_width, self.x_data[self.current_index])
    #     self.current_index += 1
    #     y_new = self.generate_signal(self.x + self.current_index)
    #     self.plot_widget