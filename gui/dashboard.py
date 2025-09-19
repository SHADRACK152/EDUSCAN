from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QStackedWidget, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import sqlite3
from datetime import datetime


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.sidebar = QVBoxLayout()
        self.content_area = QStackedWidget()

        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(220)
        sidebar_frame.setStyleSheet("background-color: #343a40;")
        sidebar_frame.setLayout(self.sidebar)

        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

        self.init_sidebar()
        self.init_home()

    def init_sidebar(self):
        from theme_manager import toggle_theme

        # Logo + Title
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png").scaled(
            120, 120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("padding: 10px; background-color: #495057; border-radius: 8px;")
        self.sidebar.addWidget(logo_label)

        title = QLabel("EduScan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white; padding: 12px;")
        self.sidebar.addWidget(title)

        # Theme toggle
        toggle_btn = QPushButton("🌙 Toggle Theme")
        toggle_btn.clicked.connect(lambda: (toggle_theme(), None)[-1])
        self.sidebar.addWidget(toggle_btn)

        # Sidebar buttons
        from run_attendance import start_attendance
        buttons = [
            ("🏠 Dashboard", self.show_home),
            ("➕ Register Student", self.open_register_student),
            ("👥 View Students", self.view_students),
            ("📘 Manage Units", self.open_manage_units),
            ("🧾 View Attendance", self.open_attendance),
            ("📤 Export Attendance", self.export_attendance),
            ("🎥 Start Attendance", start_attendance),
            ("🔄 Refresh", self.refresh_dashboard),
            ("🔒 Logout", self.logout_admin)
        ]

        for label, action in buttons:
            btn = QPushButton(label)
            btn.clicked.connect(action)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #495057;
                    color: white;
                    font-size: 14px;
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #6c757d;
                }
            """)
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()

    def init_home(self):
        home_page = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        # Welcome Banner
        welcome_text = f"Welcome, Admin 👋 | {datetime.now().strftime('%A, %d %B %Y %I:%M %p')}"
        heading = QLabel(welcome_text)
        heading.setFont(QFont("Segoe UI", 28, QFont.Bold))
        heading.setStyleSheet("color: #212529;")
        layout.addWidget(heading)

        # Overview Cards
        card_layout = QHBoxLayout()
        card_layout.setSpacing(30)

        conn = sqlite3.connect("database/students.db")
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM students")
        total_students = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM units")
        total_units = cur.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute("SELECT COUNT(*) FROM attendance WHERE DATE(timestamp)=?", (today,))
        attendance_today = cur.fetchone()[0]
        cur.execute("SELECT unit_name FROM units LIMIT 1")
        active_unit = cur.fetchone()
        active_unit = active_unit[0] if active_unit else "None"
        conn.close()

        def create_card(icon, title, value, color):
            card = QFrame()
            card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #dee2e6;")
            vbox = QVBoxLayout()
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 32))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont("Segoe UI", 13))
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl = QLabel(str(value))
            val_lbl.setFont(QFont("Segoe UI", 30, QFont.Bold))
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setStyleSheet(f"color: {color};")
            vbox.addWidget(icon_lbl)
            vbox.addWidget(val_lbl)
            vbox.addWidget(title_lbl)
            card.setLayout(vbox)
            return card

        card_layout.addWidget(create_card("🧑‍🎓", "Students", total_students, "#007bff"))
        card_layout.addWidget(create_card("📚", "Units", total_units, "#28a745"))
        card_layout.addWidget(
            create_card(
                "🕒",
                "Attendance Today",
                attendance_today,
                "#17a2b8"
            )
        )
        card_layout.addWidget(
            create_card(
                "✅",
                "Active Unit",
                active_unit,
                "#ffc107"
            )
        )
        layout.addLayout(card_layout)

        layout.addStretch()
        home_page.setLayout(layout)
        self.content_area.addWidget(home_page)
        self.content_area.setCurrentWidget(home_page)

    def show_home(self):
        self.content_area.setCurrentIndex(0)

    def open_register_student(self):
        from gui.register_student import RegisterStudentWindow
        self.register_window = RegisterStudentWindow()
        self.register_window.show()

    def view_students(self):
        from gui.view_students import ViewStudentsWindow
        self.students_window = ViewStudentsWindow()
        self.students_window.show()

    def open_attendance(self):
        from gui.view_attendance import ViewAttendanceWindow
        self.attendance_window = ViewAttendanceWindow()
        # Add Clear Attendance button to attendance window
        clear_btn = QPushButton("🗑️ Clear Attendance")
        clear_btn.setStyleSheet("background-color: #dc3545; color: white; font-size: 14px; border-radius: 6px; margin: 10px;")
        def clear_attendance():
            reply = QMessageBox.question(self.attendance_window, "Confirm Clear", "Are you sure you want to clear all attendance records? This cannot be undone.", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                conn = sqlite3.connect("database/students.db")
                cur = conn.cursor()
                cur.execute("DELETE FROM attendance")
                conn.commit()
                conn.close()
                QMessageBox.information(self.attendance_window, "Cleared", "All attendance records have been cleared.")
                # Optionally refresh the attendance view if it supports it
        clear_btn.clicked.connect(clear_attendance)
        # Try to add button to attendance window layout
        if hasattr(self.attendance_window, 'layout') and callable(self.attendance_window.layout):
            layout = self.attendance_window.layout()
            if layout is not None:
                layout.addWidget(clear_btn)
        self.attendance_window.show()

    def export_attendance(self):
        import pandas as pd
        conn = sqlite3.connect("database/students.db")
        cur = conn.cursor()
        cur.execute("SELECT student_id, name, timestamp FROM attendance ORDER BY timestamp DESC")
        rows = cur.fetchall()

        if not rows:
            conn.close()
            QMessageBox.information(self, "No Records", "No attendance records found.")
            return

        df = pd.DataFrame(rows, columns=["Student ID", "Name", "Timestamp"])
        filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        conn.close()

        QMessageBox.information(self, "Exported", f"Attendance exported to {filename}")

    def refresh_dashboard(self):
        self.init_home()
        QMessageBox.information(self, "Refreshed", "Dashboard data refreshed.")

    def logout_admin(self):
        QMessageBox.information(self, "Logout", "You have been logged out.")

    def open_manage_units(self):
        from gui.manage_units import ManageUnitsWindow
        self.unit_window = ManageUnitsWindow()
        self.unit_window.show()