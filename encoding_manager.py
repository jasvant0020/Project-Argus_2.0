import os
import pickle
import cv2
import face_recognition

IMAGE_PATH = 'ImagesAttendance'
ENCODE_DIR = 'encodings'
PICKLE_FILE = os.path.join(ENCODE_DIR, 'encodings.pkl')
META_FILE = os.path.join(ENCODE_DIR, 'encoding_meta.pkl')

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.resize(img, (300, 300))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            encodeList.append(encodings[0])
        else:
            print("⚠️ No face found in one image.")
    return encodeList

def load_encodings_with_check():
    if not os.path.exists(ENCODE_DIR):
        os.makedirs(ENCODE_DIR)

    images = []
    classNames = []
    for filename in sorted(os.listdir(IMAGE_PATH)):
        path = os.path.join(IMAGE_PATH, filename)
        img = cv2.imread(path)
        if img is not None:
            images.append(img)
            classNames.append(os.path.splitext(filename)[0].upper())

    if os.path.exists(PICKLE_FILE) and os.path.exists(META_FILE):
        with open(META_FILE, 'rb') as f:
            saved_names = pickle.load(f)
        if saved_names == classNames:
            with open(PICKLE_FILE, 'rb') as f:
                return pickle.load(f), classNames

    print("🔄 Generating fresh encodings...")
    encodings = findEncodings(images)
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(encodings, f)
    with open(META_FILE, 'wb') as f:
        pickle.dump(classNames, f)

    return encodings, classNames
