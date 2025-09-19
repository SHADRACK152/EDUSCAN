 # -*- coding: utf-8 -*-

import cv2
import face_recognition
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import os
import tempfile
import pyttsx3
import json
from datetime import datetime
from face_engine.recognizer import match_voice, load_all_encodings
from database.student_db import log_attendance

# Initialize text-to-speech engine


def speak(text):
    try:
        engine = pyttsx3.init(driverName='sapi5')  # Windows voice API
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("🔇 Voice error:", e)


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


def capture_voice(temp_path, seconds=3):
    speak("Face not recognized. Please speak your name.")
    print("🎙️ Listening...")
    fs = 44100
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(temp_path, fs, recording)


def mark_attendance(student_id, name, frame, show_pos=(50, 50)):
    log_attendance(student_id, name)
    save_to_json_log(student_id, name)
    speak(f"{name}, attendance marked. Next student.")
    cv2.putText(frame, f"{name}", show_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
    cv2.putText(frame, "✔ Attendance Marked", (show_pos[0], show_pos[1] + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
    cv2.imshow("EduScan", frame)
    cv2.waitKey(3000)


def start_attendance_camera():
    known_ids, known_names, known_encodings = load_all_encodings()
    video = cv2.VideoCapture(0)

    if not video.isOpened():
        print("❌ Could not open webcam.")
        speak("Webcam error. Please check your camera.")
        return

    print("🎯 EduScan started. Press Q to quit.")
    speak("EduScan started. Please face the camera.")

    logged_students = set()

    while True:
        ret, frame = video.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        recognized = False

        for face_encoding, face_loc in zip(encodings, faces):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            if len(face_distances) == 0:
                continue

            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                sid = known_ids[best_match_index]
                name = known_names[best_match_index]

                if already_logged_today(sid) or sid in logged_students:
                    speak(f"{name}, your attendance is already marked.")
                    print(f"⚠️ {name} already marked.")
                    recognized = True
                    break

                top, right, bottom, left = face_loc
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"{name}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2)

                mark_attendance(sid, name, frame)
                logged_students.add(sid)
                recognized = True
                break

        if not recognized and len(faces) > 0:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
                capture_voice(tmpfile.name)
                sid, name = match_voice(tmpfile.name)
                os.remove(tmpfile.name)

                if sid and name:
                    if already_logged_today(sid) or sid in logged_students:
                        speak(f"{name}, your attendance is already marked.")
                        print(f"⚠️ {name} already marked by voice.")
                        continue

                    mark_attendance(sid, name, frame)
                    logged_students.add(sid)
                else:
                    speak("Voice not recognized. Try again.")
                    print("❌ Voice match failed.")

        cv2.imshow("EduScan", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_attendance_camera()
