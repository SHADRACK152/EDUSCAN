# 🎓 EduScan — Smart Attendance System

> A desktop-based Smart Attendance System with AI-powered facial and voice recognition, built using Python + PyQt5. 
> EduScan modernizes classroom attendance with real-time recognition, hybrid fallback, exports, and a sleek dashboard UI.

---

## 📌 Features
- 🎭 AI Recognition — Face recognition with fallback to voice confirmation
- 🖥️ Modern Dashboard — Responsive PyQt5 GUI with school branding
- 📂 Unit-Based Attendance — Manage units, assign students, track attendance
- 🔔 Audio Feedback — Real-time voice confirmations via TTS engine
- 📊 Data Export — Export records to CSV / Excel
- ⚡ Hybrid Mode — Face recognition → fallback to voice → log attendance once/day
- 🔒 Admin Tools — Reset records, manage units & students

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/SHADRACK152/EDUSCAN.git
cd EDUSCAN
```

### 2. Create environment & install dependencies
```bash
python -m venv .venv
# Activate:
#   macOS/Linux: source .venv/bin/activate
#   Windows:     .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run EduScan
```bash
python main.py
```

---

### ⚙️ Requirements
- Python 3.8+
- Webcam (internal/external)
- OS: Windows / Linux
- Dependencies:
  - pyqt5
  - opencv-python
  - face_recognition
  - numpy
  - pandas
  - pyttsx3
  - openpyxl

---

## 🗂️ Project Structure
```
eduscan/
├── assets/            # logos, screenshots, icons
├── core/              # engines: face, voice, db
├── ui/                # PyQt5 views & widgets
├── exports/           # exported reports
├── logs/              # JSON attendance logs
├── main.py            # entry point
├── requirements.txt   # dependencies
└── README.md          # this file
```


## 🧪 Testing
Run unit tests with:
```bash
pytest -q
```

## 🗺️ Roadmap
- Face recognition attendance
- Voice fallback system
- Attendance export (CSV, Excel)
- Multi-admin roles & login system
- Real-time analytics (charts, graphs)
- Cloud sync option

## 🤝 Contributing
Contributions welcome!
1. Fork the repo
2. Create a feature branch
3. Commit & push
4. Open a PR 🎉

## 📄 License
MIT License © 2025 — EduScan Team

---

