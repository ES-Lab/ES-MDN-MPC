from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
import PyQt5.QtCore as QtCore
import pyqtgraph as pg
import numpy as np
import seaborn as sns


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.FONT = QFont("Microsoft JhengHei", 8) # QFont.Bold

        # Create a central widget
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: white;")
        self.setCentralWidget(self.central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        # Create a graphics layout widget
        self.graphics_layout = pg.GraphicsLayoutWidget()
        self.graphics_layout.setBackground('w')
        layout.addWidget(self.graphics_layout)
        
        # Initialize subplots
        self.plot_items = []
        self.curves = []
        self.fills = []
        self.v_lines = []

        # Get Seaborn color palette
        sns_colors = sns.color_palette("deep", 10).as_hex()
        for i in range(4): sns_colors[i] = '#f74639'
        sns_colors[4] = '#0061FF' 
        sns_colors[5] = '#FF1B00'
        sns_colors[6] = '#FFCD00'
        sns_colors[7] = '#35FF6C'
        sns_colors[8] = '#989898'
        sns_colors[9] = '#000000'

        # Generate initial data
        self.x = np.linspace(0, 24, 24*4, endpoint=False)
        self.current_heights = 0

        # Create the 3-column layout with titles and labels
        for i in range(4):
            plot_item = self.graphics_layout.addPlot(row=i, col=0)
            self.plot_items.append(plot_item)
            curve = plot_item.plot(pen=pg.mkPen(color=sns_colors[i], width=2))
            self.curves.append(curve)
            fill = pg.FillBetweenItem(curve, pg.PlotCurveItem(self.x, np.zeros_like(self.x)), brush=sns_colors[i] + '40')
            plot_item.addItem(fill)
            self.fills.append(fill)
            v_line = pg.InfiniteLine(pos=24, angle=90, pen=pg.mkPen(color='gray', style=QtCore.Qt.DashLine))
            plot_item.addItem(v_line)
            self.v_lines.append(v_line)

            # plot_item.getViewBox().setBackgroundColor('w')
            plot_item.showGrid(x=True, y=True, alpha=0.1)
            plot_item.setYRange(0, 11000, padding=0.1)
            plot_item.getAxis('left').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('left').setStyle(tickFont=self.FONT)
            plot_item.getAxis('left').label.setFont(self.FONT)
            plot_item.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('bottom').setStyle(tickFont=self.FONT)
            plot_item.getAxis('bottom').label.setFont(self.FONT)
            plot_item.setTitle(f'Charger {i+1}', color='black', size='10pt')
            plot_item.titleLabel.item.setFont(self.FONT)
            plot_item.setLabel('left', 'Power', units='W', color='black', size='10pt')
        plot_item.setLabel('bottom', 'Time', units='h', color='black', size='10pt')

        titles = ['Main Grid Power', 'Battery Power']
        ranges = np.array([[0,20000, 0.1], [-5000, 5000, 0.1]])
        for i in range(2):
            plot_item = self.graphics_layout.addPlot(row=2*i, col=1, rowspan=2)
            self.plot_items.append(plot_item)
            curve = plot_item.plot(pen=pg.mkPen(color=sns_colors[4 + i], width=2))
            self.curves.append(curve)
            fill = pg.FillBetweenItem(curve, pg.PlotCurveItem(self.x, np.zeros_like(self.x)), brush=sns_colors[4 + i] + '40')
            plot_item.addItem(fill)
            self.fills.append(fill)
            v_line = pg.InfiniteLine(pos=24, angle=90, pen=pg.mkPen(color='gray', style=QtCore.Qt.DashLine))
            plot_item.addItem(v_line)
            self.v_lines.append(v_line)

            # plot_item.getViewBox().setBackgroundColor('w')
            plot_item.showGrid(x=True, y=True, alpha=0.1)
            plot_item.setYRange(ranges[i,0], ranges[i,1], padding=ranges[i,2])
            plot_item.getAxis('left').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('left').setStyle(tickFont=self.FONT)
            plot_item.getAxis('left').label.setFont(self.FONT)
            plot_item.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('bottom').setStyle(tickFont=self.FONT)
            plot_item.getAxis('bottom').label.setFont(self.FONT)
            plot_item.setTitle(titles[i], color='black', size='10pt')
            plot_item.titleLabel.item.setFont(self.FONT)
            plot_item.setLabel('left', 'Power', units='W', color='black', size='10pt')
        plot_item.setLabel('bottom', 'Time', units='h', color='black', size='10pt')

        titles = ['PV measurement', 'Battery SoC']
        labels = ['Power', 'SoC']
        units = ['W', '%']
        ranges = np.array([[0,22000, 0.1], [0, 1, 0.1]])
        for i in range(2):
            plot_item = self.graphics_layout.addPlot(row=2*i, col=2, rowspan=2)
            self.plot_items.append(plot_item)
            curve = plot_item.plot(pen=pg.mkPen(color=sns_colors[6 + i], width=2))
            self.curves.append(curve)
            fill = pg.FillBetweenItem(curve, pg.PlotCurveItem(self.x, np.zeros_like(self.x)), brush=sns_colors[6 + i] + '40')
            plot_item.addItem(fill)
            self.fills.append(fill)
            v_line = pg.InfiniteLine(pos=24, angle=90, pen=pg.mkPen(color='gray', style=QtCore.Qt.DashLine))
            plot_item.addItem(v_line)
            self.v_lines.append(v_line)

            # plot_item.getViewBox().setBackgroundColor('w')
            plot_item.showGrid(x=True, y=True, alpha=0.1)
            plot_item.setYRange(ranges[i,0], ranges[i,1], padding=ranges[i,2])
            plot_item.getAxis('left').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('left').setStyle(tickFont=self.FONT)
            plot_item.getAxis('left').label.setFont(self.FONT)
            plot_item.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=1))
            plot_item.getAxis('bottom').setStyle(tickFont=self.FONT)
            plot_item.getAxis('bottom').label.setFont(self.FONT)
            plot_item.setTitle(titles[i], color='black', size='10pt')
            plot_item.titleLabel.item.setFont(self.FONT)
            plot_item.setLabel('left', labels[i], units=units[i], color='black', size='10pt')
        plot_item.setLabel('bottom', 'Time', units='h', color='black', size='10pt')
        


        # Electricivity Price
        i = 0
        plot_item = self.graphics_layout.addPlot(row=2*i, col=3, rowspan=2)
        self.plot_items.append(plot_item)
        curve = plot_item.plot(pen=pg.mkPen(color=sns_colors[8 + i], width=2))
        self.curves.append(curve)
        fill = pg.FillBetweenItem(curve, pg.PlotCurveItem(self.x, np.zeros_like(self.x)), brush=sns_colors[8 + i] + '40')
        plot_item.addItem(fill)
        self.fills.append(fill)
        v_line = pg.InfiniteLine(pos=24, angle=90, pen=pg.mkPen(color='gray', style=QtCore.Qt.DashLine))
        plot_item.addItem(v_line)
        self.v_lines.append(v_line)

        # plot_item.getViewBox().setBackgroundColor('w')
        plot_item.showGrid(x=True, y=True, alpha=0.1)
        # plot_item.setYRange(ranges[i,0], ranges[i,1], padding=ranges[i,2])
        plot_item.getAxis('left').setPen(pg.mkPen(color='#000000', width=1))
        plot_item.getAxis('left').setStyle(tickFont=self.FONT)
        plot_item.getAxis('left').label.setFont(self.FONT)
        plot_item.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=1))
        plot_item.getAxis('bottom').setStyle(tickFont=self.FONT)
        plot_item.getAxis('bottom').label.setFont(self.FONT)
        plot_item.setTitle('Electricity Price', color='black', size='10pt')
        plot_item.titleLabel.item.setFont(self.FONT)
        plot_item.setLabel('left', 'Price', units='€/kW', color='black', size='10pt')
        plot_item.setLabel('bottom', 'Time', units='h', color='black', size='10pt')


        # deman plot
        i = 1
        plot_item = self.graphics_layout.addPlot(row=2*i, col=3, rowspan=2)
        self.plot_items.append(plot_item)
        self.bars = pg.BarGraphItem(x=np.arange(4), height=self.current_heights, width=0.6, brush='b')
        plot_item.addItem(self.bars)
        
        plot_item.showGrid(x=True, y=True, alpha=0.1)
        plot_item.setYRange(0, 50, padding=0.1)
        plot_item.getAxis('left').setPen(pg.mkPen(color='#000000', width=1))
        plot_item.getAxis('left').setStyle(tickFont=self.FONT)
        plot_item.getAxis('left').label.setFont(self.FONT)
        plot_item.getAxis('bottom').setPen(pg.mkPen(color='#000000', width=1))
        plot_item.getAxis('bottom').setStyle(tickFont=self.FONT)
        plot_item.getAxis('bottom').label.setFont(self.FONT)
        plot_item.setTitle('EV Demands', color='black', size='10pt')
        plot_item.titleLabel.item.setFont(self.FONT)
        plot_item.setLabel('left', 'Energy', units='kW', color='black', size='10pt')
        plot_item.setLabel('bottom', 'Charger', units=None, color='black', size='10pt')

        # Set window title and size
        self.setWindowTitle("Slimer Park Live Dashboard")
        self.resize(1400, 800)

    def update_demands(self, target_heights):
        # Smooth transition parameters
        transition_speed = 0.2

        # Compute the difference between current and target heights
        difference = target_heights - self.current_heights

        # Adjust heights smoothly
        step = difference * transition_speed
        self.current_heights += step

        # Update bar heights
        self.bars.setOpts(height=self.current_heights)
