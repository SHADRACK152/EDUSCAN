
# 🎓 EduScan — Smart Attendance System

> A **desktop-based Smart Attendance System** with **AI-powered facial and voice recognition**, built using **Python + PyQt5**.  
> EduScan modernizes classroom attendance with real-time recognition, hybrid fallback, exports, and a sleek dashboard UI.

---

## 📌 Features
- 🎭 **AI Recognition** → Face recognition with fallback to voice confirmation.  
- 🖥️ **Modern Dashboard** → Responsive PyQt5 GUI with school branding.  
- 📂 **Unit-Based Attendance** → Manage units, assign students, track attendance.  
- 🔔 **Audio Feedback** → Real-time voice confirmations via TTS engine.  
- 📊 **Data Export** → Export records to CSV / Excel.  
- ⚡ **Hybrid Mode** → Face recognition → fallback to voice → log attendance once/day.  
- 🔒 **Admin Tools** → Reset records, manage units & students.  

---

## � Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/<your-org>/eduscan.git
cd eduscan

2. Create environment & install dependencies
python -m venv .venv
# Activate:
# macOS/Linux → source .venv/bin/activate
# Windows → .venv\Scripts\activate
pip install -r requirements.txt

3. Run EduScan
python main.py
```

⚙️ Requirements

Python 3.8+

Webcam (internal/external)

OS: Windows / Linux

Dependencies: pyqt5, opencv-python, face_recognition, numpy, pandas, pyttsx3, openpyxl

Install all with:

```bash
pip install -r requirements.txt
```

🖼️ Screenshots
<details> <summary>Click to expand</summary>

Dashboard View


Attendance Capture


</details>
🛠️ Project Structure
eduscan/
│── assets/            # logos, screenshots, icons
│── core/              # engines: face, voice, db
│── ui/                # PyQt5 views & widgets
│── exports/           # exported reports
│── logs/              # JSON attendance logs
│── main.py            # entry point
│── requirements.txt   # dependencies
│── README.md          # this file

🔄 How It Works
```mermaid
flowchart TD
   UI[Dashboard (PyQt5)] -->|Start| Camera[Camera Capture]
   Camera --> FaceRec[Face Recognition Engine]
   FaceRec --> Decision{Recognized?}
   Decision -->|Yes| DB[(Attendance DB)]
   Decision -->|No| Voice[Voice Fallback (TTS)]
   Voice --> DB
   DB --> Export[CSV/Excel Reports]
```

🧪 Testing

Run unit tests with:

```bash
pytest -q
```

📌 Roadmap

 Face recognition attendance

 Voice fallback system

 Attendance export (CSV, Excel)

 Multi-admin roles & login system

 Real-time analytics (charts, graphs)

 Cloud sync option

🤝 Contributing

Contributions welcome!

Fork the repo

Create a feature branch

Commit & push

Open a PR 🎉

� License

MIT License © 2025 — EduScan Team


---

👉 This is now **one clean, modern README.md file**.
Do you also want me to embed the **dependencies list (`requirements.txt`) inside this README** (so yo
