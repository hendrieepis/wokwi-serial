import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QComboBox, QPushButton, QLabel, QStatusBar,
                            QTabWidget)
import pyqtgraph as pg


class SerialMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle("Advanced Sensor Monitor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Apply modern style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QComboBox, QPushButton {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #4e5254;
            }
            QPushButton:pressed {
                background-color: #2d2f30;
            }
            QStatusBar {
                background-color: #3c3f41;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2b2b2b;
            }
            QTabBar::tab {
                background: #3c3f41;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                border-bottom: 2px solid #6bbfde;
            }
        """)
        
        # Top control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Serial port selection
        self.port_label = QLabel("Serial Port:")
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        # Baud rate selection
        self.baud_label = QLabel("Baud Rate:")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("9600")
        
        # Connect/disconnect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # Add widgets to control panel
        control_layout.addWidget(self.port_label)
        control_layout.addWidget(self.port_combo)
        control_layout.addWidget(self.baud_label)
        control_layout.addWidget(self.baud_combo)
        control_layout.addWidget(self.connect_btn)
        control_layout.addStretch()
        
        # Add control panel to main layout
        main_layout.addWidget(control_panel)
        
        # Create tab widget for different views
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab 1: Real-time Graphs
        self.graph_tab = QWidget()
        self.tabs.addTab(self.graph_tab, "Real-time Graphs")
        
        # Setup graphs layout
        graph_layout = QVBoxLayout(self.graph_tab)
        
        # Create pyqtgraph widgets with dark theme
        pg.setConfigOption('background', '#2b2b2b')
        pg.setConfigOption('foreground', 'w')
        
        # Temperature graph
        self.temp_graph = pg.PlotWidget(title="Temperature")
        self.temp_graph.setLabel('left', 'Value')
        self.temp_graph.setLabel('bottom', 'Time (s)')
        self.temp_graph.addLegend()
        self.temp_curve = self.temp_graph.plot(pen=pg.mkPen(color=(255, 100, 100)), name="Temperature")
        
        # Humidity graph
        self.humidity_graph = pg.PlotWidget(title="Humidity")
        self.humidity_graph.setLabel('left', 'Value')
        self.humidity_graph.setLabel('bottom', 'Time (s)')
        self.humidity_graph.addLegend()
        self.humidity_curve = self.humidity_graph.plot(pen=pg.mkPen(color=(100, 255, 100)), name="Humidity")
        
        # Light graph
        self.light_graph = pg.PlotWidget(title="Light Intensity")
        self.light_graph.setLabel('left', 'Value')
        self.light_graph.setLabel('bottom', 'Time (s)')
        self.light_graph.addLegend()
        self.light_curve = self.light_graph.plot(pen=pg.mkPen(color=(100, 100, 255)), name="Light")
        
        # Add graphs to layout
        graph_layout.addWidget(self.temp_graph)
        graph_layout.addWidget(self.humidity_graph)
        graph_layout.addWidget(self.light_graph)
        
        # Tab 2: Raw Data
        self.raw_data_tab = QWidget()
        self.tabs.addTab(self.raw_data_tab, "Raw Data")
        
        # Setup raw data layout
        raw_data_layout = QVBoxLayout(self.raw_data_tab)
        
        # Raw data display
        self.raw_data_display = QtWidgets.QTextEdit()
        self.raw_data_display.setReadOnly(True)
        self.raw_data_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: Consolas, Courier New, monospace;
                font-size: 12px;
                border: 1px solid #444;
            }
        """)
        
        # Data statistics
        stats_layout = QHBoxLayout()
        
        self.temp_stat = QLabel("Temperature: --")
        self.humidity_stat = QLabel("Humidity: --")
        self.light_stat = QLabel("Light: --")
        
        stats_layout.addWidget(self.temp_stat)
        stats_layout.addWidget(self.humidity_stat)
        stats_layout.addWidget(self.light_stat)
        stats_layout.addStretch()
        
        raw_data_layout.addLayout(stats_layout)
        raw_data_layout.addWidget(self.raw_data_display)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")
        
        # Serial connection
        self.serial = None
        self.is_connected = False
        
        # Data storage
        self.time_data = []
        self.temp_data = []
        self.humidity_data = []
        self.light_data = []
        self.max_points = 100  # Number of points to display
        
        # Timer for reading serial data
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        
        # Timer for updating graphs
        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graphs)
        self.graph_timer.start(100)  # Update graphs every 100ms
        
        # Start time
        self.start_time = QtCore.QDateTime.currentDateTime()
        
    def refresh_ports(self):
        """Refresh available serial ports including virtual tty0tty"""
        self.port_combo.clear()
        
        # Prioritaskan virtual ports tty0tty (tnt*) di awal list
        virtual_ports = [f"/dev/tnt{i}" for i in range(8)]  # Contoh: /dev/tnt0 sampai tnt7
        for vport in virtual_ports:
            self.port_combo.addItem(vport)
        
        # Tambahkan port fisik yang terdeteksi
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.device not in virtual_ports:
                self.port_combo.addItem(port.device)
    
    def toggle_connection(self):
        """Toggle serial connection"""
        if self.is_connected:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        
        try:
            # Konfigurasi khusus untuk virtual port
            self.serial = serial.Serial(
                port=port,
                baudrate=baud,
                timeout=1,
                # Parameter penting untuk virtual port
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                # Nonaktifkan kontrol flow
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )
            
            # Untuk virtual port, biasanya tidak perlu set DTR/RTS
            self.serial.dtr = False
            self.serial.rts = False
            
            self.is_connected = True
            self.connect_btn.setText("Disconnect")
            self.status_bar.showMessage(f"Connected to VIRTUAL PORT {port} at {baud} baud")
            self.timer.start(10)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Virtual Port Error", 
                f"Failed to connect to {port}:\n{str(e)}\n\n"
                "Pastikan:\n"
                "1. Modul tty0tty sudah terload (lsmod | grep tty0tty)\n"
                "2. Port virtual ada (ls /dev/tnt*)"
            )
    
    def disconnect_serial(self):
        """Disconnect from serial port"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
        self.connect_btn.setText("Connect")
        self.status_bar.showMessage("Disconnected")
        self.timer.stop()
    
    def read_serial_data(self):
        """Read and process incoming serial data"""
        if self.serial and self.serial.in_waiting:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if line:
                    self.raw_data_display.append(line)
                    
                    # Parse CSV data (temperature,humidity,light)
                    parts = line.split(',')
                    if len(parts) == 3:
                        try:
                            temp = float(parts[0])
                            humidity = float(parts[1])
                            light = float(parts[2])
                            
                            # Get current time in seconds since start
                            current_time = self.start_time.msecsTo(QtCore.QDateTime.currentDateTime()) / 1000.0
                            
                            # Store data
                            self.time_data.append(current_time)
                            self.temp_data.append(temp)
                            self.humidity_data.append(humidity)
                            self.light_data.append(light)
                            
                            # Keep only the most recent points
                            if len(self.time_data) > self.max_points:
                                self.time_data.pop(0)
                                self.temp_data.pop(0)
                                self.humidity_data.pop(0)
                                self.light_data.pop(0)
                            
                            # Update statistics
                            self.temp_stat.setText(f"Temperature: {temp:.1f}")
                            self.humidity_stat.setText(f"Humidity: {humidity:.1f}")
                            self.light_stat.setText(f"Light: {light:.1f}")
                            
                        except ValueError:
                            pass  # Ignore lines that can't be parsed
            except UnicodeDecodeError:
                pass  # Ignore incomplete data
    
    def update_graphs(self):
        """Update the graphs with new data"""
        if len(self.time_data) > 0:
            # Update temperature graph
            self.temp_curve.setData(self.time_data, self.temp_data)
            
            # Update humidity graph
            self.humidity_curve.setData(self.time_data, self.humidity_data)
            
            # Update light graph
            self.light_curve.setData(self.time_data, self.light_data)
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.disconnect_serial()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme palette
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(43, 43, 43))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
    
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec_())