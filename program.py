from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPixmap
from scipy import interpolate
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QGraphicsOpacityEffect
import json
import os
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow
from non_rectangle_plot_window import nonRectanglePlotWindow
from collect_online_data import CollectOnlineData
from PyQt5 import QtCore
from PyQt5.QtWidgets import QColorDialog
from fpdf import FPDF
from signal_1 import SignalProcessor
from graph import Graph

class CustomAxis(pg.AxisItem):
    def tickString(self, value, scale, sigDigits=3):
        return "{:.3f}".format(value)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.signal_count = 0

        # self.ui.graph1Widget.graph.plotItem.getAxis('left').setTickSpacing(100, 10)
        self.ui.graph1Widget.graph.plotItem.setLabel("left", "Voltage")
        self.ui.graph1Widget.graph.plotItem.setLabel("bottom", "Time (s)")
        self.ui.graph2Widget.graph_2.plotItem.setLabel("left", "Voltage")
        self.ui.graph2Widget.graph_2.plotItem.setLabel("bottom", "Time (s)")
        self.ui.graph1Widget_3.graph.plotItem.setLabel("left", "Voltage")
        self.ui.graph1Widget_3.graph.plotItem.setLabel("bottom", "Time (s)")

        self.timer = QtCore.QTimer()
        self.timer2 = QtCore.QTimer()
        self.max_index_graph1 = 0
        self.max_index_graph2 = 0
        self.ui.graph1Widget.graph.setLimits(xMin=0)
        self.ui.graph2Widget.graph_2.setLimits(xMin=0)
        self.ui.graph1Widget_3.graph.setLimits(xMin=0)
        self.images = []

        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        self.graph1_color="w"
        self.graph2_color="w"
        self.signal_processor1 = [] 
        self.signal_processor2=[] # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2 = []
        self.graph2_filtered_x = []
        self.graph2_filtered_y = []
        self.graph1_filtered_x = []
        self.graph1_filtered_y = []
        self.x_shifted = []
        self.whole_x_data = []
        self.whole_y_data = []
        self.graph1_plot = self.ui.graph1Widget_3.graph.plot([], [], pen=pg.mkPen("w", width=1))
        self.graph2_plot = None
        self.ui.slider_glue.setMinimum(-40)
        self.ui.slider_glue.setMaximum(40)
        self.ui.slider_glue.setValue(0) 
        self.ui.slider_glue.setSingleStep(1) 
        self.ui.slider_glue.valueChanged.connect(self.on_slider_change)
        self.total_shifed_glue_slider = 0.0
        self.graph1_end_x = None
        self.graph1_start_x = None
        self.graph1_end_y = None
        self.graph1_start_y = None
        self.graph2_start_x = None
        self.graph2_end_x=None
        self.graph2_start_y =None
        self.graph2_end_y=None
        self.cutted_signal_color_graph1='w'
        self.cutted_signal_color_graph2='w'
     
        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.snapshot_button_graph_3.clicked.connect(lambda: self.taking_snapshot(3))
        self.ui.snapshot_button.clicked.connect(lambda: self.taking_snapshot(1))
        self.ui.snapshot_button_graph2.clicked.connect(lambda: self.taking_snapshot(2))
        self.ui.export_button.clicked.connect(self.PDF_maker)
        
        

        self.ui.select_button_graph1.clicked.connect(self.select_graph_to_cut)
        self.ui.select_button_graph2.clicked.connect(self.select_graph_to_cut_2)
        self.ui.pushButton.clicked.connect(self.on_glue_button_click)

        self.ui.signal_color_button_graph_1.clicked.connect(
            lambda: self.open_color_dialog(1)
        )
        self.ui.signal_color_button_graph_2.clicked.connect(
            lambda: self.open_color_dialog(2)
        )
        # self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(
        #     self.update_graph_name_1
        # )

        # self.ui.signal_name_lineEdit_graph_2.returnPressed.connect(
        #     self.update_graph_name_2
        # )

        self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(lambda: self.update_graph_name(1))
        self.ui.signal_name_lineEdit_graph_2.returnPressed.connect(lambda: self.update_graph_name(2))


        self.timer_graph_1 = QtCore.QTimer()
        # self.timer_graph_1.start(10)
        self.timer_graph_2 = QtCore.QTimer()
        self.speed_graph_1 = 25  # Default speed in ms
        self.speed_graph_2 = 25  # Default speed in ms
        # Initialize dictionaries to store signals by name
        self.signals_graph_1 = {}
        self.signals_graph_2 = {}

        self.ui.speed_slider_graph_1.valueChanged.connect(self.set_speed_graph_1)
        self.ui.speed_slider_graph_2.valueChanged.connect(self.set_speed_graph_2)

        self.ui.move_to_graph_1_button.clicked.connect(
            self.move_signal_from_graph2_to_graph1
        )
        self.ui.move_to_graph_2_button.clicked.connect(
            self.move_signal_from_graph1_to_graph2
        )

        self.ui.reset_button_graph_1.clicked.connect(lambda: self.rewind_graph(1))
        self.ui.reset_button_graph_2.clicked.connect(lambda: self.rewind_graph(2))

        self.ui.link_button.clicked.connect(self.link_graphs)
        self.ui.link_play_button.clicked.connect(self.stop_run_graph)
        self.ui.link_rewind_button.clicked.connect(lambda: self.rewind_graph(1))
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

        # Collect Online Data Thread
        self.collector_online = CollectOnlineData()

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
        # self.timer2.timeout.connect(self.graph_3.update_graph)
        self.ui.nonrectangle_graph_button.clicked.connect(self.show_non_rectangle_plot)
        self.timer.start(1000)
        self.rect_roi = pg.RectROI([0, -0.25], [0.2, 1.4], pen='r')
        self.rect_roi.addScaleHandle([1, 0.5], [0.5, 0.5]) 
        self.selected_range = None        

    def connect_online(self):
        sender_button = self.sender()

        if (
            sender_button == self.ui.connect_online_button_graph_1
            and self.first_graph_online_connected
        ):
            self.ui.graph1Widget.graph.plotItem.setLabel("left", "Voltage")
            self.disconnect_online(sender_button)

        elif (
            sender_button == self.ui.connect_online_button_graph_2
            and self.second_graph_online_connected
        ):
            self.ui.graph2Widget.graph_2.plotItem.setLabel("left", "Voltage")
            self.disconnect_online(sender_button)

        elif (
            sender_button == self.ui.connect_online_button_graph_1
        ) and self.graph1_on:  # clicked on connect_online_button_graph_1
            self.ui.graph1Widget.graph.plotItem.setLabel("left", "Distance (km)")
            # self.ui.graph1Widget.graph.setAxisItems({'left': CustomAxis(orientation='left')})
            # self.ui.graph1Widget.graph.plotItem.setAxisItems({'left': CustomAxis(orientation='left')})
            # self.ui.graph1Widget.graph.setAxisItems({'left': CustomAxis(orientation='left')})
            # self.ui.graph1Widget.graph.plotItem.getAxis('left').setTickSpacing(100, 10)
