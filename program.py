from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QInputDialog

import json
import os
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow
from non_rectangle_plot_window import nonRectanglePlotWindow
from collect_online_data import CollectOnlineData
# import subprocess

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QRubberBand,
    QFileDialog,
)
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QRubberBand,
    QFileDialog,
)
from PyQt5.QtCore import QRect, QPoint, QSize, Qt
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent
from fpdf import FPDF


from PyQt5.QtCore import QTimer  # For QTimer
from PyQt5.QtWidgets import QGridLayout  # For QGridLayout

import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as Navi,
)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as Navi,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from signal_1 import SignalProcessor
from graph import Graph
from non_rectangular import BubbleChartApp
#import pyedflib
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()
        self.ui.graph1Widget.graph.setLimits(xMin=0)
        self.ui.graph2Widget.graph_2.setLimits(xMin=0)
        self.ui.graph1Widget_3.graph.setLimits(xMin=0)
        self.images = []

        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        self.graph_3 = BubbleChartApp(self.ui.graph1Widget_3.graph)
        self.graph1_color = "w"
        self.graph2_color = "w"
        self.signal_processor1 = []
        self.signal_processor2 = []  # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2 = []

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.open_button_graph_3.clicked.connect(self.open_file_graph_3)
        self.ui.stop_button_graph_1.clicked.connect(lambda:  self.taking_snap_shot(1))
        self.ui.stop_button_graph_2.clicked.connect(lambda:  self.taking_snap_shot(2))
        self.ui.export_button.clicked.connect(self.PDF_maker)

        self.ui.signal_color_button_graph_1.clicked.connect(
            lambda: self.open_color_dialog(1)
        )
        self.ui.signal_color_button_graph_2.clicked.connect(
            lambda: self.open_color_dialog(2)
        )
        self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(
            self.update_graph_name_1
        )

        self.timer_graph_1 = QtCore.QTimer()
        # self.timer_graph_1.start(10)
        self.timer_graph_2 = QtCore.QTimer()
        # self.timer_graph_2.start(10)
        self.speed_graph_1 = 500  # Default speed in ms
        self.speed_graph_2 = 500  # Default speed in ms
        # Initialize dictionaries to store signals by name
        self.signals_graph_1 = {}
        self.signals_graph_2 = {}

        # Initialize speed sliders and connect them
        self.ui.speed_slider_graph_1.valueChanged.connect(self.set_speed_graph_1)
        self.ui.speed_slider_graph_2.valueChanged.connect(self.set_speed_graph_2)

        self.ui.move_to_graph_1_button.clicked.connect(self.move_signal_from_graph2_to_graph1)
        self.ui.move_to_graph_2_button.clicked.connect(self.move_signal_from_graph1_to_graph2)

        # Connect the checkbox state change signal to the toggle method
        # self.ui.visible_checkBox_graph_2.stateChanged.connect(lambda: self.toggle_signal_visibility(1))
        # self.ui.visible_checkBox_graph_2.stateChanged.connect(lambda: self.toggle_signal_visibility(2))

        
        # Set up the timer for updating the graph
        # self.timer.timeout.connect(self.update_graphs)
        
        self.ui.link_button.clicked.connect(self.link_graphs)
        self.ui.link_play_button.clicked.connect(self.stop_run_graph)
        self.isLinked = False

        self.is_timer_graph1_connected = False
        self.is_timer_graph2_connected = False

        self.window_width = 100
        self.graph1_on = True
        self.graph2_on = True
        self.play_both = False
        self.is_file1_opened = False
        self.is_file2_opened = False
        self.first_graph_online_connected = False
        self.second_graph_online_connected = False
        
        # Collect Online Data
        # self.collector_online = CollectOnlineData()
        # self.timer_online = QtCore.QTimer()
        # self.collector_online.data_fetched.connect(self.update_online_plot)
        
        self.plot_online_curve_graph1 = self.ui.graph1Widget.graph.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o"
        
        )
        self.plot_online_curve_graph2 = self.ui.graph2Widget.graph_2.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o"
        
        )
        self.ui.connect_online_button_graph_1.clicked.connect(self.connect_online)
        self.ui.connect_online_button_graph_2.clicked.connect(self.connect_online)

        self.ui.play_button_graph_1.clicked.connect(self.stop_run_graph)
        self.ui.play_button_graph_2.clicked.connect(self.stop_run_graph)
        self.timer2.start(1000)
        self.timer2.timeout.connect(self.graph_3.update_graph)
        
        self.ui.nonrectangle_graph_button.clicked.connect(self.show_non_rectangle_plot)
        self.timer.start(1000)

    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str
    def closeEvent(self, event):
        """Handle window close event to stop the timer"""
        self.graph_3.closeEvent(event)

    def connect_online(self):
        
        sender_button = self.sender()
        print(sender_button)
        if sender_button == self.ui.connect_online_button_graph_1 and self.first_graph_online_connected:
            print("disconnect 1")
            self.disconnect_online(sender_button)
        elif sender_button == self.ui.connect_online_button_graph_2 and self.second_graph_online_connected:
            print("disconnect 2")
            self.disconnect_online(sender_button)
         
        # elif (sender_button != self.ui.connect_online_button_graph_1 and sender_button != self.ui.connect_online_button_graph_2):  # No new click
        #     sender_button = self.last_sender
        elif (sender_button == self.ui.connect_online_button_graph_1) and self.graph1_on:  # clicked on connect_online_button_graph_1
            print("connect 1")
            self.first_graph_online_connected = True
            # collect data from the website
            
            # self.timer_online.start(2000)
            # self.timer_online.timeout.connect(self.collector_online.data_update)
            
            # if self.collector_online.running == False:  # Ensure the thread isn't already running
            #     print("Start Thread run")
            #     self.collector_online.start()  # Start the thread
           
            # self.collector_online.start()
            
            if not self.is_timer_graph1_connected:
                print("connect 1::: ", self.is_timer_graph1_connected)
                self.is_timer_graph1_connected = True
                self.timer_graph_1.start(10)
                self.timer_graph_1.timeout.connect(self.update_online_plot)
                
            self.ui.connect_online_button_graph_1.setText("Disconnect Online")
            
        elif (sender_button == self.ui.connect_online_button_graph_2) and self.graph2_on:  # clicked on connect_online_button_graph_2
            print("connect 2")
            self.second_graph_online_connected = True
            
            # collect data from the website
            # self.timer_online.start(2000)
            # self.timer_online.timeout.connect(self.collector_online.data_update)
            
            # if self.collector_online.running == False:  # Ensure the thread isn't already running
            #     print("Start Thread run")
            #     self.collector_online.start()  # Start the thread
            
            # self.collector_online.start()
                
            if not self.is_timer_graph2_connected:
                self.is_timer_graph2_connected = True
                self.timer_graph_2.start(10)
                self.timer_graph_2.timeout.connect(self.update_online_plot)
                
            self.ui.connect_online_button_graph_2.setText("Disconnect Online")    
                    
    def disconnect_online(self, button):            
        if button == self.ui.connect_online_button_graph_1:
            print("disconnecting")
            # if  self.collector_online.running == True: 
            #     print("Stop Thread graph 1")
            #     self.collector_online.stop() 
            # self.collector_online.wait()
            
            
            # self.timer_online.timeout.disconnect(self.collector_online.data_update)
            self.first_graph_online_connected = False
            self.ui.connect_online_button_graph_1.setText("Connect Online")
            # disconnect timer 1
            self.is_timer_graph1_connected = False
            self.timer_graph_1.timeout.disconnect(self.update_online_plot)
            # Clear graph 1
            self.plot_online_curve_graph1.setData([], [])

        elif button == self.ui.connect_online_button_graph_2:
            # if  self.collector_online.running == True: 
            #     print("Stop Thread graph 2")
            #     self.collector_online.stop()
            # self.collector_online.wait()
            
            
            self.second_graph_online_connected = False 
            self.ui.connect_online_button_graph_2.setText("Connect Online") 
            # disconnect timer 2
            self.is_timer_graph2_connected = False
            self.timer_graph_2.timeout.disconnect(self.update_online_plot) 
            # Clear graph 2
            self.plot_online_curve_graph2.setData([], [])
            
            

            
    def update_online_plot(self):
        try:
            with open("online_data.json", "r") as file:
                self.data = json.load(file)
            y_axis = []
            for item in self.data["Data_Y"]:
                try:
                    item = float(item.replace(",", ""))
                except ValueError:
                    item = np.nan
                y_axis.append(item)
            # format time 
            time_data = self.data["Time"]
            if len(time_data) > 0:
                time_data = [self.format_time_string(t) for t in time_data]
                # first time as the base
                base_time = datetime.strptime(time_data[0], "%H:%M:%S") 
                x_axis = [(
                        datetime.strptime(self.format_time_string(t), "%H:%M:%S")
                        - base_time
                    ).total_seconds()
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
                if self.graph1_on and self.first_graph_online_connected:
                    print("graph 111")
                    self.ui.graph1Widget.graph.setLimits(xMin=0, xMax=x_axis[x_axis.size - 1], yMin=y_axis[0], yMax=y_axis[y_axis.size - 1])
                    self.plot_online_curve_graph1.setData(x_axis, y_axis)
                if self.graph2_on and self.second_graph_online_connected:
                    print("graph 222")
                    self.ui.graph2Widget.graph_2.setLimits(xMin=0, xMax=x_axis[x_axis.size - 1], yMin=y_axis[0], yMax=y_axis[y_axis.size - 1])
                    self.plot_online_curve_graph2.setData(x_axis, y_axis)
                # else:
                #     print("hahaha no sender ")
        except Exception as e:
            print(f"Error loading or plotting data: {e}")
    
    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str
    
    
    def stop_run_graph(self):
        sender_button = self.sender()
        if sender_button == self.ui.play_button_graph_1:
            print("graph 1 button ")
            self.graph1_on = not self.graph1_on
            if self.graph1_on:
                if self.first_graph_online_connected:
                    print("first online graph play")
                    self.timer_graph_1.timeout.connect(self.update_online_plot)
                else:    
                    self.timer_graph_1.timeout.connect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                if self.first_graph_online_connected:
                    print("first online graph stop")
                    self.timer_graph_1.timeout.disconnect(self.update_online_plot)
                else:
                    self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon1)
        
        elif sender_button == self.ui.play_button_graph_2:
            print("graph 2 button ")
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                if self.second_graph_online_connected:
                    print("second online graph play")
                    self.timer_graph_2.timeout.connect(self.update_online_plot)
                else:
                    self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                if self.second_graph_online_connected:
                    print("second online graph stop")
                    self.timer_graph_2.timeout.disconnect(self.update_online_plot)
                else:    
                    self.timer_graph_2.timeout.disconnect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon1)

        elif sender_button == self.ui.link_play_button:
            print("heyyyy link_play_button")
            self.play_both = not self.play_both
            if self.play_both:
                print("runnnnnnnnn:   ", self.play_both)
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.link_play_button.setIcon(self.ui.icon)
            elif not self.play_both:
                print("stoppppppppp:   ", self.play_both)
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
                print("Successfully disconnected from update_graph1.")
                self.ui.link_play_button.setIcon(self.ui.icon1)

    def open_file_graph_1(self):
          #self.timer.start(500)
        signal_processor= SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor1.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        
        graph = Graph(signal_processor.plot_widget)
        graph.signal_processor = signal_processor
        self.graphs_1.append(graph)


        # After the file is opened, prompt user for a name and store it
        new_name, ok = QInputDialog.getText(self, "Signal Name", "Enter a name for the new signal:")
        if ok and new_name:
            graph.add_signal(new_name, color = self.graph1_color)  # Adjust color as needed
            graph.toggle_signal_visibility(new_name, True)

            self.signals_graph_1[new_name] = (signal_processor, graph , signal_processor.plot_widget)
            self.ui.signals_name_combo_box_graph_1.addItem(new_name)
            self.ui.signals_name_combo_box_graph_1.setCurrentText(new_name)
            self.ui.signal_name_lineEdit_graph_1.clear()

            print(f"Opened file for {new_name} and added to Graph 1")
            print(f"Graph 1 signals: {self.signals_graph_1}")
        else:
            print("No signal name provided for Graph 1")
            
        if not self.is_timer_graph1_connected:
            self.timer_graph_1.timeout.connect(self.update_graph1)
            self.is_timer_graph1_connected = True
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()    

    def open_file_graph_2(self):

        signal_processor = SignalProcessor(self.ui.graph2Widget.graph_2)
        self.signal_processor2.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        graph.signal_processor = signal_processor
        self.graphs_2.append(graph)

        # After the file is opened, prompt user for a name and store it
        new_name, ok = QInputDialog.getText(self, "Signal Name", "Enter a name for the new signal:")
        
        if ok and new_name:
            graph.add_signal(new_name, color= self.graph2_color)  # Adjust color as needed
            graph.toggle_signal_visibility(new_name, True)
            
            self.signals_graph_2[new_name] = (signal_processor, graph, signal_processor.plot_widget)
            self.ui.signals_name_combo_box_graph_2.addItem(new_name)
            self.ui.signals_name_combo_box_graph_2.setCurrentText(new_name)
            self.ui.signal_name_lineEdit_graph_2.clear()
            print(type(self.signals_graph_2[new_name]))
            print(f"Opened file for {new_name} and added to Graph 2")
            print(f"Graph 2 signals: {self.signals_graph_2}")
        else:
            print("No signal name provided for Graph 2")
            
        if not self.is_timer_graph2_connected:
            self.timer_graph_2.timeout.connect(self.update_graph2)
            self.is_timer_graph2_connected = True
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()

        
    def update_graph1(self):
        window_width = 500 # Adjust the window width as needed
        selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
        visibility =self.ui.visible_checkBox_graph_1.isChecked()
        for graph in self.graphs_1:
            graph.toggle_signal_visibility(selected_name, visibility)
        for signal_processor_1, graph in zip(self.signal_processor1, self.graphs_1):
            data = signal_processor_1.get_next_data(self.window_width)
            # previous_data = signal_processor_1.get_previous_data()
            if data is not None:
                print("update graph 1")
                self.is_file1_opened = True
                graph.update_graph( data, signal_processor_1.current_index, window_width,self.graph1_color)

        
    def update_graph2(self): 
        window_width = 500 # Adjust the window width as needed
        selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
        visibility =self.ui.visible_checkBox_graph_2.isChecked()
        for graph in self.graphs_2:
            graph.toggle_signal_visibility(selected_name, visibility)
        for signal_processor_2, graph in zip(self.signal_processor2, self.graphs_2):
            data = signal_processor_2.get_next_data(self.window_width)
            # previous_data = signal_processor_2.get_previous_data()
            if data is not None:
                print("update graph 2")
                self.is_file2_opened = True
                graph.update_graph( data, signal_processor_2.current_index, window_width,self.graph2_color)

    def open_file_graph_3(self):
        if self.graph_3 is None:
            self.graph_3 = BubbleChartApp(self.graph_widget_3)
        
        # Call the open_file method to open a CSV file
        self.graph_3.open_file(self)

    def open_color_dialog(self, graph_number):
        # Open a color dialog and get the selected color
        color = QColorDialog.getColor()

        if color.isValid():
            # Update the signal color based on the chosen color
            hex_color = color.name()  # Get color in hex format
            print(hex_color)
            self.update_signal_color(hex_color, graph_number)

    def update_signal_color(self, color, graph_number):
        # Update the color of the plotted signal for the selected graph
        selected_name = None
        if graph_number == 1:
            selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
        elif graph_number == 2:
            selected_name = self.ui.signals_name_combo_box_graph_2.currentText()

        if selected_name:
            if graph_number == 1:
                if selected_name in self.signals_graph_1:
                    signal_processor, graph, plot_widget = self.signals_graph_1[selected_name]
                    graph.signals[selected_name]['item'].setPen(pg.mkPen(color))
            elif graph_number == 2:
                if selected_name in self.signals_graph_2:
                    signal_processor, graph, plot_widget = self.signals_graph_2[selected_name]
                    graph.signals[selected_name]['item'].setPen(pg.mkPen(color))
        else:
            print("No signal selected to change color.")
    
    def set_speed_graph_1(self, value):
        print("set speed graph 1")
        self.speed_graph_1 = value
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()

        if self.isLinked:
            self.timer_graph_2.setInterval(self.speed_graph_1)
            if not self.timer_graph_2.isActive():
                self.timer_graph_2.start()

    def set_speed_graph_2(self, value):
        print("set speed graph 2")
        self.speed_graph_2 = value
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()

        if self.isLinked:
            self.timer_graph_1.setInterval(self.speed_graph_2)
            if not self.timer_graph_1.isActive():
                self.timer_graph_1.start()

    def move_signal_from_graph1_to_graph2(self):
        selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
        if selected_name in self.signals_graph_1:
            signal_processor, graph, plot_widget = self.signals_graph_1[selected_name]
            saved_data = signal_processor.get_data()

            # Remove from Graph 1 and plot in Graph 2
            graph.move_signal_to_another_graph(selected_name, self.graph2_color, saved_data, self.graphs_2[-1])

            # Update signals_graph dictionaries
            del self.signals_graph_1[selected_name]
            self.ui.signals_name_combo_box_graph_1.removeItem(self.ui.signals_name_combo_box_graph_1.currentIndex())
            self.signals_graph_2[selected_name] = (signal_processor, graph, plot_widget)
            self.ui.signals_name_combo_box_graph_2.addItem(selected_name)
        else:
            print(f"Error: Signal '{selected_name}' not found in Graph 1.")

    def move_signal_from_graph2_to_graph1(self):
        selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
        if selected_name in self.signals_graph_2:
            source_graph = self.graphs_2[-1]  # Ensure this refers to a Graph instance
            target_graph = self.graphs_1[-1]  # Ensure this refers to a Graph instance
            
            # Call the method to move the signal and get necessary data
            signal_processor, plot_widget, graph_color = self.signals_graph_2[selected_name]
            
            # Save the current data from the signal processor before moving
            saved_data = signal_processor.get_data()
            current_index = signal_processor.current_index  # Retrieve the current index
            window_width = 500  # Ensure this is the right width for the target graph
            
            # Move the signal to the target graph
            try:
                source_graph.move_signal_to_another_graph(selected_name, self.graph1_color)
            except AttributeError as e:
                print(f"Error while moving signal: {e}")

            # Update the target graph with the new data
            target_graph.update_graph(saved_data, current_index, window_width, graph_color)

            if not self.is_timer_graph1_connected:
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.is_timer_graph_1_connected = True
                self.timer_graph_1.setInterval(self.speed_graph_1)
            if not self.timer_graph_1.isActive():
                self.timer_graph_1.start()


            # Manage the visibility in the combo boxes
            del self.signals_graph_2[selected_name]
            self.ui.signals_name_combo_box_graph_2.removeItem(self.ui.signals_name_combo_box_graph_2.currentIndex())
            self.signals_graph_1[selected_name] = (signal_processor, plot_widget)
            self.ui.signals_name_combo_box_graph_1.addItem(selected_name)
        else:
            print(f"Error: Signal '{selected_name}' not found in Graph 2.")




     
    def update_graph_name_1(self):  
        new_name = self.ui.signal_name_lineEdit_graph_1.text()
        print(new_name)
        self.ui.nameegraph1.setText(new_name)

        # Create the label text item
        self.ui.signals_name_combo_box_graph_1.addItem(new_name)
        self.ui.signals_name_combo_box_graph_1.setCurrentText(new_name)
        self.ui.signal_name_lineEdit_graph_1.clear()



    def update_graph_name_2(self):  
        new_name = self.ui.signal_name_lineEdit_graph_2.text()
        print(new_name)
        # self.ui.nameegraph2.setText(new_name)
        
        # Create the label text item
        self.ui.signals_name_combo_box_graph_2.addItem(new_name)
        self.ui.signals_name_combo_box_graph_2.setCurrentText(new_name)
        self.ui.signal_name_lineEdit_graph_2.clear()

        
        # Get the viewBox from the PlotWidget (for scaling)
        """ text_item = pg.TextItem(text=new_name, color='w', anchor=(0.5, 1))
        viewBox = self.graph_1.plot_widget.getViewBox()
        
        # Get the current scale (zoom level) of the viewBox
        scale_x, scale_y = viewBox.viewRange()[0][1], viewBox.viewRange()[1][1]
        
        # Calculate the font size based on the scale (zoom factor)
        # You can adjust the scaling factor for the font size as needed
        font_size = max(10, int(10 * scale_x))  # Make sure it doesn’t get too small
        
        # Set the label's font size (adjust dynamically with zoom)
        text_item.setFont(QtGui.QFont("Arial", font_size))
        
        # Get the PlotWidget's scene (this is where we can add floating items)
        scene = self.graph_1.plot_widget.scene()

        # Add the label to the scene (this keeps it floating above the plot)
        scene.addItem(text_item)
        
        # Position the label in absolute coordinates (fixed position in scene)
        text_item.setPos(700, 40)  # Adjust (x, y) for floating label position"""

    def link_graphs(self):
        self.isLinked = not self.isLinked
        if self.isLinked:
            if self.is_file1_opened and self.is_file2_opened:
                self.play_both = True
                # initially play
                if not self.graph1_on:
                    print("Connect 1111 after link ")
                    self.timer_graph_1.timeout.connect(self.update_graph1)
                if not self.graph2_on:
                    print("Connect 2222 after link ")
                    self.timer_graph_2.timeout.connect(self.update_graph2)

                # Clear both graphs
                # for graph in self.graphs_1:
                #     graph.plot_widget.clear()
                # for graph in self.graphs_2:
                #     graph.plot_widget.clear()
                # start from first
                for signal_processor in self.signal_processor1:
                    print("heeee  current_index = 0")
                    signal_processor.current_index = 0
                for signal_processor in self.signal_processor2:
                    print("kkkkk  current_index = 0")
                    signal_processor.current_index = 0

                # To link Views (zoom in/out and scroll)
                self.link1_view = self.link_views(self.ui.graph1Widget.graph, self.ui.graph2Widget.graph_2)
                self.link2_view = self.link_views(self.ui.graph2Widget.graph_2, self.ui.graph1Widget.graph)

                # GUI
                self.ui.link_play_button.setIcon(self.ui.icon)
                self.ui.link_button.setText("Un Link")
                self.ui.link_play_button.show()
                self.ui.link_rewind_button.show()
                self.ui.play_button_graph_1.hide()
                self.ui.play_button_graph_2.hide()
                self.ui.pause_button_graph_1.hide()
                self.ui.pause_button_graph_2.hide()
                self.ui.stop_button_graph_1.hide()
                self.ui.stop_button_graph_2.hide()
                self.ui.connect_online_button_graph_2.hide()
                self.ui.connect_online_button_graph_1.hide()
                self.ui.open_button_graph_2.hide()
                self.ui.open_button_graph_1.hide()
                self.ui.move_to_graph_1_button.hide()
                self.ui.move_to_graph_2_button.hide()

                self.timer_graph_1.start(self.speed_graph_1)
                self.timer_graph_2.start(self.speed_graph_1)
                
            else:
                self.isLinked = False
        else:
            self.un_link_graphs()

    def un_link_graphs(self):
        print("un linkk")
        # Return graphs to play same as before start linking
        print(self.play_both)
        if self.play_both:
            print("play both:  ", self.play_both)
            if not self.graph1_on:
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
            if not self.graph2_on:
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
        else:
            print("not play both:  ", self.play_both)
            if self.graph1_on:
                self.timer_graph_1.timeout.connect(self.update_graph1)
            if self.graph2_on:
                self.timer_graph_2.timeout.connect(self.update_graph2)
                
        # Disconnect the signals for view range (zoom)
        self.ui.graph1Widget.graph.sigRangeChanged.disconnect(self.link1_view)
        self.ui.graph2Widget.graph_2.sigRangeChanged.disconnect(self.link2_view)
                
        self.play_both = False
        # GUI
        self.ui.link_button.setText("Link")
        self.ui.link_play_button.hide()
        self.ui.link_rewind_button.hide()
        self.ui.play_button_graph_1.show()
        self.ui.play_button_graph_2.show()
        self.ui.pause_button_graph_1.show()
        self.ui.pause_button_graph_2.show()
        self.ui.stop_button_graph_1.show()
        self.ui.stop_button_graph_2.show()
        self.ui.connect_online_button_graph_2.show()
        self.ui.connect_online_button_graph_1.show()
        self.ui.open_button_graph_2.show()
        self.ui.open_button_graph_1.show()
        self.ui.move_to_graph_1_button.show()
        self.ui.move_to_graph_2_button.show()

    def link_views(self, source_plot, target_plot):
        def update_view():
            target_plot.setXRange(*source_plot.getViewBox().viewRange()[0], padding=0)
            target_plot.setYRange(*source_plot.getViewBox().viewRange()[1], padding=0)
            source_plot.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
            target_plot.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)

        # Connect 3ashan ye3ml update lama ye7sal ta8yer
        connection = source_plot.sigRangeChanged.connect(lambda: update_view())
        # Store connection hanehtago wehna bn3ml un link
        return connection        

    def taking_snap_shot(self, x):
        if x == 1:
            snapshot = QPixmap(self.ui.graph1Widget.graph.size())
            painter = QPainter(snapshot)
            self.ui.graph1Widget.graph.render(painter)
        elif x == 3:
            snapshot = QPixmap(self.ui.graph1Widget.graph.size())
            painter = QPainter(snapshot)
            self.ui.graph2Widget.graph_2.render(painter)

        # End the painter session (flush the drawing)
        painter.end()
        print("hh")

        # Save the snapshot to an image file (optional)
        if len(self.images) == 0:
            snapshot.save(f"graph_snapshot{0}.png")
            self.images.append(f"graph_snapshot{0}.png")
            print("img")
        else:
            snapshot.save(f"graph_snapshot{len(self.images)}.png")
            self.images.append(f"graph_snapshot{len(self.images)}.png")
            print(f"img{len(self.images) - 1}")

    def PDF_maker(self):
        # Create a PDF report using FPDF
        pdf = FPDF()
        pdf.add_page()

        # Add title to the PDF
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Signal Glue Report", ln=True, align="C")

        # Add the snapshot image to the PDF
        for x in range(len(self.images)):
            pdf.image(
                f"graph_snapshot{x}.png", x=10, y=20 + x * 50, w=100
            )  # Adjust position and size as needed
            print(f"graph_snapshot{x}.png")

        # Add some data statistics (example)
        pdf.set_xy(10, 120)  # Set position for the statistics text
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(
            0, 10, "Statistics:\n- Max value: 1.23\n- Min value: -0.56\n- Mean: 0.12"
        )

        # Save the PDF to a file
        pdf_path = "signal_glue_report.pdf"
        pdf.output(pdf_path)

        if os.path.exists(pdf_path):
            print(f"Report generated and saved at: {pdf_path}")
        else:
            print(f"Error: PDF report was not saved at {pdf_path}")
            
    def show_non_rectangle_plot(self):
        self.non_rectangle_plot= nonRectanglePlotWindow()
        self.non_rectangle_plot.show()        


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = MainWindow()
    ui.show()
    app.exec_()
