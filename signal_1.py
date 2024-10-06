# signal.py
import pandas as pd
from PyQt5.QtWidgets import QFileDialog

class SignalProcessor:
    def __init__(self):
        self.data = None
        self.current_index = 0
    
    def open_file(self, parent_widget):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        
        if file_path:
            # Read CSV file
            df = pd.read_csv(file_path)
            self.data = df.values.flatten()
            self.current_index = 0
    
    def get_next_data(self, window_width):
        if self.data is not None:
            if self.current_index + window_width <= len(self.data):
                data_segment = self.data[self.current_index:self.current_index + window_width]
                self.current_index += 1  # Adjust for slower scrolling
                return data_segment
            else:
                return None
