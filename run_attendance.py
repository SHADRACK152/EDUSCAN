
# Ensure QApplication is constructed before any QWidget or PyQt import
from PyQt5.QtWidgets import QApplication
import sys
QApplication.instance() or QApplication(sys.argv)  # noqa: F841, intentional side effect

import cv2
import face_recognition
import numpy as np
import os
import json
from datetime import datetime
from face_engine.recognizer import load_all_encodings
from database.student_db import log_attendance
import pyttsx3


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(text)
    engine.runAndWait()


def already_logged_today(student_id, unit_id):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = "attendance_logs.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
            for log in logs:
                # Check both student and unit for today
                if (
                    log.get("student_id") == student_id and
                    log.get("unit_id") == unit_id and
                    log.get("timestamp", "").startswith(today)
                ):
                    return True
    return False


def save_to_json_log(student_id, name, unit_id):
    log_file = "attendance_logs.json"
    new_log = {
        "student_id": student_id,
        "name": name,
        "unit_id": unit_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(new_log)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)


def start_attendance():
    # Ensure QApplication is constructed before any QWidget
    from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMainWindow, QWidget
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtCore import Qt, QTimer
    import sys, json, sqlite3
    QApplication.instance() or QApplication(sys.argv)  # noqa: F841, intentional side effect

    # PyQt5 dialog for unit selection
    class UnitPasswordDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Start Attendance")
            self.setGeometry(500, 300, 400, 200)
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Select Unit:"))
            self.unit_combo = QComboBox()
            conn = sqlite3.connect("database/students.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, unit_name, unit_code FROM units")
            self.units = cursor.fetchall()
            for uid, name, code in self.units:
                self.unit_combo.addItem(f"{name} ({code})", uid)
            layout.addWidget(self.unit_combo)
            button_layout = QHBoxLayout()
            start_btn = QPushButton("Start")
            start_btn.clicked.connect(self.accept)
            button_layout.addWidget(start_btn)
            layout.addLayout(button_layout)
            self.setLayout(layout)

    # PyQt5 window for attendance with stop button
    class AttendanceWindow(QMainWindow):
        def __init__(self, unit_id):
            super().__init__()
            self.setWindowTitle("EduScan Attendance - Taking")
            self.setGeometry(100, 100, 1000, 700)
            self.unit_id = unit_id
            self.is_running = True
            self.logged_students = set()

            # Main widget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout()

            # Video label
            from PyQt5.QtWidgets import QLabel as QLabelWidget
            self.video_label = QLabelWidget()
            self.video_label.setMinimumHeight(600)
            layout.addWidget(self.video_label)

            # Button layout
            button_layout = QHBoxLayout()
            stop_btn = QPushButton("Stop Attendance")
            stop_btn.setStyleSheet("background-color: red; color: white; font-size: 14px; padding: 10px;")
            stop_btn.clicked.connect(self.stop_attendance)
            button_layout.addStretch()
            button_layout.addWidget(stop_btn)
            layout.addLayout(button_layout)

            main_widget.setLayout(layout)

            # Camera setup
            self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.video.isOpened():
                print("❌ Cannot access camera.")
                self.is_running = False
                return

            self.known_ids, self.known_names, self.known_encodings = load_all_encodings()

            # Timer for camera updates
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)

        def update_frame(self):
            if not self.is_running:
                return

            ret, frame = self.video.read()
            if not ret:
                return

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_encodings, face_encoding, tolerance=0.5)
                face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)

                if len(face_distances) == 0:
                    continue

                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    sid = self.known_ids[best_match_index]
                    name = self.known_names[best_match_index]

                    if already_logged_today(sid, self.unit_id) or (sid, self.unit_id) in self.logged_students:
                        continue

                    # Draw rectangle and name
                    top, right, bottom, left = face_location
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                    # Save attendance
                    log_attendance(sid, name)
                    save_to_json_log(sid, name, self.unit_id)
                    self.logged_students.add((sid, self.unit_id))

                    # Show confirmation
                    cv2.putText(frame, "✔ Attendance Marked – Next Student", (100, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 3)
                    speak(f"{name}, attendance marked. Next student.")

            # Add instructions
            cv2.putText(frame, "Press STOP button to end attendance", (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Convert to Qt format
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(qt_image)
            self.video_label.setPixmap(pixmap.scaledToWidth(self.video_label.width()))

        def stop_attendance(self):
            self.is_running = False
            self.timer.stop()
            self.video.release()
            print("[INFO] Attendance session ended.")
            self.close()

        def closeEvent(self, event):
            self.is_running = False
            self.timer.stop()
            if self.video.isOpened():
                self.video.release()
            event.accept()

    # ...existing code...
    logged_students = set()
    # Get unit_id from password dialog
    unit_id = None
    # Ensure QApplication is constructed before any QWidget
    # (already done above)
    # Show password dialog and get unit_id
    dialog = UnitPasswordDialog()
    if not dialog.exec_():
        print("Attendance not started.")
        return
    unit_id = dialog.unit_combo.currentData()

    # Show attendance window with camera
    attendance_window = AttendanceWindow(unit_id)
    attendance_window.show()


