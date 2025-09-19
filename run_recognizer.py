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

def already_logged_today(student_id):
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = "attendance_logs.json"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = json.load(f)
            for log in logs:
                if log["student_id"] == student_id and log["timestamp"].startswith(today):
                    return True
    return False

def save_to_json_log(student_id, name):
    log_file = "attendance_logs.json"
    new_log = {
        "student_id": student_id,
        "name": name,
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
    known_ids, known_names, known_encodings = load_all_encodings()
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        print("❌ Cannot access camera.")
        return

    print("✅ EduScan Started. Face recognition in progress...")

    logged_students = set()

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

                # Skip if already logged
                if already_logged_today(sid) or sid in logged_students:
                    continue

                # Draw rectangle
                top, right, bottom, left = face_location
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                # ✅ Save Attendance
                log_attendance(sid, name)
                save_to_json_log(sid, name)
                logged_students.add(sid)

                # ✅ Show success + announce
                cv2.putText(frame, "✔ Attendance Marked – Next Student", (100, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 0), 3)
                speak(f"{name}, attendance marked. Next student.")

                # Show confirmation for 2.5 seconds
                cv2.imshow("EduScan Attendance", frame)
                cv2.waitKey(2500)
                break  # Move to next frame

        cv2.imshow("EduScan Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_attendance()
