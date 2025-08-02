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
    
    venv/                    # prefer python 3.10

---

## 🚀 Features

- 🎥 **Real-Time Detection** using webcam
- 🧠 **Face Encoding Caching** for fast startup
- 📝 **Attendance Logging** to `assets/Attendance.csv`
- ⏱️ **Time Gap Protection**: Avoids repeating logs within 5 minutes per person
- 📈 **Confidence-Based Updates**: Higher-confidence detection updates older entry
- 📩 **Telegram Alert Notification** on specific names
- 🔊 **Alert Sound** when target person is detected



## 🧠 How It Works

1. Face images in `ImagesAttendance/` are encoded using `face_recognition`
2. Encodings are cached to `encodings/encodings.pkl`
3. `main.py` reads webcam frames and runs recognition
4. If person detected:
   - Logs entry in CSV (once per 5 minutes or if confidence is higher)
   - Sends Telegram alert if person is in your `TARGET_NAMES` list
   - Plays alert sound



## 📸 Image Requirements

- Place clear, front-facing images in `ImagesAttendance/`
- File name should be the person's name (e.g., `Elon Musk.jpg`)
- Supported formats: `.jpg`, `.jpeg`, `.png`



## ⚙️ Configuration

### 🎯 Target Person(s) for Alert
Edit this in `main.py`:
```python
TARGET_NAMES = ["ELON MUSK", "JASVANT"]
```
## 📲 Telegram Alert Setup
```In notifier.py, replace:
BOT_TOKEN = "your_bot_token"
CHAT_ID = "your_chat_id"
```
- Use `BotFather` to create a bot and get a token
- Use `@userinfobot` to get your Chat ID



⏱️ Attendance Time Gap
```In attendance.py, change:
TIME_GAP_MINUTES = 5  # prevents frequent logging
```


## 🔊 Alert Sound
- Place your sound in assets/alert.mp3
- Must be in .mp3 format
- It will play when a target person is detected



## 📦 Installation
```🐍 1. Clone and Set Up Virtual Environment
git clone https://github.com/yourname/FaceRecognitionProject
cd FaceRecognitionProject
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```
```📦 2. Install Python Dependencies
pip install -r requirements.txt
```
If face_recognition or dlib fails:
- Use Python 3.10 or earlier for best compatibility



## ▶️ Running the Project
```
python main.py
```
- Press Q to exit the webcam
- Check attendance logs in assets/Attendance.csv



## 💡Tips
- Make sure lighting is good when capturing new face images
- Restart main.py after adding new images to generate encodings
- Add multiple names to TARGET_NAMES for multi-alerts
- Use .env file for storing secrets securely (optional)


## 🔐 Dependencies
```
face_recognition
opencv-python
numpy
pygame
requests
dlib (via face_recognition)
```
Install all with:
```
pip install -r requirements.txt
```


## 📈 Example Attendance Entry
```
Name,Timestamp,Confidence
ELON MUSK,2025-08-02 16:40:09,91.34
```


## 🛡️ License
This project is for educational and personal use. Commercial or surveillance use must comply with local laws regarding face recognition.



## 🙌 Credits
Developed by Jasvant
AI + Vision Enthusiast | Final-Year B.Tech
