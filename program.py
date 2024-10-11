from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
import json
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog


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


        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        self.graph_3=BubbleChartApp(self.ui.graph1Widget_3.graph)
        self.graph1_color="w"
        self.graph2_color="w"
        self.signal_processor1 = [] 
        self.signal_processor2=[] # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2=[]

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.open_button_graph_3.clicked.connect(self.open_file_graph_3)
       
        self.ui.signal_color_button_graph_1.clicked.connect(lambda: self.open_color_dialog(1))
        self.ui.signal_color_button_graph_2.clicked.connect(lambda: self.open_color_dialog(2))
        self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(self.update_graph_name_1)
        self.ui.signal_name_lineEdit_graph_2.returnPressed.connect(self.update_graph_name_2)
        
        self.timer_graph_1 = QtCore.QTimer()
        self.timer_graph_1.start(10)
        self.timer_graph_2 = QtCore.QTimer()
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
        self.timer2.start(1000)
        self.timer2.timeout.connect(self.graph_3.update_graph)
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
                # Resume from the stored index
                self.signal_processor_1.current_index = self.graph1_pause_index
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                # Save the current index and stop
                self.graph1_pause_index = self.signal_processor_1.current_index
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon1)
        elif sender_button == self.ui.play_button_graph_2:
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                # Resume from the stored index
                self.signal_processor_2.current_index = self.graph2_pause_index
                self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                # Save the current index and stop
                self.graph2_pause_index = self.signal_processor_2.current_index
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon1)
    
    def open_file_graph_1(self):
          #self.timer.start(500)
        signal_processor= SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor1.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_1.append(graph)

        # Get the signal name from the line edit
        signal_name = self.ui.signal_name_lineEdit_graph_1.text()

        # Store the signal data in signals_graph_1 dictionary
        if signal_name:
            self.signals_graph_1[signal_name] = (signal_processor, graph)
            self.ui.signals_name_combo_box_graph_1.addItem(signal_name)
            self.ui.signals_name_combo_box_graph_1.setCurrentText(signal_name)

        # Clear the line edit after adding the signal
        self.ui.signal_name_lineEdit_graph_1.clear()
             
        self.timer_graph_1.timeout.connect(self.update_graph1)
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()


        # # After the file is opened, prompt user for a name and store it
        # new_name = self.ui.signal_name_lineEdit_graph_1.text()
        # if new_name:
        #     self.signals_graph_1[new_name] = signal_processor
        #     self.ui.signals_name_combo_box_graph_1.addItem(new_name)
        #     self.ui.signals_name_combo_box_graph_1.setCurrentText(new_name)
        #     self.ui.signal_name_lineEdit_graph_1.clear()

    def open_file_graph_2(self):
        
        signal_processor= SignalProcessor(self.ui.graph2Widget.graph_2)
        self.signal_processor2.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_2.append(graph)

        
        # Get the signal name from the line edit
        signal_name = self.ui.signal_name_lineEdit_graph_2.text()

        # Store the signal data in signals_graph_1 dictionary
        if signal_name:
            self.signals_graph_2[signal_name] = (signal_processor, graph)
            self.ui.signals_name_combo_box_graph_2.addItem(signal_name)
            self.ui.signals_name_combo_box_graph_2.setCurrentText(signal_name)

        # Clear the line edit after adding the signal
        self.ui.signal_name_lineEdit_graph_2.clear()


        self.timer_graph_2.timeout.connect(self.update_graph2)
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()

        
    def update_graph1(self):
         window_width = 500 # Adjust the window width as needed
         for signal_processor_1, graph in zip(self.signal_processor1, self.graphs_1):
            data = signal_processor_1.get_next_data(self.window_width)
            if data is not None:
                graph.update_graph(data, signal_processor_1.current_index, window_width,self.graph1_color)

        
    def update_graph2(self): 
        window_width = 500 # Adjust the window width as needed
        for signal_processor_2, graph in zip(self.signal_processor2, self.graphs_2):
                    data = signal_processor_2.get_next_data(self.window_width)
                    if data is not None:
                        graph.update_graph(data, signal_processor_2.current_index, window_width,self.graph2_color)

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
        print(graph_number)
        if graph_number==1 :
            self.graph1_color=color
        else :self.graph2_color=color
    def set_speed_graph_1(self, value):
        self.speed_graph_1 = value
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()

    def set_speed_graph_2(self, value):
        self.speed_graph_2 = value
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()

    def move_signal_from_graph1_to_graph2(self):
        # Get the selected signal name from the combo box
        selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
    
        # Check if the selected signal is in graph1
        if selected_name in self.signals_graph_1:
            # Retrieve the signal processor and graph associated with the signal
            signal_processor, graph = self.signals_graph_1.pop(selected_name)
        
            # Add the signal to graph2's dictionaries and list
            self.signals_graph_2[selected_name] = (signal_processor, graph)
            self.graphs_2.append(graph)
            self.signal_processor2.append(signal_processor)
        
            # Remove the signal from graph1's combo box and update graph2
            self.ui.signals_name_combo_box_graph_1.removeItem(self.ui.signals_name_combo_box_graph_1.currentIndex())
            self.ui.signals_name_combo_box_graph_2.addItem(selected_name)
            self.update_graph2()

    def move_signal_from_graph2_to_graph1(self):
        # Get the selected signal name from the combo box
        selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
    
        # Check if the selected signal is in graph2
        if selected_name in self.signals_graph_2:
            # Retrieve the signal processor and graph associated with the signal
            signal_processor, graph = self.signals_graph_2.pop(selected_name)
        
            # Add the signal to graph1's dictionaries and list
            self.signals_graph_1[selected_name] = (signal_processor, graph)
            self.graphs_1.append(graph)
            self.signal_processor1.append(signal_processor)
        
            # Remove the signal from graph2's combo box and update graph1
            self.ui.signals_name_combo_box_graph_2.removeItem(self.ui.signals_name_combo_box_graph_2.currentIndex())
            self.ui.signals_name_combo_box_graph_1.addItem(selected_name)
            self.update_graph1()




     
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
        ''' text_item = pg.TextItem(text=new_name, color='w', anchor=(0.5, 1))
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
        text_item.setPos(700, 40)  # Adjust (x, y) for floating label position'''


                
                    

    
   
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()
        



       
    
        
    