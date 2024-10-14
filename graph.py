import pyqtgraph as pg
import numpy as np
from signal_1 import SignalProcessor
from PyQt5.QtCore import QTimer
import copy
class Graph:
    def __init__(self, graph_widget):
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')        
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.signals = {}  # Track signal plot items and their visibility status
        self.signal_processor = None
        self.second_time = False
        # self.timer = QTimer()  # Initialize a timer for the graph
        # self.timer.timeout.connect(self.update_graph)  # Connect the timer to update_graph method
        # self.timer.start(100)  # Set the interval for updates (in milliseconds)
        

    def add_signal(self, name, color):
        """Add a new signal to the graph."""
        if name not in self.signals:  # Avoid duplicate signals
            plot_item = self.plot_widget.plot([], [], pen=pg.mkPen(color), name=name)
            # self.signals[name] = (self.signal_processor, plot_item, self.plot_widget)
            self.signals[name] = {
                'processor': self.signal_processor,  # Store the SignalProcessor instance
                'item': plot_item,                   # Store the plot item
                'visible': True                       # Store visibility status
            }  # Track visibility

    def toggle_signal_visibility(self, name, visible):
        """Toggle visibility of a specific signal."""
        if name in self.signals:
            self.signals[name]['item'].setVisible(visible)
            self.signals[name]['visible'] = visible

    def update_graph(self, data, current_index, window_width, graph1_color):
        if data is not None:
            # Clear the previous plot before replotting
            # self.plot_widget.clear()
            if self.zero_line not in self.plot_widget.items():
                self.plot_widget.addItem(self.zero_line)  # Add the zero line back  
            
            
            # Create x-axis data for plotting based on current_index
            new_x_data = np.arange(current_index, current_index + len(data)) * 0.001  # 0.001 assumes 1 unit is 1 ms
            previous_x_data = np.arange(0, current_index) * 0.001

            # Update the visible signals with the new data
            for signal_name, signal_info in self.signals.items():
                if signal_info['visible']:  # Only update visible signals
                    # get current data
                    if self.second_time:
                        x_data, y_data = signal_info['item'].getData()
                        self.second_time = True
                    else:
                        self.second_time = True
                        x_data = None
                        y_data = None    
                    if x_data is None or y_data is None:
                        x_data = np.array([])  # Initialize as empty arrays
                        y_data = np.array([])

                    x_data = np.append(x_data, new_x_data)
                    y_data = np.append(y_data, data)
                    # data = np.resize(data, len(x_data))  # Resize y_data to match x_data

                    signal_info['item'].setData(x=previous_x_data, y=data)
                    # signal_info['item'].setData(x=new_x_data, y=data)  # Keep this line to update signals



            # Adjust the x-axis to fit all data seen so far
            start_x = max(0, (current_index - window_width) * 0.001)  # Start of the x-range
            end_x = (current_index + len(data)) * 0.001               # End of the x-range
            self.plot_widget.setXRange(start_x, end_x)


    def remove_signal(self, name):
        """Remove a signal from the graph by its name."""
        if name in self.signals:
            self.plot_widget.removeItem(self.signals[name]['item'])  # Remove the plot item from the widget
            del self.signals[name]  # Delete from the signals dictionary

    # In the Graph class
    def move_signal_to_another_graph(self, name, color):
        """Move a signal from this graph to another graph."""
        if name in self.signals:
            # Stop the timer for this graph if it is active
            if self.timer.isActive():
                self.timer.stop()

            # Retrieve the SignalProcessor for the current signal
            signal_processor = self.signals[name]['processor']
            
            # Remove the signal from this graph
            self.remove_signal(name)

            # Prepare the new signal data
            new_processor = SignalProcessor(self.plot_widget)
            new_processor.data = signal_processor.data.copy()  # Assuming data is a numpy array
            new_processor.current_index = signal_processor.current_index

            # Return the new processor and the color for updating the target graph
            return new_processor, color
        return None, None  # Return None if the signal does not exist
