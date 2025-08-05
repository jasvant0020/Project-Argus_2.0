import cv2
import numpy as np
import pygame
import face_recognition
from encoding_manager import load_encodings_with_check
from notifier import send_telegram_notification
from attendance import markAttendance
from logger.snapshot_logger import save_object_snapshot
from logger.unknown_logger import log_unknown
import os

# ====== Configuration ======
TARGET_NAMES = ["NISHANT", "JASVANT"]  # Add multiple names here in uppercase
ALERT_SOUND = "assets/alert.mp3"

# ====== Initialize ======
pygame.mixer.init()
sound_channel = pygame.mixer.Channel(0)

if os.path.exists(ALERT_SOUND):
    print("✅ Alert sound loaded.")
else:
    print("❌ Alert sound not found.")

encodeListKnown, classNames = load_encodings_with_check()
print("Encoding Complete. Starting Webcam...just in 10 sec")

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

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    detected = False

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            confidence = (1 - faceDis[matchIndex]) * 100

            y1, x2, y2, x1 = [v * 4 for v in faceLoc]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # green box

            text = f"{name} {confidence:.2f}%"
            cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            markAttendance(name, confidence)

            if name in TARGET_NAMES:
                detected = True
                send_telegram_notification(name)

                # Save snapshot log of this detection
                save_object_snapshot(
                    object_name=name,
                    object_id=matchIndex,
                    frame=img,
                    bbox=(x1, y1, x2, y2)
                )
        else:
            # Handle unknown person
            confidence = (1 - np.min(faceDis)) * 100
            y1, x2, y2, x1 = [v * 4 for v in faceLoc]

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box
            text = f"UNKNOWN {confidence:.2f}%"
            cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            log_unknown(img, encodeFace, confidence)

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




