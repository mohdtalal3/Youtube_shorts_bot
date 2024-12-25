import sys
import csv
import time
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QProgressBar, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from gologin import GoLogin, getRandomPort
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from gologin import GoLogin
from webdriver_manager.chrome import ChromeDriverManager
from gologin import getRandomPort
from google_login import *
from youtube_login import *
from parsing_csv import *


def open_profile(token, profile_data):
    """Open a profile and attempt to log in"""
    print(profile_data)
    proxy_config = {}
    if profile_data.get('proxy_details'):
        proxy_config = {
            "mode": "http",
            "host": profile_data['proxy_details']['ip'],
            "port": profile_data['proxy_details']['port'],
            "username": profile_data['proxy_details']['username'],
            "password": profile_data['proxy_details']['password']
        }

    gl = GoLogin({
        "token": token, 
        "profile_id": profile_data['profile_id'],
        "port": getRandomPort(),
        "writeCookiesFromServer": True,
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
        print(profile_data)
        g_login=login_google(driver,profile_data['login_details']['email'],profile_data['login_details']['password'],profile_data['login_details']['recovery_mail'])
        time.sleep(5)
        channel_created=False
        if g_login:
            channel_created=create_account(driver,profile_data['login_details']['name'])

        return channel_created
    
    except Exception as e:
        print(f"Error during profile opening: {e}")
        return False
    finally:
        driver.quit()
        gl.stop()


def create_and_test_profile(token, login_info, proxy_info=None):
    """Create a GoLogin profile and immediately test it."""
    gl = GoLogin({"token": token})
    try:
        profile_config = {
            "name": login_info['email'],
            "os": 'win',  
            "navigator": {
                "language": 'en-US',
                "userAgent": 'random',  
                "resolution": '1024x768' 
            },
            # "proxy_info":None,
            'proxyEnabled': proxy_info is not None,
            # 'proxyEnabled': False,
            # 'proxy': {
            # 'mode': 'none',
            # },
            'proxy': {
                'mode': 'http' if proxy_info else 'none',
                'host': proxy_info['ip'] if proxy_info else '',
                'port': proxy_info['port'] if proxy_info else '',
                'username': proxy_info['username'] if proxy_info else '',
                'password': proxy_info['password'] if proxy_info else '',
            },
            "webRTC": {
                "mode": "alerted",
                "enabled": True,
            },
            "uploadCookiesToServer": True,
            "writeCookiesFromServer": True,
        }
        
        profile_id = gl.create(profile_config)
        print(f"Profile created with ID: {profile_id}")
        
        # Immediately test the profile
        profile_data = {
            'login_details': login_info,
            'proxy_details': proxy_info,
            'profile_id': profile_id
        }
        
        # Try to open and login
        login_success = open_profile(token, profile_data)
        if not login_success:
            print(f"Login failed. Deleting profile {profile_id}")
            gl.delete(profile_id)
            return None
        
        return {
            'login_details': login_info,
            'proxy_details': proxy_info,
            'profile_id': profile_id,
            'account_created': True
        }
        
    except Exception as e:
        print(f"Error creating/testing profile: {e}")
        if 'profile_id' in locals():
            try:
                gl.delete(profile_id)
                print(f"Deleted failed profile {profile_id}")
            except:
                pass
        return None
    


class ProfileWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, input_file, token):
        super().__init__()
        self.input_file = input_file
        self.token = token
        self.is_paused = False

    def run(self):
        try:
            self.process_csv(
                self.token,
                self.input_file,
                'output.csv'
            )
            self.finished.emit()
        except Exception as e:
            self.status.emit(f"Error: {str(e)}")

    def process_csv(self, token, input_file, output_file):
            fieldnames = ['Name', 'Login_detail', 'proxy', 'profile_id', 'account_created', 'title', 'description', 'upload_video']
            
            # Get total number of rows
            with open(input_file, 'r') as csvfile:
                total_rows = sum(1 for row in csvfile) - 1  # Subtract header row
            
            # Write header
            with open(output_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            # Process rows
            processed = 0
            with open(input_file, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    while self.is_paused:
                        time.sleep(0.1)
                        
                    login_details = parse_login_details(row['Login_detail'], row['Name'])
                    proxy_details = parse_proxy_details(row['proxy'])
                    
                    self.status.emit(f"Processing {row['Name']}...")
                    profile_result = create_and_test_profile(token, login_details, proxy_details)
                    
                    new_row = {
                        'Name': row['Name'],
                        'Login_detail': row['Login_detail'],
                        'proxy': row['proxy'],
                        'profile_id': profile_result['profile_id'] if profile_result else '',
                        'account_created': 'True' if profile_result else 'False',
                        'title': '',  # Empty title field
                        'description': '',  # Empty description field
                        'upload_video': ''  # Empty upload_video field
                    }
                    
                    with open(output_file, 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(new_row)

                    processed += 1
                    progress = int((processed / total_rows) * 100)
                    self.progress.emit(progress)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.worker = None

    def initUI(self):
        self.setWindowTitle('GoLogin Profile Creator')
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QLineEdit {
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
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap('gologin.jpg')  # Replace with your logo
        scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Token input
        self.create_input_field(layout, "GoLogin Token:", "token_input")

        # File selection
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setPlaceholderText("Select input CSV file")
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("background-color: #4CAF50;")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

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

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start")
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

    def center(self):
        frame = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_name:
            self.file_path.setText(file_name)

    def start_processing(self):
        if not self.token_input.text() or not self.file_path.text():
            QMessageBox.warning(self, "Error", "Token and input file are required!")
            return

        self.worker = ProfileWorker(
            self.file_path.text(),
            self.token_input.text()
        )
        
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_label.setText)
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
            self.status_label.setText("Paused")

    def resume_processing(self):
        if self.worker:
            self.worker.is_paused = False
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)
            self.status_label.setText("Resumed")

    def processing_finished(self):
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.status_label.setText("Completed!")
        QMessageBox.information(self, "Complete", 
                              "Profile creation completed successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())