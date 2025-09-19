from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFrame,
    QMessageBox, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from gui.dashboard import DashboardWindow

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduScan Login")
        self.showFullScreen()
        self.setStyleSheet("background-color: #e9ecef;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Logo at the top
        from PyQt5.QtGui import QPixmap
        logo = QLabel()
        pixmap = QPixmap("assets/logo.png").scaled(
            250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo)

        # Header
        title = QLabel("EduScan")
        title.setFont(QFont("Segoe UI", 40, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")

        subtitle = QLabel("Smart Biometric Attendance System")
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6c757d;")

        # Frame with shadow
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 25px;
                padding: 60px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 80))
        frame.setGraphicsEffect(shadow)

        # Form elements
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        self.username.setStyleSheet(self.input_style(font_size=24))

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Enter password")
        self.password.setStyleSheet(self.input_style(font_size=24))

        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet(self.button_style(font_size=28))
        self.login_btn.clicked.connect(self.handle_login)

        # Inner layout in frame
        form_layout = QVBoxLayout()
        form_layout.setSpacing(30)
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.login_btn)
        frame.setLayout(form_layout)

        # Final layout
        main_layout.addSpacing(20)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addStretch()
        main_layout.addWidget(frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def handle_login(self):
        user = self.username.text().strip()
        pwd = self.password.text()

        if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
            self.dashboard = DashboardWindow()
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Access Denied",
                "Invalid credentials. Try again."
            )

    def input_style(self, font_size=14):
        return f"""
            QLineEdit {{
                padding: 20px;
                border: 1.5px solid #ced4da;
                border-radius: 12px;
                font-size: {font_size}px;
                background: #ffffff;
            }}
            QLineEdit:focus {{
                border: 2px solid #007bff;
            }}
        """

    def button_style(self, font_size=15):
        return f"""
            QPushButton {{
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe
                );
                color: white;
                padding: 24px;
                border: none;
                border-radius: 12px;
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #007bff;
            }}
        """
