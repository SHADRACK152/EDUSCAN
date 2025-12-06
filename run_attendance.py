
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
    """Text to speech - speaks the given text"""
    try:
        import threading
        
        # Run speech in background thread to prevent blocking UI
        def speak_thread():
            try:
                engine = pyttsx3.init(driverName='sapi5')  # Windows SAPI5
                engine.setProperty('rate', 150)  # Speed
                engine.setProperty('volume', 0.9)  # Volume
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"[WARNING] Speech error: {e}")
        
        # Start speech in background thread
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    except Exception as e:
        print(f"[WARNING] Speech initialization failed: {e}")


def listen_for_voice():
    """Listen to microphone and return recognized text"""
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 4000  # Adjust sensitivity
        
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                print("[INFO] Listening... (speak now)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                try:
                    # Listen with timeout of 5 seconds
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                except sr.RequestError as e:
                    # Silently fail - user will get feedback on UI
                    return None
                except sr.UnknownValueError:
                    return None
        except Exception as e:
            # Microphone error - return None silently
            return None
        
        # Recognize speech using Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio)
            print(f"[VOICE] Recognized: {text}")
            return text.lower()
        except sr.UnknownValueError:
            # Could not understand - return None
            return None
        except sr.RequestError as e:
            # API error or no internet
            print(f"[ERROR] Internet/API error: {e}")
            return None
            
    except Exception as e:
        # Silently fail
        return None




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
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if not app:
        print("[ERROR] Failed to get QApplication instance.")
        return

    # Show attendance window
    try:
        attendance_window = AttendanceWindow()
        attendance_window.show()
        print("[INFO] Attendance window opened.")
    except Exception as e:
        print(f"[ERROR] Failed to open attendance window: {e}")
        import traceback
        traceback.print_exc()


# Define AttendanceWindow class at module level (outside the function)
def _create_attendance_window_class():
    """Create the AttendanceWindow class"""
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMainWindow, QWidget, QMessageBox
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtCore import Qt, QTimer
    import sqlite3

    class AttendanceWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("EduScan Attendance - Taking")
            self.setGeometry(100, 100, 1000, 700)
            self.is_running = False
            self.logged_students = set()
            self.unit_id = None
            self.video = None
            self.timer = None

            # Main widget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            layout = QVBoxLayout()

            # Unit selection layout
            unit_layout = QHBoxLayout()
            unit_layout.addWidget(QLabel("Select Unit:"))
            self.unit_combo = QComboBox()
            
            try:
                conn = sqlite3.connect("database/students.db")
                cursor = conn.cursor()
                cursor.execute("SELECT id, unit_name, unit_code FROM units")
                self.units = cursor.fetchall()
                if not self.units:
                    QMessageBox.warning(self, "Error", "No units found in database. Please create a unit first.")
                    self.close()
                    return
                else:
                    for uid, name, code in self.units:
                        self.unit_combo.addItem(f"{name} ({code})", uid)
                conn.close()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to load units: {e}")
                self.close()
                return
            
            unit_layout.addWidget(self.unit_combo)
            start_btn = QPushButton("🎥 Start Camera")
            start_btn.clicked.connect(self.start_camera)
            unit_layout.addWidget(start_btn)
            
            voice_btn = QPushButton("🎤 Start Voice")
            voice_btn.clicked.connect(self.start_voice_attendance)
            unit_layout.addWidget(voice_btn)
            layout.addLayout(unit_layout)

            # Video label
            from PyQt5.QtWidgets import QLabel as QLabelWidget
            self.video_label = QLabelWidget()
            self.video_label.setMinimumHeight(600)
            self.video_label.setText("Select a unit and click 'Start Attendance' to begin...")
            layout.addWidget(self.video_label)

            # Button layout for stop
            button_layout = QHBoxLayout()
            self.stop_btn = QPushButton("Stop Attendance")
            self.stop_btn.setStyleSheet("background-color: red; color: white; font-size: 14px; padding: 10px;")
            self.stop_btn.clicked.connect(self.stop_attendance)
            self.stop_btn.setEnabled(False)
            button_layout.addStretch()
            button_layout.addWidget(self.stop_btn)
            layout.addLayout(button_layout)

            main_widget.setLayout(layout)

        def start_camera(self):
            """Start the camera and begin attendance"""
            self.unit_id = self.unit_combo.currentData()
            if not self.unit_id:
                QMessageBox.warning(self, "Error", "Please select a unit first.")
                return
            
            try:
                self.video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                # Set camera properties for better performance
                self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.video.set(cv2.CAP_PROP_FPS, 30)
                
                if not self.video.isOpened():
                    QMessageBox.critical(self, "Camera Error", "Cannot access camera. Please check if camera is connected.")
                    print("❌ Cannot access camera.")
                    return

                self.known_ids, self.known_names, self.known_encodings = load_all_encodings()
                
                if not self.known_encodings:
                    QMessageBox.warning(self, "No Students", "No student encodings found. Please register students first.")
                    print("[WARNING] No student encodings loaded.")
                    self.video.release()
                    return

                # Disable unit selection and enable stop button
                self.unit_combo.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.is_running = True
                self.frame_count = 0  # For frame skipping
                
                # Timer for camera updates - reduced from 30ms to 50ms
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_frame)
                self.timer.start(50)  # ~20 FPS instead of 33 FPS
                print("[INFO] Attendance window started successfully.")
                # Announce that attendance has started
                unit_name = self.unit_combo.currentText()
                speak(f"Attendance has started for {unit_name}")
            except Exception as e:
                QMessageBox.critical(self, "Initialization Error", f"Failed to initialize attendance: {e}")
                print(f"[ERROR] Initialization failed: {e}")
                import traceback
                traceback.print_exc()
                self.is_running = False
                if self.video:
                    self.video.release()

        def update_frame(self):
            if not self.is_running or not self.video:
                return

            try:
                ret, frame = self.video.read()
                if not ret:
                    return

                # Optimize: Scale down frame for faster processing
                small_frame = cv2.resize(frame, (320, 240))
                rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Process face recognition only every 5 frames to reduce lag
                self.frame_count += 1
                if self.frame_count % 5 == 0:
                    # Use model='hog' for faster (but less accurate) face detection
                    face_locations = face_recognition.face_locations(rgb_frame, model='hog')
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

                            # Draw rectangle and name on small frame
                            top, right, bottom, left = face_location
                            cv2.rectangle(small_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(small_frame, name, (left, top - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                            # Save attendance
                            log_attendance(sid, name)
                            save_to_json_log(sid, name, self.unit_id)
                            self.logged_students.add((sid, self.unit_id))

                            # Show confirmation
                            cv2.putText(small_frame, "✔ Attendance Marked", (50, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
                            print(f"[ATTENDANCE] {name} marked present")
                            # Speak confirmation
                            speak(f"Attendance marked for {name}")

                # Add instructions to display
                cv2.putText(small_frame, "Press STOP to end", (10, small_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                # Convert to Qt format - use small_frame for display
                h, w, ch = small_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(small_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
                pixmap = QPixmap.fromImage(qt_image)
                self.video_label.setPixmap(pixmap.scaledToWidth(self.video_label.width()))
            except Exception as e:
                print(f"[ERROR] Frame update failed: {e}")
                self.stop_attendance()

        def start_voice_attendance(self):
            """Start voice-based attendance"""
            self.unit_id = self.unit_combo.currentData()
            if not self.unit_id:
                QMessageBox.warning(self, "Error", "Please select a unit first.")
                return
            
            try:
                # Disable unit selection and enable stop button
                self.unit_combo.setEnabled(False)
                self.stop_btn.setEnabled(True)
                self.is_running = True
                
                self.video_label.setText("🎤 Voice Attendance Mode\n\nSay your student name or ID when prompted.\n\nClick STOP to end.")
                
                print("[INFO] Voice attendance started.")
                speak("Voice attendance started. Say your name or student ID when ready.")
                
                # Timer for voice input - use longer interval to avoid spamming
                self.voice_timer = QTimer()
                self.voice_timer.timeout.connect(self.process_voice_input)
                self.voice_timer.start(3000)  # Check for voice input every 3 seconds
                self.last_voice_check = datetime.now()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start voice attendance: {e}")
                print(f"[ERROR] Voice attendance failed: {e}")
                self.is_running = False

        def process_voice_input(self):
            """Process voice input in background"""
            if not self.is_running:
                return
            
            try:
                # Listen for voice
                text = listen_for_voice()
                
                if text:
                    # Search for student by name or ID
                    conn = sqlite3.connect("database/students.db")
                    cursor = conn.cursor()
                    
                    # Try to find student by name or ID
                    cursor.execute(
                        "SELECT student_id, name FROM students WHERE LOWER(name) LIKE ? OR student_id LIKE ?",
                        (f"%{text}%", f"%{text}%")
                    )
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        sid, name = result
                        
                        if not (already_logged_today(sid, self.unit_id) or (sid, self.unit_id) in self.logged_students):
                            # Mark attendance
                            log_attendance(sid, name)
                            save_to_json_log(sid, name, self.unit_id)
                            self.logged_students.add((sid, self.unit_id))
                            
                            # Visual feedback
                            self.video_label.setText(f"✅ Attendance marked for {name}\n\nSay next student name...")
                            speak(f"Attendance marked for {name}")
                            print(f"[ATTENDANCE] {name} marked present via voice")
                        else:
                            speak(f"{name} already marked present")
                            self.video_label.setText(f"Already marked: {name}\n\nSay next student name...")
                    else:
                        speak("Student not found. Please try again.")
                        self.video_label.setText("❌ Student not found\n\nPlease say a valid student name...")
                        
            except Exception as e:
                print(f"[ERROR] Voice input processing failed: {e}")

        def stop_attendance(self):

            self.is_running = False
            if self.timer:
                self.timer.stop()
            if hasattr(self, 'voice_timer'):
                self.voice_timer.stop()
            if self.video:
                self.video.release()
            print("[INFO] Attendance session ended.")
            self.unit_combo.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.video_label.setText("Select a unit and click 'Start Attendance' to begin...")
            self.logged_students = set()

        def closeEvent(self, event):
            self.is_running = False
            if self.timer:
                self.timer.stop()
            if self.video and self.video.isOpened():
                self.video.release()
            event.accept()

    return AttendanceWindow

# Create the class at module level
AttendanceWindow = _create_attendance_window_class()


