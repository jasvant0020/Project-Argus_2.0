import os
import pickle
import cv2
import numpy as np
from insightface.app import FaceAnalysis

IMAGE_PATH = 'ImagesAttendance'
ENCODE_DIR = 'encodings'
PICKLE_FILE = os.path.join(ENCODE_DIR, 'encodings.pkl')
META_FILE = os.path.join(ENCODE_DIR, 'encoding_meta.pkl')

# Initialize InsightFace FaceAnalysis
# -----------------------------
# Default: GPU (ctx_id=0).
# If your laptop DOESN'T have a GPU, change ctx_id to -1:
#    fa.prepare(ctx_id=-1)
# (This is the *one* minor change needed to run on CPU.)
fa = FaceAnalysis(allowed_modules=['detection', 'recognition'])
fa.prepare(ctx_id=-1, det_size=(640, 640))  # ctx_id=0 -> GPU, set -1 for CPU
# -----------------------------

def face_embeddings_from_bgr(resized_bgr):
    """
    Input: resized_bgr (OpenCV BGR image)
    Return: list of (embedding (np.array), bbox (list[x1,y1,x2,y2])) for faces found
    """
    # FaceAnalysis expects RGB images; convert
    rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)
    faces = fa.get(rgb)
    out = []
    for f in faces:
        # f.embedding is a numpy array
        emb = np.array(f.embedding, dtype=np.float32)
        bbox = f.bbox  # [x1,y1,x2,y2] in resized image coordinates
        out.append((emb, bbox))
    return out

def findEncodings(images):
    encodeList = []
    for img in images:
        # Resize to speed up (same as original flow where you used 0.25 scaling)
        small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        embs = face_embeddings_from_bgr(small)
        if embs:
            # Use first face found in that image (same behavior as original)
            encodeList.append(embs[0][0])
            encodeList[-1] = encodeList[-1] / np.linalg.norm(encodeList[-1])
        else:
            print("⚠️ No face found in one image.")
    return encodeList

def load_encodings_with_check():
    if not os.path.exists(ENCODE_DIR):
        os.makedirs(ENCODE_DIR)

    classNames = []
    encodings = []

    for person in sorted(os.listdir(IMAGE_PATH)):
        person_dir = os.path.join(IMAGE_PATH, person)
        if not os.path.isdir(person_dir):
            continue

        person_embs = []
        for file in os.listdir(person_dir):
            path = os.path.join(person_dir, file)
            img = cv2.imread(path)
            if img is None:
                continue
            small = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            embs = face_embeddings_from_bgr(small)
            if embs:
                person_embs.append(embs[0][0])

        if person_embs:
            mean_emb = np.mean(person_embs, axis=0)
            mean_emb /= np.linalg.norm(mean_emb)  # normalize
            encodings.append(mean_emb)
            classNames.append(person.upper())
        else:
            print(f"⚠️ No valid faces for {person}")

    # Save as before...
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(encodings, f)
    with open(META_FILE, 'wb') as f:
        pickle.dump(classNames, f)

    print(f"✅ Encoded {len(classNames)} identities.")
    return encodings, classNames
