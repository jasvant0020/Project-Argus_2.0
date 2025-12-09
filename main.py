import cv2
import numpy as np
import pygame
from encoding_manager import load_encodings_with_check, face_embeddings_from_bgr, fa
from notifier import send_telegram_notification
from attendance import markAttendance
from logger.snapshot_logger import save_object_snapshot
from logger.unknown_logger import log_unknown
import os

# ====== Configuration ======
TARGET_NAMES = ["NISHANT", "JASVANT"]  # Add multiple names here in uppercase
ALERT_SOUND = "assets/alert.mp3"

# ====== Detection Mode Selection ======
print("Choose detection mode:")
print("1. Detect only known faces")
print("2. Detect only unknown faces")
print("3. Detect both known and unknown faces")

mode = input("Enter option (1/2/3): ").strip()
if mode not in ['1', '2', '3']:
    print("Invalid choice. Defaulting to mode 3 (both).")
    mode = '3'

mode = int(mode)
print(f"✅ Detection mode set to {mode}")

# ====== Initialize ======
pygame.mixer.init()
sound_channel = pygame.mixer.Channel(0)

if os.path.exists(ALERT_SOUND):
    print("✅ Alert sound loaded.")
else:
    print("❌ Alert sound not found.")

encodeListKnown, classNames = load_encodings_with_check()
print("Encoding Complete. Starting Webcam...just in 10 sec")

# Convert known encodings to numpy array for fast math (N x D)
if len(encodeListKnown) > 0:
    known_array = np.vstack([np.array(e, dtype=np.float32) for e in encodeListKnown])
else:
    known_array = np.zeros((0, 512), dtype=np.float32)  # fallback

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Webcam is live ")

person_present = False

while True:
    success, img = cap.read()
    if not success:
        print("❌ Webcam error.")
        break

    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    faces = face_embeddings_from_bgr(imgS)

    detected = False

    for encodeFace, bbox in faces:
        # --- ArcFace cosine similarity matching ---
        if known_array.shape[0] > 0:
            sims = np.dot(known_array, encodeFace) / (
                np.linalg.norm(known_array, axis=1) * np.linalg.norm(encodeFace)
            )
            matchIndex = int(np.argmax(sims))
            matches = sims >= 0.40
        else:
            sims = np.array([])
            matchIndex = -1
            matches = np.array([])

        x1, y1, x2, y2 = [int(v * 4) for v in bbox]

        is_known = sims.size > 0 and matches[matchIndex]

        # ------------------ Mode Handling ------------------
        if mode == 1 and not is_known:
            continue  # skip unknown
        if mode == 2 and is_known:
            continue  # skip known
        # ---------------------------------------------------

        if is_known:
            name = classNames[matchIndex].upper()
            confidence = max(0.0, (1.0 - float(sims[matchIndex]) / 2.0) * 100.0)

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{name} {confidence:.2f}%", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            markAttendance(name, confidence)

            if name in TARGET_NAMES:
                detected = True
                send_telegram_notification(name)
                save_object_snapshot(name, matchIndex, img, (x1, y1, x2, y2))

        else:
            # Unknown face
            unknown_conf = max(0.0, (1.0 - np.min(sims) / 2.0) * 100.0) if sims.size > 0 else 0.0
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(img, f"UNKNOWN {unknown_conf:.2f}%", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            log_unknown(img, encodeFace, unknown_conf)

    if detected and not person_present:
        print("🔊 Playing alert sound...")
        if os.path.exists(ALERT_SOUND) and not sound_channel.get_busy():
            sound_channel.play(pygame.mixer.Sound(ALERT_SOUND))
        person_present = True
    elif not detected:
        sound_channel.stop()
        person_present = False

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
