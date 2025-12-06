import face_recognition
import cv2
import os
import pickle
from database.student_db import load_all_encodings, log_attendance
import numpy as np
import warnings

# Suppress deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Try to import voice encoder, but make it optional
try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    encoder = VoiceEncoder()
except ImportError:
    # Voice recognition is optional - face recognition is the primary method
    encoder = None

DATASET_DIR = "students"
ENCODINGS_FILE = "face_engine/encodings.pkl"


def encode_faces():
    known_encodings = []
    known_names = []

    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    for file in os.listdir(DATASET_DIR):
        if file.endswith("_face.jpg"):
            path = os.path.join(DATASET_DIR, file)
            name = file.replace("_face.jpg", "")
            img = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(name)
                print(f"[INFO] Encoded: {name}")
            else:
                print(f"[WARNING] No face found in {file}")

    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)
    print("[INFO] Face encodings saved!")


def recognize_face_live():
    ids, names, encodings = load_all_encodings()
    if not encodings:
        print("[ERROR] No students in database.")
        return

    cap = cv2.VideoCapture(0)
    print("[INFO] Starting camera. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        live_encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding, box in zip(live_encodings, boxes):
            matches = face_recognition.compare_faces(
                encodings, encoding, tolerance=0.45
            )
            name = "Unknown"

            if True in matches:
                matched_index = matches.index(True)
                name = names[matched_index]
                student_id = ids[matched_index]
                log_attendance(student_id, name)

            top, right, bottom, left = box
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("EduScan - Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def match_voice(student_id, test_wav_path, threshold=0.75):
    enrolled_path = f"students/{student_id}_voice.wav"
    if not os.path.exists(enrolled_path) or not os.path.exists(test_wav_path):
        return False
    # Preprocess and encode both voices
    enrolled_wav = preprocess_wav(enrolled_path)
    test_wav = preprocess_wav(test_wav_path)
    enrolled_embed = encoder.embed_utterance(enrolled_wav)
    test_embed = encoder.embed_utterance(test_wav)
    # Cosine similarity
    numerator = np.dot(enrolled_embed, test_embed)
    denominator = np.linalg.norm(enrolled_embed) * np.linalg.norm(test_embed)
    similarity = numerator / denominator
    return similarity > threshold
