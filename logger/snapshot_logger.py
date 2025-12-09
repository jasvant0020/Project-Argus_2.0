import os
import cv2
import json
from datetime import datetime

def save_object_snapshot(object_name, object_id, frame, bbox):
    # Ensure bounding box values are standard ints
    x1, y1, x2, y2 = [int(v) for v in bbox]

    # Create folder for the person
    object_folder = os.path.join("logs", object_name)
    os.makedirs(object_folder, exist_ok=True)

    # Save full frame instead of cropped face
    snapshot_path = os.path.join(object_folder, "last_seen.jpg")
    meta_path = os.path.join(object_folder, "meta.json")

    # Save the full frame (not cropped)
    cv2.imwrite(snapshot_path, frame)

    # Save metadata
    metadata = {
        "object_id": int(object_id),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bbox": [x1, y1, x2, y2]
    }

    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=4)
