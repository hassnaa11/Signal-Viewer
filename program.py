from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
import json
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer  # For QTimer
from PyQt5.QtWidgets import QGridLayout  # For QGridLayout

import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from signal_1 import SignalProcessor
from graph import Graph
#import pyedflib
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()
        self.ui.graph1Widget.graph.setLimits(xMin=0)
        self.ui.graph2Widget.graph_2.setLimits(xMin=0)
        self.ui.graph1Widget_3.graph.setLimits(xMin=0)


        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        
        # Set up the timer for updating the graph
        # self.timer.timeout.connect(self.update_graphs)
        
        self.window_width = 100 
        self.graph1_on = True
        self.graph2_on = True
        self.first_graph_online_connected = False
        self.second_graph_online_connected = False
        self.plot_online_curve_graph1 = self.ui.graph1Widget.graph.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.plot_online_curve_graph2 = self.ui.graph2Widget.graph_2.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.ui.connect_online_button_graph_1.clicked.connect(self.update_online_plot)
        self.ui.connect_online_button_graph_2.clicked.connect(self.update_online_plot)
        self.ui.play_button_graph_1.clicked.connect(self.stop_run_graph)
        self.ui.play_button_graph_2.clicked.connect(self.stop_run_graph)
        self.timer.start(1000)


    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str


    def update_online_plot(self):
        sender_button = self.sender()
        print(sender_button)
        if sender_button != self.ui.connect_online_button_graph_1 and  sender_button != self.ui.connect_online_button_graph_2: # No new click
            sender_button = self.last_sender
        elif (sender_button == self.ui.connect_online_button_graph_1) and self.graph1_on: # clicked on connect_online_button_graph_1
            self.timer.timeout.connect(self.update_online_plot)
            self.last_sender = sender_button
            self.first_graph_online_connected = True
        elif (sender_button == self.ui.connect_online_button_graph_2) and self.graph2_on: # clicked on connect_online_button_graph_2
            self.timer.timeout.connect(self.update_online_plot)
            self.last_sender = sender_button 
            self.second_graph_online_connected = True      
            
        try:
            # Read and process the JSON data
            with open("online_data.json", "r") as file:
                self.data = json.load(file)
            # Convert y-axis data to floats
            y_axis = []
            for item in self.data["Data_Y"]:
                try:
                    item = float(item.replace(",", ""))
                except ValueError:
                    item = np.nan
                y_axis.append(item)
            # Convert time strings to elapsed seconds with standardized format
            time_data = self.data["Time"]
            if len(time_data) > 0:
                time_data = [self.format_time_string(t) for t in time_data] 
                base_time = datetime.strptime(time_data[0], "%H:%M:%S")  # First timestamp as the base
                x_axis = [
                    (datetime.strptime(self.format_time_string(t), "%H:%M:%S") - base_time).total_seconds()
                    for t in time_data
                ]
            else:
                x_axis = []
                
            y_axis = np.array(y_axis, dtype=np.float64)
            x_axis = np.array(x_axis, dtype=np.float64)

            valid_indices = np.isfinite(y_axis) & np.isfinite(x_axis)
            x_axis = x_axis[valid_indices]
            y_axis = y_axis[valid_indices]

            if len(x_axis) > 0 and len(y_axis) > 0:           
                if self.graph1_on and self.first_graph_online_connected: self.plot_online_curve_graph1.setData(x_axis, y_axis)
                if self.graph2_on and self.second_graph_online_connected: self.plot_online_curve_graph2.setData(x_axis, y_axis) 
                else: print("hahaha no sender")       
        except Exception as e:
            print(f"Error loading or plotting data: {e}")
    
    def stop_run_graph(self):
        sender_button = self.sender()
        if sender_button == self.ui.play_button_graph_1:
            self.graph1_on = not self.graph1_on
            if self.graph1_on:
                self.timer.timeout.connect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                self.timer.timeout.disconnect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon1)   
        elif sender_button == self.ui.play_button_graph_2:
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                self.timer.timeout.connect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                self.timer.timeout.disconnect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon1)  

    
    def open_file_graph_1(self):
        self.signal_processor_1.open_file(self)
        self.timer.timeout.connect(self.update_graph1)

    def open_file_graph_2(self):
        self.signal_processor_2.open_file(self)
        self.timer.timeout.connect(self.update_graph2)
        
    def update_graph1(self):
        data_1 = self.signal_processor_1.get_next_data(self.window_width)
        if (data_1 is not None) and (self.graph1_on):
            self.graph_1.update_graph(data_1, self.signal_processor_1.current_index, self.window_width)
        
    def update_graph2(self): 
        data_2 = self.signal_processor_2.get_next_data(self.window_width)  
        if (data_2 is not None) and (self.graph2_on):
            self.graph_2.update_graph(data_2, self.signal_processor_2.current_index, self.window_width)
        

    # def update_graphs(self):
    #     data_1 = self.signal_processor_1.get_next_data(self.window_width)
    #     data_2 = self.signal_processor_2.get_next_data(self.window_width)

    #     if (data_1 is not None) and (self.graph1_on):
    #         self.graph_1.update_graph(data_1, self.signal_processor_1.current_index, self.window_width)
    #     else:
    #         self.timer.timeout.disconnect(self.update_graphs)   
    #     if (data_2 is not None) and (self.graph2_on):
    #         self.graph_2.update_graph(data_2, self.signal_processor_2.current_index, self.window_width)
    #     else:
    #         self.timer.timeout.disconnect(self.update_graphs)      
            
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()
