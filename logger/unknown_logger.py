# unknown_logger.py

import os
import csv
import cv2
from datetime import datetime, timedelta
import face_recognition
import numpy as np

UNKNOWN_CSV = 'assets/UnknownLog.csv'
UNKNOWN_DIR = 'logs/UNKNOWN'
UNKNOWN_GAP_SECONDS = 10  # Log same unknown after this many seconds

# Stores: {encoded_vector (tuple): last_logged_time}
unknown_faces_log = []

def is_similar(face_encoding1, face_encoding2, tolerance=0.5):
    distance = np.linalg.norm(np.array(face_encoding1) - np.array(face_encoding2))
    return distance < tolerance

def log_unknown(frame, encoding, confidence):
    global unknown_faces_log
    now = datetime.now()

    # Check if this face matches any previously seen unknown
    for i, (prev_encoding, last_time) in enumerate(unknown_faces_log):
        if is_similar(prev_encoding, encoding):
            if now - last_time < timedelta(seconds=UNKNOWN_GAP_SECONDS):
                return  # Recently logged → skip
            else:
                unknown_faces_log[i] = (prev_encoding, now)  # Update timestamp
                break
    else:
        # New unknown person
        unknown_faces_log.append((encoding, now))

    # Log to CSV
    os.makedirs(os.path.dirname(UNKNOWN_CSV), exist_ok=True)
    if not os.path.exists(UNKNOWN_CSV):
        with open(UNKNOWN_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Timestamp', 'Confidence'])

    with open(UNKNOWN_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['UNKNOWN', now.strftime("%Y-%m-%d %H:%M:%S"), f"{confidence:.2f}"])

    # Save snapshot
    os.makedirs(UNKNOWN_DIR, exist_ok=True)
    filename = f"unknown_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(os.path.join(UNKNOWN_DIR, filename), frame)

    print(f"📸 Logged unknown at {now.strftime('%H:%M:%S')} with confidence {confidence:.2f}")
