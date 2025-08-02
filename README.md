# Project-Argus
🎯 Face Recognition Alert & Attendance System

A modular real-time face recognition system that:

✅ Detects known faces via webcam  
✅ Logs attendance with confidence and timestamp  
✅ Sends Telegram alerts when specific people are detected  
✅ Avoids duplicate logs using time threshold  
✅ Works offline with robust encoding & caching  

---

## 📁 Project Structure
    Project-Argus/
    │
    ├── main.py              # Main controller — runs detection and coordination
    ├── notifier.py          # Sends Telegram alerts (non-blocking)
    ├── attendance.py        # Logs attendance with time-gap and confidence
    ├── encoding_manager.py  # Handles image loading, encoding, and caching
    │
    ├── ImagesAttendance/    # Store images of persons to recognize
    ├── encodings/           # Stores pickle-encoded face encodings
    ├── assets/
    │ ├── Attendance.csv     # CSV log of detections
    │ └── alert.mp3          # Sound played on detection
    │
    ├── requirements.txt     # Python dependencies
    └── README.md            # Documentation

---

## 🚀 Features

- 🎥 **Real-Time Detection** using webcam
- 🧠 **Face Encoding Caching** for fast startup
- 📝 **Attendance Logging** to `assets/Attendance.csv`
- ⏱️ **Time Gap Protection**: Avoids repeating logs within 5 minutes per person
- 📈 **Confidence-Based Updates**: Higher-confidence detection updates older entry
- 📩 **Telegram Alert Notification** on specific names
- 🔊 **Alert Sound** when target person is detected

---

## 🧠 How It Works

1. Face images in `ImagesAttendance/` are encoded using `face_recognition`
2. Encodings are cached to `encodings/encodings.pkl`
3. `main.py` reads webcam frames and runs recognition
4. If person detected:
   - Logs entry in CSV (once per 5 minutes or if confidence is higher)
   - Sends Telegram alert if person is in your `TARGET_NAMES` list
   - Plays alert sound

---

## 📸 Image Requirements

- Place clear, front-facing images in `ImagesAttendance/`
- File name should be the person's name (e.g., `Elon Musk.jpg`)
- Supported formats: `.jpg`, `.jpeg`, `.png`

---

## ⚙️ Configuration

### 🎯 Target Person(s) for Alert
Edit this in `main.py`:
```python
TARGET_NAMES = ["ELON MUSK", "JASVANT"]
```
## 📲 Telegram Alert Setup
In notifier.py, replace:
BOT_TOKEN = "your_bot_token"
CHAT_ID = "your_chat_id"


