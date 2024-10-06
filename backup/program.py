import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

from main_gui import Ui_MainWindow
from signal_1 import SignalProcessor
from graph import Graph

class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Set up the UI components

        # Initialize SignalProcessor and Graph
        self.signal_processor = SignalProcessor()
        self.graph_1 = Graph(self.graph1Widget, self.graph2Widget)
        self.graph_2 = Graph(self.graph1Widget, self.graph2Widget)
        
        # Connect the button to open_file function
        self.open_button_graph_1.clicked.connect(self.open_file)
        self.open_button_graph_2.clicked.connect(self.open_file)
        
        # Set up the timer for updating the graph
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        
        self.window_width = 100  # Number of points to show in the window at a time

    def open_file(self):
        self.signal_processor.open_file(self)
        if self.signal_processor.data is not None:
            self.timer.start(500)  # Start timer with interval in ms

    def update_graph(self):  # Ensure this method is indented correctly within the class
        data = self.signal_processor.get_next_data(self.window_width)
        if data is not None:
            # Update graph 1 with scrolling x-axis
            self.graph_1.update_graph(data, self.signal_processor.current_index, self.window_width)
            # Update graph 2 with scrolling x-axis
            self.graph_2.update_graph(data, self.signal_processor.current_index, self.window_width)
        else:
            self.timer.stop()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

