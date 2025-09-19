from PyQt5.QtWidgets import QSplashScreen, QLabel
from PyQt5.QtGui import QMovie, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from playsound import playsound
import threading

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        # Make splash fullscreen
        self.showFullScreen()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: white;")

        # Centered logo
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap("assets/logo.png").scaled(
            300, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_logo = self.width() // 2 - 90
        y_logo = self.height() // 2 - 200
        self.logo.setGeometry(x_logo, y_logo, 180, 180)

        # Centered loading GIF below logo
        self.loader = QLabel(self)
        loader_size = 180
        x_loader = self.width() // 2 - loader_size // 2
        y_loader = self.height() // 2 - 80
        self.loader.setGeometry(x_loader, y_loader, loader_size, loader_size)
        movie = QMovie("assets/loading.gif")
        movie.setScaledSize(movie.scaledSize())
        self.loader.setMovie(movie)
        movie.start()

        # Loading text below loader
        self.status_label = QLabel("Starting EduScan...", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 36))
        x_status = self.width() // 2 - 400
        y_status = self.height() // 2 + 120
        self.status_label.setGeometry(x_status, y_status, 800, 80)

        # Sequence messages
        self.messages = [
            "Loading database...",
            "Checking camera...",
            "Loading face models...",
            "Starting services...",
            "Welcome to EduScan 🎓"
        ]
        self.current_step = 0

        # Sound (non-blocking)
        threading.Thread(target=self.play_sound).start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_message)
        self.duration_timer = QTimer()
        self.duration_timer.setSingleShot(True)
        self.duration_timer.timeout.connect(self.finish_splash)

    def start(self, on_complete):
        self.on_complete = on_complete
        self.show()
        self.timer.start(800)
        self.duration_timer.start(15000)  # 15 seconds

    def update_message(self):
        if self.current_step < len(self.messages):
            self.status_label.setText(self.messages[self.current_step])
            self.current_step += 1
        else:
            self.timer.stop()
            # Wait for duration_timer to close splash

    def finish_splash(self):
        self.close()
        self.on_complete()

    def play_sound(self):
        try:
            playsound("assets/welcome.mp3")
        except Exception:
            pass  # Sound is optional
