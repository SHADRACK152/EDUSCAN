
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
    from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QMessageBox
    import sys, json, sqlite3
    QApplication.instance() or QApplication(sys.argv)  # noqa: F841, intentional side effect

    # PyQt5 dialog for unit selection and password entry
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
            start_btn = QPushButton("Start")
            start_btn.clicked.connect(self.accept)
            layout.addWidget(start_btn)
            self.setLayout(layout)

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

    known_ids, known_names, known_encodings = load_all_encodings()
    video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not video.isOpened():
        print("❌ Cannot access camera.")
        return

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            if len(face_distances) == 0:
                continue

            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                sid = known_ids[best_match_index]
                name = known_names[best_match_index]

                if already_logged_today(sid, unit_id) or (sid, unit_id) in logged_students:
                    continue

                # Draw rectangle and name
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # Save attendance
                log_attendance(sid, name)
                save_to_json_log(sid, name, unit_id)
                logged_students.add((sid, unit_id))

                # Show confirmation
                cv2.putText(frame, "✔ Attendance Marked – Next Student", (100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 3)
                speak(f"{name}, attendance marked. Next student.")
                cv2.imshow("EduScan Attendance", frame)
                cv2.waitKey(2500)
                break

        cv2.imshow("EduScan Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()


