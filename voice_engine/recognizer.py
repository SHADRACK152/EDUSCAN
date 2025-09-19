import numpy as np
import scipy.io.wavfile as wav
import os


def match_voice(student_id, test_wav_path):
    """
    Dummy voice matcher: returns True if the file exists for the student.
    Replace with real voice matching logic as needed.
    """
    # Path to the enrolled voice file
    enrolled_path = f"students/{student_id}_voice.wav"
    if not os.path.exists(enrolled_path):
        return False
    # For demo: just check both files exist
    return os.path.exists(test_wav_path)
