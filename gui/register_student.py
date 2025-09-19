import face_recognition
from database.student_db import save_student
import cv2
import sounddevice as sd
import scipy.io.wavfile as wav
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt, QTimer


class RegisterStudentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register Student - EduScan")
        self.setGeometry(300, 150, 700, 500)
        # self.setStyleSheet("background-color: #f1f3f5;")

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        # UI Layouts
        layout = QHBoxLayout()

        # Webcam Preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(320, 240)
        layout.addWidget(self.image_label)

        # Form Section
        form_frame = QFrame()
        form_frame.setStyleSheet(
            "border-radius: 15px; "
            "padding: 20px;"
        )
        form_layout = QVBoxLayout()

        title = QLabel("Register New Student")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Student Full Name")
        self.name_input.setStyleSheet(self.input_style())

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Student ID / Reg Number")
        self.id_input.setStyleSheet(self.input_style())

        self.capture_btn = QPushButton("📸 Capture Face")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setStyleSheet(self.button_style())

        self.record_btn = QPushButton("🎤 Record Voice")
        self.record_btn.clicked.connect(self.record_voice)
        self.record_btn.setStyleSheet(self.button_style())

        self.save_btn = QPushButton("💾 Save Student Data")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setStyleSheet(self.button_style())

        widgets = [
            self.name_input,
            self.id_input,
            self.capture_btn,
            self.record_btn,
            self.save_btn
        ]
        for w in widgets:
            form_layout.addWidget(w)

        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        self.setLayout(layout)

        self.captured_face = None
        self.voice_path = None

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QImage(
                rgb_frame.data,
                rgb_frame.shape[1],
                rgb_frame.shape[0],
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(img)
            self.image_label.setPixmap(pixmap)

    def capture_image(self):
        ret, frame = self.capture.read()
        if ret:
            student_id = self.id_input.text()
            if not student_id:
                QMessageBox.warning(
                    self,
                    "Missing ID",
                    "Enter Student ID before capturing."
                )
                return
            path = f"students/{student_id}_face.jpg"
            folder_path = os.path.dirname(path)
            os.makedirs(folder_path, exist_ok=True)
            cv2.imwrite(path, frame)
            self.captured_face = path
            QMessageBox.information(
                self,
                "Captured",
                f"Face image saved: {path}"
            )

    def record_voice(self):
        student_id = self.id_input.text()
        if not student_id:
            QMessageBox.warning(
                self,
                "Missing ID",
                "Enter Student ID before recording."
            )
            return
        fs = 44100  # Sample rate
        seconds = 5  # Duration
        QMessageBox.information(
            self,
            "Recording",
            ("Recording voice for 5 seconds...")
        )
        voice = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        path = f"students/{student_id}_voice.wav"
        os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure directory exists
        wav.write(path, fs, voice)
        self.voice_path = path
        QMessageBox.information(self, "Saved", f"Voice sample saved: {path}")

    def save_data(self):
        name = self.name_input.text()
        student_id = self.id_input.text()

        if not all([name, student_id, self.captured_face, self.voice_path]):
            QMessageBox.warning(
                self,
                "Incomplete",
                "Please fill all fields and capture face & voice."
            )
            return

        # Check if face image exists before loading
        if not self.captured_face or not os.path.exists(self.captured_face):
            QMessageBox.warning(
                self,
                "Face Not Captured",
                "Please capture a face photo before saving."
            )
            return
        # Encode the face image
        img = face_recognition.load_image_file(self.captured_face)
        encodings = face_recognition.face_encodings(img)
        if not encodings:
            QMessageBox.warning(
                self,
                "Error",
                "No face found in captured image."
            )
            return
        save_student(student_id, name, encodings[0], self.voice_path)
        QMessageBox.information(
            self,
            "Saved",
            f"Student {name} saved to database!"
        )

    def input_style(self):
        return """
            QLineEdit {
                padding: 10px;
                border-radius: 8px;
            }
        """

    def button_style(self):
        return """
            QPushButton {
                padding: 10px;
                font-weight: bold;
                border-radius: 6px;
            }
        """

    def closeEvent(self, event):
        self.capture.release()
