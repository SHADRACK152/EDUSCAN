# EduScan Digital README

Welcome to EduScan! This is a modern, AI-powered attendance and student management system built with Python and PyQt5.

## 🚀 Features
- Face recognition-based attendance
- Secure unit selection and logging
- Real-time camera capture (Windows compatible)
- Modern PyQt5 dashboard UI
- Attendance export to Excel
- Voice feedback for attendance confirmation
- Modular codebase for easy extension

## 🖥️ Quick Start
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the main application**
   ```bash
   python main.py
   ```
3. **Mark attendance**
   - Use the dashboard sidebar to start attendance capture.
   - Follow on-screen instructions for unit selection and face scan.

## 📸 Camera Troubleshooting
- If you see camera errors, ensure no other app is using the webcam.
- Windows users: Camera access uses DirectShow for best compatibility.
- Check privacy settings: Settings > Privacy > Camera > Allow apps to access your camera.

## 🗂️ Project Structure
- `main.py` — App entry point
- `gui/` — Dashboard and login UI
- `run_attendance.py` — Attendance capture logic
- `face_engine/` — Face recognition engine
- `database/` — Student and unit database
- `assets/` — Images and logos
- `themes/` — UI themes
- `voice_engine/` — Voice feedback

## 📝 Attendance Logs & Export
- Attendance is logged in `attendance_logs.json`.
- Export attendance to Excel from the dashboard.

## 🤖 AI & Voice
- Uses `face_recognition` for face matching
- Uses `pyttsx3` for voice feedback

## 💡 Contributing
Pull requests are welcome! For major changes, please open an issue first.

## 📄 License
This project is licensed under the MIT License.

---
For more help, contact the maintainer or open an issue on GitHub.
