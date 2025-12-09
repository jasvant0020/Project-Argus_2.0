import os
import csv
import cv2
from datetime import datetime, timedelta
import numpy as np

UNKNOWN_CSV = 'assets/UnknownLog.csv'
UNKNOWN_DIR = 'logs/UNKNOWN'
UNKNOWN_GAP_SECONDS = 30  # Log same unknown after this many seconds

# Stores: list of tuples (encoded_vector (np.array), last_logged_time)
unknown_faces_log = []

def is_similar(face_encoding1, face_encoding2, tolerance=0.40):
    """
    Compare two InsightFace embeddings using cosine similarity.
    Return True if similarity >= tolerance.
    """
    e1 = np.array(face_encoding1, dtype=np.float32)
    e2 = np.array(face_encoding2, dtype=np.float32)
    sim = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
    return sim >= tolerance  # threshold ~0.35–0.45


def log_unknown(frame, encoding, confidence):
    global unknown_faces_log
    now = datetime.now()

    # Check if this face matches any previously seen unknown
    for i, (prev_encoding, last_time) in enumerate(unknown_faces_log):
        if is_similar(prev_encoding, encoding):
            time_since_last = now - last_time

            # Skip if still within cooldown → prevents multiple snapshots
            if time_since_last < timedelta(seconds=UNKNOWN_GAP_SECONDS):
                return  

            # Update last seen time → allow next log after cooldown
            unknown_faces_log[i] = (prev_encoding, now)
            break
    else:
        # New unknown detected → store it and proceed to log once
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
