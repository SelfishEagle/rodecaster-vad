#!/usr/bin/env python3
"""
RØDECaster Control Panel - Simple & Stable Version
"""

import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class SimpleControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RØDECaster Control Panel")
        self.setGeometry(100, 100, 600, 400)
        
        # Simple styling
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QLabel { color: white; font-size: 14px; }
            QPushButton { 
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        
        self.init_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        self.update_status()
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("RØDECaster Pro 2 Control Panel")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Checking status...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addSpacing(20)
        
        # Service controls
        group = QGroupBox("Service Control")
        group.setStyleSheet("QGroupBox { color: white; font-size: 14px; }")
        group_layout = QVBoxLayout()
        
        start_btn = QPushButton("▶ Start Service")
        start_btn.clicked.connect(self.start_service)
        group_layout.addWidget(start_btn)
        
        restart_btn = QPushButton("🔄 Restart Service")
        restart_btn.clicked.connect(self.restart_service)
        group_layout.addWidget(restart_btn)
        
        stop_btn = QPushButton("⏹ Stop Service")
        stop_btn.clicked.connect(self.stop_service)
        group_layout.addWidget(stop_btn)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addSpacing(20)
        
        # Quick actions
        pavucontrol_btn = QPushButton("🎛 Open PulseAudio Mixer")
        pavucontrol_btn.clicked.connect(lambda: subprocess.Popen(['pavucontrol']))
        layout.addWidget(pavucontrol_btn)
        
        layout.addStretch()
        central.setLayout(layout)
    
    def update_status(self):
        try:
            # Check service
            result = subprocess.run(
                ['systemctl', '--user', 'is-active', 'rodecaster-vad.service'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                status_text = "🟢 Service Running\n"
            else:
                status_text = "⚫ Service Stopped\n"
            
            # Check device
            import hid
            devices = hid.enumerate(0x19f7, 0x0072)
            if devices:
                status_text += "🎛 Device Connected"
            else:
                status_text += "❌ Device Not Found"
            
            self.status_label.setText(status_text)
            
        except Exception as e:
            self.status_label.setText(f"⚠ Error: {str(e)}")
    
    def start_service(self):
        subprocess.run(['systemctl', '--user', 'start', 'rodecaster-vad.service'])
        self.update_status()
    
    def restart_service(self):
        subprocess.run(['systemctl', '--user', 'restart', 'rodecaster-vad.service'])
        self.update_status()
    
    def stop_service(self):
        subprocess.run(['systemctl', '--user', 'stop', 'rodecaster-vad.service'])
        self.update_status()

def main():
    try:
        app = QApplication(sys.argv)
        window = SimpleControlPanel()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