# Set the label for the left axis after setting the custom axis
            # self.ui.graph1Widget.graph.plotItem.setLabel("left", "Distance (km)")
            
            self.first_graph_online_connected = True
            self.ui.open_button_graph_1.setDisabled(True)
            self.ui.open_button_graph_1.setGraphicsEffect(
                effect := QGraphicsOpacityEffect()
            ) or effect.setOpacity(0.4)

            if self.collector_online.running == False:
                self.collector_online.start()
                self.collector_online.data_fetched.connect(self.update_online_plot)

            if not self.is_timer_graph1_connected:
                self.is_timer_graph1_connected = True
                self.timer_graph_1.start(10)
                self.timer_graph_1.timeout.connect(self.update_online_plot)

            self.ui.connect_online_button_graph_1.setText("Disconnect Online")

        elif (
            sender_button == self.ui.connect_online_button_graph_2
        ) and self.graph2_on:  # clicked on connect_online_button_graph_2
            self.ui.graph2Widget.graph_2.plotItem.setLabel("left", "Distance (km)")
            self.second_graph_online_connected = True
            self.ui.open_button_graph_2.setDisabled(True)
            self.ui.open_button_graph_2.setGraphicsEffect(
                effect := QGraphicsOpacityEffect()
            ) or effect.setOpacity(0.4)

            if self.collector_online.running == False:
                self.collector_online.start()
                self.collector_online.data_fetched.connect(self.update_online_plot)

            if not self.is_timer_graph2_connected:
                self.is_timer_graph2_connected = True
                self.timer_graph_2.start(10)
                self.timer_graph_2.timeout.connect(self.update_online_plot)

            self.ui.connect_online_button_graph_2.setText("Disconnect Online")

    def disconnect_online(self, button):
        if button == self.ui.connect_online_button_graph_1:
            # open button graph 1 disable and opacity
            self.ui.open_button_graph_1.setDisabled(False)
            self.ui.open_button_graph_1.setGraphicsEffect(
                effect := QGraphicsOpacityEffect()
            ) or effect.setOpacity(1)

            # stop thread
            if (
                self.collector_online.running == True
                and not self.second_graph_online_connected
            ):
                self.collector_online.stop()

            self.first_graph_online_connected = False
            self.ui.connect_online_button_graph_1.setText("Connect Online")
            # disconnect timer 1
            self.is_timer_graph1_connected = False
            if self.graph1_on:
                self.timer_graph_1.timeout.disconnect(self.update_online_plot)
            # Clear graph 1
            self.plot_online_curve_graph1.setData([], [])

        elif button == self.ui.connect_online_button_graph_2:
            # open button graph 2 disable and opacity
            self.ui.open_button_graph_2.setDisabled(False)
            self.ui.open_button_graph_2.setGraphicsEffect(
                effect := QGraphicsOpacityEffect()
            ) or effect.setOpacity(1)

            if (
                self.collector_online.running == True
                and not self.first_graph_online_connected
            ):
                self.collector_online.stop()

            self.second_graph_online_connected = False
            self.ui.connect_online_button_graph_2.setText("Connect Online")
            # disconnect timer 2
            self.is_timer_graph2_connected = False
            if self.graph2_on:
                self.timer_graph_2.timeout.disconnect(self.update_online_plot)
            # Clear graph 2
            self.plot_online_curve_graph2.setData([], [])

    def update_online_plot(self):
        try:
            with open("online_data.json", "r") as file:
                self.data = json.load(file)
            y_axis = []
            for item in self.data["Data_Y"]:
                item = float(item.replace(",", ""))
                # item = (f"{(item / (13377 * 10**9)):.6f}")
                # y_axis.append(item / (133777 * 10**9))
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

            if len(x_axis) > 0 and len(y_axis) > 0:
                if self.graph1_on and self.first_graph_online_connected:
                    self.ui.graph1Widget.graph.setLimits(
                        xMin=0,
                        xMax=x_axis[len(x_axis) - 1],
                        yMin=y_axis[0],
                        yMax=y_axis[len(y_axis) - 1],
                    )
                    self.plot_online_curve_graph1.setData(x_axis, y_axis)
                if self.graph2_on and self.second_graph_online_connected:
                    self.ui.graph2Widget.graph_2.setLimits(
                        xMin=0,
                        xMax=x_axis[len(x_axis) - 1],
                        yMin=y_axis[0],
                        yMax=y_axis[len(y_axis) - 1],
                    )
                    self.plot_online_curve_graph2.setData(x_axis, y_axis)
        except Exception as e:
            print(f"error plot online data: {e}")
            
    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str       

    def stop_run_graph(self):
        sender_button = self.sender()
        if sender_button == self.ui.play_button_graph_1:
            self.graph1_on = not self.graph1_on
            if self.graph1_on:
                if self.first_graph_online_connected:
                    self.timer_graph_1.timeout.connect(self.update_online_plot)
                else:
                    self.timer_graph_1.timeout.connect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                if self.first_graph_online_connected:
                    self.timer_graph_1.timeout.disconnect(self.update_online_plot)
                else:
                    self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.pause)

        elif sender_button == self.ui.play_button_graph_2:
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                if self.second_graph_online_connected:
                    self.timer_graph_2.timeout.connect(self.update_online_plot)
                else:
                    self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                if self.second_graph_online_connected:
                    self.timer_graph_2.timeout.disconnect(self.update_online_plot)
                else:
                    self.timer_graph_2.timeout.disconnect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.pause)

        elif sender_button == self.ui.link_play_button:
            self.play_both = not self.play_both
            if self.play_both:
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.link_play_button.setIcon(self.ui.icon)
            elif not self.play_both:
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
                self.ui.link_play_button.setIcon(self.ui.pause)

    def show_input_dialog(self):
        input_dialog = QInputDialog(self)
        input_dialog.setStyleSheet(
            """
            QInputDialog { background-color: white; }
            QLineEdit { background-color: white; color: black; }
            QPushButton { background-color: white; color: black; }
        """
        )
        return input_dialog.getText(
            self, "Signal Name", "Enter a name for the new signal:"
        )

    def open_file_graph_1(self):

        signal_processor = SignalProcessor(self.ui.graph1Widget.graph)
        # add the new signal pricessor to the the list of signal processors for graph 1
        self.signal_processor1.append(signal_processor)

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate the new signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        graph.signal_processor = signal_processor
        self.graphs_1.append(graph)

        default_name_prefix = "Signal"
        self.signal_count += 1
        new_name = f"{default_name_prefix} {self.signal_count}"

        # After the file is opened, prompt user for a name and add the signal to the dictionary signals_graph_1 wher the name is the id 
        # new_name, ok = QInputDialog.getText(self, "Signal Name", "Enter a name for the new signal:")
        # if ok and new_name:
        #     self.ui.connect_online_button_graph_1.setDisabled(True)
        #     self.ui.connect_online_button_graph_1.setGraphicsEffect(effect := QGraphicsOpacityEffect()) or effect.setOpacity(0.4)

        #     graph.add_signal(new_name, color = self.graph1_color)
        #     #set the new signal to be visible
        #     graph.toggle_signal_visibility(new_name, True)
        #     #add the name of the new signal to the legand of the graph
        #     graph.update_signal_label(new_name, color= self.graph2_color)
        #     self.signals_graph_1[new_name] = (signal_processor, graph , signal_processor.plot_widget)
        #     self.ui.signals_name_combo_box_graph_1.addItem(new_name)
        #     self.ui.signals_name_combo_box_graph_1.setCurrentText(new_name)
        #     self.ui.signal_name_lineEdit_graph_1.clear()

        self.ui.connect_online_button_graph_1.setDisabled(True)
        self.ui.connect_online_button_graph_1.setGraphicsEffect(effect := QGraphicsOpacityEffect()) or effect.setOpacity(0.4)
        graph.add_signal(new_name, color = self.graph1_color)
        #set the new signal to be visible
        graph.toggle_signal_visibility(new_name, True)
        #add the name of the new signal to the legand of the graph
        graph.update_signal_label(new_name, color= self.graph2_color)
        self.signals_graph_1[new_name] = (signal_processor, graph , signal_processor.plot_widget)
        self.ui.signals_name_combo_box_graph_1.addItem(new_name)
        self.ui.signals_name_combo_box_graph_1.setCurrentText(new_name)
        self.ui.signal_name_lineEdit_graph_1.clear()

        print(f"Opened file for {new_name} and added to Graph 1")
        print(f"Graph 1 signals: {self.signals_graph_1}")

        if not self.is_timer_graph1_connected:
            self.timer_graph_1.timeout.connect(self.update_graph1)
            self.is_timer_graph1_connected = True
        self.timer_graph_1.setInterval(self.speed_graph_1)
        # if not self.timer_graph_1.isActive():
        #     self.timer_graph_1.start()

    def open_file_graph_2(self):

        signal_processor = SignalProcessor(self.ui.graph2Widget.graph_2)
        self.signal_processor2.append(signal_processor)

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        graph.signal_processor = signal_processor
        self.graphs_2.append(graph)

        default_name_prefix = "Signal"
        self.signal_count += 1
        new_name = f"{default_name_prefix} {self.signal_count}"

        self.ui.connect_online_button_graph_2.setDisabled(True)
        self.ui.connect_online_button_graph_2.setGraphicsEffect(effect := QGraphicsOpacityEffect()) or effect.setOpacity(0.4)

        graph.add_signal(new_name, color = self.graph1_color)
        #set the new signal to be visible
        graph.toggle_signal_visibility(new_name, True)
        #add the name of the new signal to the legand of the graph
        graph.update_signal_label(new_name, color= self.graph2_color)
        self.signals_graph_2[new_name] = (signal_processor, graph , signal_processor.plot_widget)
        self.ui.signals_name_combo_box_graph_2.addItem(new_name)
        self.ui.signals_name_combo_box_graph_2.setCurrentText(new_name)
        self.ui.signal_name_lineEdit_graph_2.clear()

        print(f"Opened file for {new_name} and added to Graph 1")
        print(f"Graph 1 signals: {self.signals_graph_2}")   
            
        if not self.is_timer_graph2_connected:
            self.timer_graph_2.timeout.connect(self.update_graph2)
            self.is_timer_graph2_connected = True
        self.timer_graph_2.setInterval(self.speed_graph_2)
        # if not self.timer_graph_2.isActive():
        #     self.timer_graph_2.start()

    def update_graph1(self):
        window_width = 500

        for signal in self.signal_processor1:
            if signal.current_index > self.max_index_graph1:
                self.max_index_graph1 = signal.current_index

        if self.max_index_graph1 >= window_width:
            self.ui.graph1Widget.graph.setLimits(
                xMin=0, xMax=(self.max_index_graph1) * 0.001
            )
        else:
            self.ui.graph1Widget.graph.setLimits(xMin=0, xMax=window_width * 0.001)

        selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
        visibility = self.ui.visible_checkBox_graph_1.isChecked()
        for graph in self.graphs_1:
            graph.toggle_signal_visibility(selected_name, visibility)
        for signal_processor_1, graph in zip(self.signal_processor1, self.graphs_1):
            data = signal_processor_1.get_next_data(self.window_width)
            if data is not None:
                self.is_file1_opened = True
                graph.update_graph(
                    data,
                    signal_processor_1.current_index,
                    window_width,
                    self.graph1_color,
                )

    def update_graph2(self):
        window_width = 500

        for signal in self.signal_processor2:
            if signal.current_index > self.max_index_graph2:
                self.max_index_graph2 = signal.current_index

        if self.max_index_graph2 >= window_width:
            self.ui.graph2Widget.graph_2.setLimits(
                xMin=0, xMax=(self.max_index_graph2) * 0.001
            )
        else:
            self.ui.graph2Widget.graph_2.setLimits(xMin=0, xMax=window_width * 0.001)

        selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
        visibility = self.ui.visible_checkBox_graph_2.isChecked()
        for graph in self.graphs_2:
            graph.toggle_signal_visibility(selected_name, visibility)
        for signal_processor_2, graph in zip(self.signal_processor2, self.graphs_2):
            data = signal_processor_2.get_next_data(self.window_width)
            if data is not None:
                self.is_file2_opened = True
                graph.update_graph(
                    data,
                    signal_processor_2.current_index,
                    window_width,
                    self.graph2_color,
                )

    def open_color_dialog(self, graph_number):
        # Open a color dialog and get the selected color
        color = QColorDialog.getColor()

        if color.isValid():
            # Update the signal color based on the chosen color
            hex_color = color.name()  # Get color in hex format
            print(hex_color)
            self.update_signal_color(hex_color, graph_number)

    def update_signal_color(self, color, graph_number):
        # Update the color of the selected signal
        selected_name = None
        # take the selected signal from each graph
        if graph_number == 1:
            selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
        elif graph_number == 2:
            selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
        # for graph1
        if selected_name:
            if graph_number == 1:
                if selected_name in self.signals_graph_1:
                    signal_processor, graph, plot_widget = self.signals_graph_1[
                        selected_name
                    ]
                    # set the color for the selected signal
                    graph.signals[selected_name]["item"].setPen(pg.mkPen(color))
                    # Update the label color too
                    graph.update_signal_label(selected_name, color)
                    self.cutted_signal_color_graph1=color
            # for graph2           
            elif graph_number == 2:
                if selected_name in self.signals_graph_2:
                    signal_processor, graph, plot_widget = self.signals_graph_2[
                        selected_name
                    ]
                    # set the color for the selected signal
                    graph.signals[selected_name]["item"].setPen(pg.mkPen(color))
                    # Update the label color too
                    graph.update_signal_label(selected_name, color)
                    self.cutted_signal_color_graph2=color
        else:
            print("No signal selected to change color.")

    def rewind_graph(self, graph_number):
        # for x limit
        if graph_number == 1:
            self.max_index_graph1 = 0
        else:
            self.max_index_graph2 = 0

        # rewind on link
        if self.isLinked:
            for signal_processor in self.signal_processor1:
                signal_processor.current_index = 0
            for signal_processor in self.signal_processor2:
                signal_processor.current_index = 0
        # for graph1
        elif graph_number == 1:
            # take the selected name
            selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
            if selected_name:
                # take the signal processor of the selected signal
                signal_processor = self.signals_graph_1[selected_name][0]
                # rewind_graph() a method in signal_1.py
                signal_processor.rewind_graph()
                # udpate the signal afyer rewinding
                # if not self.is_timer_graph1_connected:
                #     self.timer_graph_1.timeout.connect(self.update_graph1)
                print(f"Rewound signal '{selected_name}' on Graph 1")

        elif graph_number == 2:
            selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
            if selected_name:
                signal_processor = self.signals_graph_2[selected_name][0]
                signal_processor.rewind_graph()
                # self.timer_graph_2.start()
                print(f"Rewound signal '{selected_name}' on Graph 2")

    def set_speed_graph_1(self, value):
        print("set speed graph 1")
        self.speed_graph_1 = value
        # set the speed
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

        if not selected_name:
            print("No signal selected for moving.")
            return

        if selected_name in self.signals_graph_1:
            signal_processor, graph1, plot_item2 = self.signals_graph_1[selected_name]

            for i, signal in enumerate(self.signal_processor1):
                if signal == signal_processor:
                    del self.signal_processor1[i]

            current_color = graph1.signals[selected_name]["item"].opts["pen"].color()

            graph1.legend.removeItem(selected_name)
            graph1.remove_signal(selected_name)
            del self.signals_graph_1[selected_name]
            self.ui.signals_name_combo_box_graph_1.removeItem(self.ui.signals_name_combo_box_graph_1.currentIndex()) 

            if graph1 in self.graphs_1:
                self.graphs_1.remove(graph1)
            if signal_processor in self.signal_processor1:
                self.signal_processor1.remove(signal_processor)


            graph2 = Graph(self.ui.graph2Widget.graph_2)
            self.signal_processor2.append(signal_processor)

            graph2.signal_processor = signal_processor
            self.graphs_2.append(graph2)

            graph2.add_signal(selected_name, color=current_color)
            graph2.update_signal_label(selected_name, color=current_color)
            graph2.toggle_signal_visibility(selected_name, True)

            self.signals_graph_2[selected_name] = (
                signal_processor,
                graph2,
                signal_processor.plot_widget,
            )
            self.ui.signals_name_combo_box_graph_2.addItem(selected_name)

            signal_processor.current_index = 0

            if not self.is_timer_graph2_connected:
                self.timer_graph_2.timeout.connect(self.update_graph2)
                self.is_timer_graph2_connected = True
                # self.timer_graph_2.setInterval(self.speed_graph_2)
            # if not self.timer_graph_2.isActive():
            #     self.timer_graph_2.start()

            # if not self.signals_graph_1:
            #     if self.timer_graph_1.isActive():
            #         self.timer_graph_1.stop()
            #         print("Graph 1 timer stopped as no signals are left.")

            print(f"Graph 1 signals after moving: {self.signals_graph_1.keys()}")
            print(f"Graph 2 signals after moving: {self.signals_graph_2.keys()}")
        else:
            print(f"Signal '{selected_name}' not found in Graph 2.")

        # print("G1: ", self.signals_graph_1)
        # print("G2: ", self.signals_graph_2)

    def move_signal_from_graph2_to_graph1(self):
        selected_name = self.ui.signals_name_combo_box_graph_2.currentText()

        if not selected_name:
            print("No signal selected for moving.")
            return

        if selected_name in self.signals_graph_2:
            signal_processor, graph2, plot_item2 = self.signals_graph_2[selected_name]

            for i, signal in enumerate(self.signal_processor2):
                if signal == signal_processor:
                    del self.signal_processor2[i]

            current_color = graph2.signals[selected_name]["item"].opts["pen"].color()
            graph2.legend.removeItem(selected_name)
            graph2.remove_signal(selected_name)
            del self.signals_graph_2[selected_name]
            self.ui.signals_name_combo_box_graph_2.removeItem(
                self.ui.signals_name_combo_box_graph_2.currentIndex()
            )

            if graph2 in self.graphs_2:
                self.graphs_2.remove(graph2)
            if signal_processor in self.signal_processor2:
                self.signal_processor2.remove(signal_processor)

            graph1 = Graph(self.ui.graph1Widget.graph)  
            self.signal_processor1.append(signal_processor)

            graph1.signal_processor = signal_processor
            self.graphs_1.append(graph1)

            graph1.add_signal(selected_name, color=current_color)
            graph1.update_signal_label(selected_name, color=current_color)
            graph1.toggle_signal_visibility(selected_name, True)

            self.signals_graph_1[selected_name] = (
                signal_processor,
                graph1,
                signal_processor.plot_widget,
            )
            self.ui.signals_name_combo_box_graph_1.addItem(selected_name)

            signal_processor.current_index = 0

            # if not self.is_timer_graph1_connected:
            #     self.timer_graph_1.timeout.connect(self.update_graph1)
            #     self.is_timer_graph1_connected = True
            if not self.is_timer_graph1_connected:
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.is_timer_graph1_connected = True
                # self.timer_graph_1.setInterval(self.speed_graph_1)
            # if not self.timer_graph_1.isActive():
            #     self.timer_graph_1.start()

            # if not self.signals_graph_2:
            #     if self.timer_graph_2.isActive():
            #         self.timer_graph_2.stop()
            #         print("Graph 2 timer stopped as no signals are left.")

            print(f"Graph 1 signals after moving: {self.signals_graph_1.keys()}")
            print(f"Graph 2 signals after moving: {self.signals_graph_2.keys()}")
        else:
            print(f"Signal '{selected_name}' not found in Graph 2.")


    def update_graph_name(self, graph_number):  
        if graph_number == 1:
            new_name = self.ui.signal_name_lineEdit_graph_1.text()
            selected_name = self.ui.signals_name_combo_box_graph_1.currentText()
            signal_dict = self.signals_graph_1
            combo_box = self.ui.signals_name_combo_box_graph_1
            line_edit = self.ui.signal_name_lineEdit_graph_1
        else:  # For Graph 2
            new_name = self.ui.signal_name_lineEdit_graph_2.text()
            selected_name = self.ui.signals_name_combo_box_graph_2.currentText()
            signal_dict = self.signals_graph_2
            combo_box = self.ui.signals_name_combo_box_graph_2
            line_edit = self.ui.signal_name_lineEdit_graph_2

        if selected_name in signal_dict:
            # Update signal's name in signals dictionary and combo box
            signal_processor, graph, _ = signal_dict.pop(selected_name)
            color = graph.signals[selected_name]['item'].opts['pen'].color()

            # Directly update the graph's signals dictionary with the new name
            graph.signals[new_name] = graph.signals.pop(selected_name)
            signal_dict[new_name] = (signal_processor, graph, graph.plot_widget)

            # Update combo box
            index = combo_box.findText(selected_name)
            combo_box.setItemText(index, new_name)
            line_edit.clear()
            combo_box.setCurrentText(new_name)

            # Update the label and the color for the new signal name
            graph.update_signal_label(new_name, color)
            graph.signals[new_name]["item"].setPen(
                pg.mkPen(color)
            )  # Apply the color to the plot

            # Update the legend entry to reflect the new signal name
            graph.legend.removeItem(selected_name)  # Remove the old entry
            graph.legend.addItem(
                graph.signals[new_name]["item"], new_name
            )  # Add new entry to legend

            print(f"Updated signal name to {new_name} with color {color}")
        else:
            print(f"Signal '{selected_name}' not found in Graph {graph_number}.")


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
                    self.timer_graph_1.timeout.connect(self.update_graph1)
                if not self.graph2_on:
                    self.timer_graph_2.timeout.connect(self.update_graph2)

                # for x limit
                self.max_index_graph1 = 0
                self.max_index_graph2 = 0

                # start from first
                for signal_processor in self.signal_processor1:
                    signal_processor.current_index = 0
                for signal_processor in self.signal_processor2:
                    signal_processor.current_index = 0

                # To link Views (zoom in/out and scroll)
                self.link1_view = self.link_views(
                    self.ui.graph1Widget.graph, self.ui.graph2Widget.graph_2
                )
                self.link2_view = self.link_views(
                    self.ui.graph2Widget.graph_2, self.ui.graph1Widget.graph
                )

                # GUI
                self.ui.link_play_button.setIcon(self.ui.icon)
                self.ui.link_button.setText("Un Link")
                self.ui.link_play_button.show()
                self.ui.link_rewind_button.show()
                self.ui.play_button_graph_1.hide()
                self.ui.play_button_graph_2.hide()
                self.ui.reset_button_graph_1.hide()
                self.ui.reset_button_graph_2.hide()
                self.ui.select_button_graph_1.hide()
                self.ui.select_button_graph_2.hide()
                self.ui.connect_online_button_graph_2.hide()
                self.ui.connect_online_button_graph_1.hide()
                self.ui.open_button_graph_2.hide()
                self.ui.open_button_graph_1.hide()
                self.ui.move_to_graph_1_button.hide()
                self.ui.move_to_graph_2_button.hide()
                self.ui.select_button_graph1.hide()
                self.ui.select_button_graph2.hide()
                self.ui.snapshot_button.hide()
                self.ui.snapshot_button_graph2.hide()

                self.timer_graph_1.start(self.speed_graph_1)
                self.timer_graph_2.start(self.speed_graph_1)

            else:
                self.isLinked = False
        else:
            self.un_link_graphs()

    def un_link_graphs(self):
        # Return graphs to play same as before start linking
        if self.play_both:
            if not self.graph1_on:
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
            if not self.graph2_on:
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
        else:
            if self.graph1_on:
                self.timer_graph_1.timeout.connect(self.update_graph1)
            if self.graph2_on:
                self.timer_graph_2.timeout.connect(self.update_graph2)
        self.ui.graph1Widget.graph.sigRangeChanged.disconnect(self.link1_view)
        self.ui.graph2Widget.graph_2.sigRangeChanged.disconnect(self.link2_view)
        self.play_both = False
        # GUI
        self.ui.link_button.setText("Link")
        self.ui.link_play_button.hide()
        self.ui.link_rewind_button.hide()
        self.ui.play_button_graph_1.show()
        self.ui.play_button_graph_2.show()
        self.ui.reset_button_graph_1.show()
        self.ui.reset_button_graph_2.show()
        self.ui.select_button_graph_1.show()
        self.ui.select_button_graph_2.show()
        self.ui.connect_online_button_graph_2.show()
        self.ui.connect_online_button_graph_1.show()
        self.ui.open_button_graph_2.show()
        self.ui.open_button_graph_1.show()
        self.ui.move_to_graph_1_button.show()
        self.ui.move_to_graph_2_button.show()
        self.ui.select_button_graph1.show()
        self.ui.select_button_graph2.show()
        self.ui.snapshot_button.show()
        self.ui.snapshot_button_graph2.show()

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

    def taking_snapshot(self, x):
        snapshot = (
            QPixmap(self.ui.graph1Widget_3.graph.size())
            if x == 3
            else (
                QPixmap(self.ui.graph1Widget.graph.size())
                if x == 1
                else QPixmap(self.ui.graph2Widget.graph_2.size())
            )
        )
        painter = QPainter(snapshot)

        # Render the appropriate graph based on x
        if x == 3:
            self.ui.graph1Widget_3.graph.render(painter)
        elif x == 1:
            self.ui.graph1Widget.graph.render(painter)
        elif x == 2:
            self.ui.graph2Widget.graph_2.render(painter)
        painter.end()

        # Save the snapshot to an image file
        index = len(self.images)  # Get the current index for the snapshot
        snapshot.save(f"graph{x}_snapshot{index}.png")
        self.images.append(
            (x, f"graph{x}_snapshot{index}.png")
        )  # Save a tuple of (graph_number, file_name)
        print(f"Snapshot saved: graph{x}_snapshot{index}.png")

    def PDF_maker(self):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", size=26)
        pdf.cell(200, 35, txt="Signal Glue Report", ln=True, align="C")

        for i, (graph_index, snapshot_file) in enumerate(self.images):

            if i > 0:
                pdf.add_page()
                y_offset = 30 
            else:y_offset = 60 
             
            pdf.image(snapshot_file, x=pdf.get_x()+30, y=y_offset, w=140)  # Adjust x position to center

            if graph_index == 1:
                x_data, y_data = self.graph1_filtered_x, self.graph1_filtered_y
                graph_name = "Graph 1"
            elif graph_index == 2:
                x_data, y_data = self.graph2_filtered_x, self.graph2_filtered_y
                graph_name = "Graph 2"
            elif graph_index == 3:
                x_data, y_data = (
                    self.whole_x_data,
                    self.whole_y_data,
                )  # Glued graph data
                graph_name = "Glued Graph 3"

            mean_value = np.mean(y_data) 
            std_value = np.std(y_data)
            min_value = np.min(y_data)
            max_value = np.max(y_data)
            duration = x_data[-1] - x_data[0]  

            # Add table title for each graph and center it
            pdf.set_xy(10, y_offset + 50) 
            pdf.set_font("Arial", "B", size=14)
            pdf.cell(0, 30, txt=f"Statistics for {graph_name}", ln=True, align="C")  # Center align
            pdf.set_font("Arial", size=10)
            data = [
                ["Mean", f"{mean_value:.2f}"],
                ["Standard Deviation", f"{std_value:.2f}"],
                ["Min Value", f"{min_value:.2f}"],
                ["Max Value", f"{max_value:.2f}"],
                ["Duration", f"{duration:.2f}"],
            ]
            col_width = 100  
            row_height = 15
            pdf.set_x((210 - (col_width * 2)) / 2)  # Center the table
            headers = ["Statistic", "Value"]
            for header in headers:
                pdf.cell(col_width, row_height, header, border=1, align="C")
            pdf.ln(row_height)

            for row in data:
                pdf.set_x((210 - (col_width * 2)) / 2)  # Center each row
                for item in row:
                    pdf.cell(col_width, row_height, item, border=1, align="C")
                pdf.ln(row_height)
        pdf_path = "signal_glue_report.pdf"
        pdf.output(pdf_path)

        if os.path.exists(pdf_path):
            print(f"Report generated and saved at: {pdf_path}")
        else:
            print(f"Error: PDF report was not saved at {pdf_path}")

    def show_non_rectangle_plot(self):
        self.non_rectangle_plot = nonRectanglePlotWindow()
        self.non_rectangle_plot.show()

    def select_graph_to_cut_2(self):
        if self.is_file2_opened == True:
            self.ui.graph2Widget.graph_2.addItem(self.rect_roi)
            self.ui.select_button_graph_2.clicked.connect(self.on_select_2)

    def select_graph_to_cut(self):
        if self.is_file1_opened == True:
            self.ui.graph1Widget.graph.addItem(self.rect_roi)
            self.ui.select_button_graph_1.clicked.connect(self.on_select)
            

     # Make sure NumPy is imported

    def on_select(self):
        """Handles the selection event"""
        pos = self.rect_roi.pos()  # Position (top-left corner)
        size = self.rect_roi.size()  # Size of the rectangle (width, height)
        left = pos.x()  # x-axis (time/sample) start
        right = pos.x() + size[0]  # x-axis (time/sample) end
        top = pos.y()  # y-axis (amplitude) start
        bottom = pos.y() + size[1]  # y-axis (amplitude) end
        print(f"Rectangle bounds - Left: {left}, Right: {right}, Top: {top}, Bottom: {bottom}")
        x_data = self.graph_1.previous_x_dataa  
        y_data = self.graph_1.previous_signal_pointss  
        left_idx = 0
        right_idx = 0

        # Find the nearest index to 'left'
 
        for i, x in enumerate(x_data):
            if x >= left:  
                left_idx = i
                break  

        # Find the nearest index to 'right'
        for i, x in enumerate(x_data):
            if x >= right:  # As soon as you hit or exceed the right boundary, take the index
                right_idx = i
                break  # Exit the loop as soon as the condition is met


        # Ensure right_idx is greater than left_idx
        right_idx = max(right_idx, left_idx + 1)

        # Slice the x and y data based on the approximated x-axis selection
        selected_x = x_data[left_idx:right_idx+1]
        selected_y = y_data[left_idx:right_idx+1]

        # Debug: Print the selected x and y data range
        print(f"Selected x data: {selected_x[:5]}")  # Print the first 5 values for verification
        print(f"Selected y data: {selected_y[:5]}")


        left_value = selected_x[0]

        filtered_selected_x = []
        filtered_selected_y = []

        for x, y in zip(selected_x, selected_y):
            if (
                x >= left_value
            ):  # Keep only x values greater than or equal to left_value
                filtered_selected_x.append(x)
                filtered_selected_y.append(y)

        # Debug: Print the filtered x and y data
        print(f"Filtered x values: {filtered_selected_x[:5]}")
        print(f"Filtered y values: {filtered_selected_y[:5]}")


     
        # 2. Filter y-data based on the selected y-range (top to bottom) and ensure one-to-one mapping with x
        

        # Use a dictionary to store only one y-value per x-value
        unique_data = {}



        # Iterate through both x and y data simultaneously
        for i, (x, y) in enumerate(zip(filtered_selected_x, filtered_selected_y)):
            if top <= y <= bottom:  # Filter y-values within the y-axis range
                if x not in unique_data:  # Only keep the first occurrence of x
                    unique_data[x] = y

        # Convert the dictionary back to two lists
        self.graph1_filtered_x = list(unique_data.keys())
        self.graph1_filtered_y = list(unique_data.values())

        # Debug: Print the filtered x and y data
        print(f"Filtered x values: {self.graph1_filtered_x[10:10]}")
        print(f"Filtered y values: {self.graph1_filtered_y[10:20]}")


        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.ui.graph1Widget_3.graph.addItem(self.zero_line)


        self.graph1_plot= self.ui.graph1Widget_3.graph.plot(self.graph1_filtered_x, self.graph1_filtered_y, pen=pg.mkPen(self.cutted_signal_color_graph1, width=1))

       

        # Store and print the selected range for verification
        self.selected_range = (left, right, top, bottom)
        print(f"Selected range: {self.selected_range}")

    def on_select_2(self):
        pos = self.rect_roi.pos()  # Position (top-left corner)
        size = self.rect_roi.size()  # Size of the rectangle (width, height)
        left = pos.x()  # x-axis (time/sample) start
        right = pos.x() + size[0]  # x-axis (time/sample) end
        top = pos.y()  # y-axis (amplitude) start
        bottom = pos.y() + size[1]  # y-axis (amplitude) end

        # Debug: Print the selected rectangle bounds
        print(f"Rectangle bounds - Left: {left}, Right: {right}, Top: {top}, Bottom: {bottom}")

        # 1. Slice the x-data range
        x_data = self.graph_2.previous_x_dataa # Original x-data
        y_data = self.graph_2.previous_signal_pointss  # Original y-data
        left_idx = 0
        right_idx = 0
        for i, x in enumerate(x_data):
            if x >= left:  # As soon as you hit or exceed the left boundary, take the index
                left_idx = i
                break 
        for i, x in enumerate(x_data):
            if x >= right:  # As soon as you hit or exceed the right boundary, take the index
                right_idx = i
                break  # Exit the loop as soon as the condition is met


        # Ensure right_idx is greater than left_idx
        right_idx = max(right_idx, left_idx + 1)
        # Slice the x and y data based on the approximated x-axis selection
        selected_x = x_data[left_idx:right_idx]
        selected_y = y_data[left_idx:right_idx]

       


        left_value = selected_x[0]
        filtered_selected_x = []
        filtered_selected_y = []
        for x, y in zip(selected_x, selected_y):
            if x >= left_value:  # Keep only x values greater than or equal to left_value
                filtered_selected_x.append(x)
                filtered_selected_y.append(y)

        # Debug: Print the filtered x and y data
        


     
        # 2. Filter y-data based on the selected y-range (top to bottom) and ensure one-to-one mapping with x
        

        # Use a dictionary to store only one y-value per x-value
        unique_data = {}



        # Iterate through both x and y data simultaneously
        for i, (x, y) in enumerate(zip(filtered_selected_x, filtered_selected_y)):
            if top <= y <= bottom: 
                if x not in unique_data: 
                    unique_data[x] = y
        # Convert the dictionary back to two lists
        self.graph2_filtered_x = list(unique_data.keys())
        self.graph2_filtered_y = list(unique_data.values())

        # Debug: Print the filtered x and y data
        
        print(f"Filtered y values: {self.graph2_filtered_y[:5]}")
        print(f"Filtered X values: {self.graph2_filtered_x[:5]}")


        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.ui.graph1Widget_3.graph.addItem(self.zero_line)


        self.graph2_plot=self.ui.graph1Widget_3.graph.plot(self.graph2_filtered_x, self.graph2_filtered_y, pen=pg.mkPen(self.cutted_signal_color_graph2, width=1))
        

    def on_slider_change(self, value):
         # Fixed amount to shift the graph
        shift_amount = 0.01  # Fixed amount to shift the graph
        self.total_shifed_glue_slider =  value * shift_amount  # Update the total shift amount
        
        # Shift x-data by the total shift amount
        self.x_shifted = [x + self.total_shifed_glue_slider for x in self.graph1_filtered_x]
        # Clear the previous plot before re-plotting
        self.graph1_plot.clear()  # Clear the previous plot
        self.graph1_plot = self.ui.graph1Widget_3.graph.plot(self.x_shifted, self.graph1_filtered_y, pen=pg.mkPen(self.cutted_signal_color_graph1, width=1))

        self.graph1_end_x = self.x_shifted[-1]
        self.graph1_start_x = self.x_shifted[0]
        self.graph1_end_y = self.graph1_filtered_y[-1]
        self.graph1_start_y = self.graph1_filtered_y[0]
        self.graph2_start_x = self.graph2_filtered_x[0]
        self.graph2_end_x = self.graph2_filtered_x[-1]
        self.graph2_start_y = self.graph2_filtered_y[0]
        self.graph2_end_y = self.graph2_filtered_y[-1]

    def on_glue_button_click(self):
        # Get the interpolation method from the user (linear, cubic, etc.)
        interpolation_order=self.ui.comboBox.currentText()

        x1_end = self.graph1_end_x  
        y1_end=self.graph1_end_y
        x1_start=self.graph1_start_x
        y1_start=self.graph1_start_y
        x2_start = self.graph2_start_x
        y2_start = self.graph2_start_y
        x2_end = self.graph2_end_x
        y2_end = self.graph2_end_y

        if x1_end < x2_start:  # Gap detected, interpolate
            x_new = np.linspace(
                x1_end, x2_start, num=100
            )  # Generate new x points between graph 1 and 2

            if interpolation_order == "linear":
                f = interpolate.interp1d(
                    [x1_end, x2_start], [y1_end, y2_start], kind="linear"
                )

            elif interpolation_order == "cubic":
                f = interpolate.interp1d(
                    [x1_end, x2_start, x1_start, x2_end],
                    [y1_end, y2_start, y1_start, y2_end],
                    kind="cubic",
                )
            else:
                self.status_label.setText("Invalid interpolation order")
                return

            y_new = f(x_new)  # Get the interpolated y values
            self.whole_x_data = list(self.graph1_filtered_x) + list(x_new) + list(self.graph2_filtered_x)
            self.whole_y_data = list(self.graph1_filtered_y) + list(y_new) + list(self.graph2_filtered_y)
            
            self.ui.graph1Widget_3.graph.plot(x_new, y_new, pen=pg.mkPen('w', width=1))
            

        else:  


            # Finding overlap and separating non-overlapping parts
            overlap_x = np.intersect1d(self.x_shifted, self.graph2_filtered_x)

            # Remove overlapping points and keep non-overlapping parts from both graphs
            graph1_non_overlap_x = [x for x in self.x_shifted if x not in overlap_x]
            graph1_non_overlap_y = [
                self.graph1_filtered_y[self.x_shifted.index(x)]
                for x in graph1_non_overlap_x
            ]

            graph2_non_overlap_x = [x for x in self.graph2_filtered_x if x not in overlap_x]
            graph2_non_overlap_y = [
                self.graph2_filtered_y[self.graph2_filtered_x.index(x)]
                for x in graph2_non_overlap_x
            ]

            # Interpolate the overlapping part
            overlap_y1 = np.interp(overlap_x, self.x_shifted, self.graph1_filtered_y)
            overlap_y2 = np.interp(overlap_x, self.graph2_filtered_x, self.graph2_filtered_y)
            averaged_y = (overlap_y1 + overlap_y2) / 2  # Average the y values of the overlap

            # Ensure the continuity by connecting the end of graph1 to the overlap
            # Get the last point of graph1_non_overlap and first point of overlap to connect
            if graph1_non_overlap_x:
                last_x_graph1 = graph1_non_overlap_x[-1]
                last_y_graph1 = graph1_non_overlap_y[-1]
                first_x_overlap = overlap_x[0]
                first_y_overlap = averaged_y[0]

                # Ensure continuity by setting last x, y of graph1 to first of overlap if they differ
                if last_x_graph1 != first_x_overlap or last_y_graph1 != first_y_overlap:
                    graph1_non_overlap_x.append(first_x_overlap)
                    graph1_non_overlap_y.append(first_y_overlap)

            # Ensure the continuity by connecting the end of the overlap to graph2
            # Get the last point of overlap and first point of graph2_non_overlap to connect
            if graph2_non_overlap_x:
                last_x_overlap = overlap_x[-1]
                last_y_overlap = averaged_y[-1]
                first_x_graph2 = graph2_non_overlap_x[0]
                first_y_graph2 = graph2_non_overlap_y[0]

                # Ensure continuity by setting last x, y of overlap to first of graph2 if they differ
                if last_x_overlap != first_x_graph2 or last_y_overlap != first_y_graph2:
                    graph2_non_overlap_x.insert(0, last_x_overlap)
                    graph2_non_overlap_y.insert(0, last_y_overlap)

            # Combine all x and y values into a single list
            self.whole_x_data = graph1_non_overlap_x + list(overlap_x) + graph2_non_overlap_x
            self.whole_y_data = graph1_non_overlap_y + list(averaged_y) + graph2_non_overlap_y

            # Sort the data based on x values
            self.whole_x_data, self.whole_y_data = zip(*sorted(zip(self.whole_x_data, self.whole_y_data)))

            # Remove duplicates by creating a dictionary
            unique_data = {}
            for x, y in zip(self.whole_x_data, self.whole_y_data):
                if x not in unique_data:
                    unique_data[x] = y

            # Convert the dictionary back to two lists
            self.whole_x_data = list(unique_data.keys())
            self.whole_y_data = list(unique_data.values())

            # Clear the previous plot
            self.ui.graph1Widget_3.graph.clear()

            # Plot the segments with different colors
            self.ui.graph1Widget_3.graph.plot(graph1_non_overlap_x, graph1_non_overlap_y, pen=pg.mkPen(self.cutted_signal_color_graph1, width=1))
            self.ui.graph1Widget_3.graph.plot(overlap_x, averaged_y, pen=pg.mkPen('w', width=1))  # Overlap in white
            self.ui.graph1Widget_3.graph.plot(graph2_non_overlap_x, graph2_non_overlap_y, pen=pg.mkPen(self.cutted_signal_color_graph2, width=1))

            # Disconnect the slider signal to prevent further changes during glue operation
            self.ui.slider_glue.valueChanged.disconnect(self.on_slider_change)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = MainWindow()
    ui.show()
    app.exec_()
