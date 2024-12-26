import sys
import csv
import time
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QProgressBar, QFileDialog, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from gologin import GoLogin, getRandomPort
from parsing_csv import *
from video_uploader import *

class VideoUploadWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, input_file, token, video_path):
        super().__init__()
        self.input_file = input_file
        self.token = token
        self.video_path = video_path
        self.is_paused = False
        self.output_file = 'upload_data.csv'

    def run(self):
        try:
            self.process_csv_youtube()
            self.finished.emit()
        except Exception as e:
            self.status.emit(f"Error: {str(e)}")
    
    def update_proxies(self,profile_data):
        gl = GoLogin({"token": self.token})
        profile_id = profile_data['profile_id']
        proxy_info = profile_data['proxy_details']
        
        if proxy_info:
            updated_config = {
                "id": profile_id,  
                "proxyEnabled": True,
                "proxy": {
                    "mode": "http",
                    "host": proxy_info['ip'],
                    "port": proxy_info['port'],
                    "username": proxy_info['username'],
                    "password": proxy_info['password'],
                }
            }
            try:
                gl.update(updated_config)  
                print(f"Proxy updated successfully for profile {profile_id}")
            except Exception as e:
                print(f"Error updating proxy for profile {profile_id}: {e}")
    def open_profile(self, profile_data):

        self.update_proxies(profile_data)
        if profile_data.get('proxy_details'):
            proxy_config = {
                "mode": "http",
                "host": profile_data['proxy_details']['ip'],
                "port": profile_data['proxy_details']['port'],
                "username": profile_data['proxy_details']['username'],
                "password": profile_data['proxy_details']['password']
            }
        
        """Open a profile and attempt to upload video"""
        gl = GoLogin({
            "token": self.token, 
            "profile_id": profile_data['profile_id'],
            "port": getRandomPort(),
            "writeCookiesToServer": True,
            "uploadCookiesToServer": True,
            "proxy": proxy_config if proxy_config else None
        })
        
        debugger_address = gl.start()
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        chrome_options.add_argument("--start-maximized")
        chrome_driver_path = "chromedriver.exe"
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            return upload_on_youtube(driver, profile_data)
        except Exception as e:
            print(f"Error during profile opening: {e}")
            return False
        finally:
            driver.quit()
            gl.stop()

    def process_csv_youtube(self):
        fieldnames = ['Login_detail', 'proxy', 'profile_id', 'account_created', 
                     'title', 'description', 'upload_video']
        
        # Get total number of rows
        with open(self.input_file, 'r') as csvfile:
            total_rows = sum(1 for row in csvfile) - 1  # Subtract header row
        
        # Write header
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

        # Process rows
        processed = 0
        with open(self.input_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                while self.is_paused:
                    time.sleep(0.1)

                self.status.emit(f"Processing profile: {row['profile_id']}")
                
                login_details = parse_login_details(row['Login_detail'], row['Name'])
                proxy_details = parse_proxy_details(row['proxy'])
                checker = row['account_created']
                
                profile_data = {
                    'login_details': login_details,
                    'proxy_details': proxy_details,
                    'profile_id': row['profile_id'],
                    'account_created': row['account_created'],
                    'video_path': self.video_path,
                    'title': row['title'],
                    'description': row['description']
                }
                if checker is True:
                    upload = self.open_profile(profile_data)
                else:
                    upload=False
                new_row = {
                    'Login_detail': row['Login_detail'],
                    'proxy': row['proxy'],
                    'profile_id': row['profile_id'],
                    'account_created': row['account_created'],
                    'title': row['title'],
                    'description': row['description'],
                    'upload_video': 'True' if upload else 'False'
                }

                with open(self.output_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(new_row)

                processed += 1
                progress = int((processed / total_rows) * 100)
                self.progress.emit(progress)
                self.status.emit(f"Processed profile {row['profile_id']} - {progress}%")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def initUI(self):
        self.setWindowTitle('YouTube Video Uploader')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        logo_label = QLabel()
        pixmap = QPixmap('youtube_logo.jpg') 
        scaled_pixmap = pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Token input
        self.create_input_field(layout, "GoLogin Token:", "token_input")

        # File selections
        self.create_file_selector(layout, "Input CSV File:", "input_csv_path")
        self.create_file_selector(layout, "Video File:", "video_path", "Video Files (*.mp4 *.avi *.mkv *.mov)")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        layout.addWidget(self.status_text)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Upload")
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")

        for btn, color in [(self.start_btn, "#4CAF50"), 
                          (self.pause_btn, "#FF9800"), 
                          (self.resume_btn, "#2196F3")]:
            btn.setStyleSheet(f"background-color: {color};")
            btn.setMinimumSize(120, 40)
            button_layout.addWidget(btn)

        self.start_btn.clicked.connect(self.start_processing)
        self.pause_btn.clicked.connect(self.pause_processing)
        self.resume_btn.clicked.connect(self.resume_processing)

        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)

        layout.addLayout(button_layout)

        self.setMinimumSize(600, 700)
        self.center()

    def create_input_field(self, layout, label_text, attribute_name):
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        input_field = QLineEdit()
        setattr(self, attribute_name, input_field)
        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        layout.addLayout(field_layout)

    def create_file_selector(self, layout, label_text, attribute_name, file_filter="CSV Files (*.csv)"):
        field_layout = QHBoxLayout()
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setReadOnly(True)
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("background-color: #4CAF50;")
        browse_btn.clicked.connect(lambda: self.browse_file(input_field, file_filter))
        
        setattr(self, attribute_name, input_field)
        
        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        field_layout.addWidget(browse_btn)
        layout.addLayout(field_layout)

    def center(self):
        frame = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def browse_file(self, input_field, file_filter):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", file_filter)
        if file_name:
            input_field.setText(file_name)

    def update_status(self, message):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def start_processing(self):
        if not all([self.token_input.text(), 
                   self.input_csv_path.text(), 
                   self.video_path.text()]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return

        self.worker = VideoUploadWorker(
            self.input_csv_path.text(),
            self.token_input.text(),
            self.video_path.text()
        )
        
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.processing_finished)
        
        self.worker.start()
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)

    def pause_processing(self):
        if self.worker:
            self.worker.is_paused = True
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)
            self.update_status("Process paused")

    def resume_processing(self):
        if self.worker:
            self.worker.is_paused = False
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.update_status("Process resumed")

    def processing_finished(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.update_status("Upload process completed!")
        QMessageBox.information(self, "Complete", 
                              "Video upload process completed successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())