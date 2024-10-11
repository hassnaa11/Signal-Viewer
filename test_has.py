import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

app = QtWidgets.QApplication([])

# Create a main window and a layout
win = pg.GraphicsLayoutWidget(show=True, title="Zoom/Scroll Sync Example")
layout = QtWidgets.QVBoxLayout()

# Create two plots
plot1 = pg.PlotWidget()
plot2 = pg.PlotWidget()

# Add some data to the plots
curve1 = plot1.plot([1, 2, 3, 4, 5], [10, 1, 3, 7, 4])
curve2 = plot2.plot([1, 2, 3, 4, 5], [4, 9, 2, 5, 8])

# Function to sync the zoom and scroll between two plots
def link_views(source_plot, target_plot):
    def update_view():
        # Get the view range of the source plot and apply it to the target plot
        target_plot.setXRange(*source_plot.getViewBox().viewRange()[0], padding=0)
        target_plot.setYRange(*source_plot.getViewBox().viewRange()[1], padding=0)

    # Connect the view range change signal to update the other plot
    source_plot.sigRangeChanged.connect(update_view)
    
    # Store the connection function for later disconnection
    return update_view

# Link the views between the two plots and store the connection functions
link1 = link_views(plot1, plot2)
link2 = link_views(plot2, plot1)  # Make the linking bidirectional

# Function to unlink the views
def unlink_views():
    # Disconnect the signals for both plots
    plot1.sigRangeChanged.disconnect(link1)
    plot2.sigRangeChanged.disconnect(link2)

# Create a button to unlink the views
button = QtWidgets.QPushButton('Unlink Views')
button.clicked.connect(unlink_views)

# Add the plots and button to the layout
layout.addWidget(plot1)
layout.addWidget(plot2)
layout.addWidget(button)

# Create a QWidget to hold the layout
container = QtWidgets.QWidget()
container.setLayout(layout)

# Show the main window
container.show()

# Start the Qt event loop
QtWidgets.QApplication.instance().exec_()
