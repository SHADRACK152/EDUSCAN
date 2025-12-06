from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QStackedWidget, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QLinearGradient, QPainter
from PyQt5.QtCore import Qt, QSize, QRect
import sqlite3
from datetime import datetime


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EduScan - Dashboard")
        self.setGeometry(0, 0, 1400, 900)
        
        self.sidebar = QVBoxLayout()
        self.content_area = QStackedWidget()

        # Professional sidebar - let QSS handle styling
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(260)
        sidebar_frame.setObjectName("sidebarFrame")
        sidebar_frame.setLayout(self.sidebar)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(self.content_area)
        self.setLayout(main_layout)

        self.init_sidebar()
        self.init_home()

    def init_sidebar(self):
        from theme_manager import toggle_theme

        # Professional header
        logo_container = QFrame()
        logo_container.setObjectName("logoContainer")
        logo_container.setFixedHeight(100)
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(20, 12, 20, 12)
        logo_layout.setSpacing(8)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png").scaled(
            50, 50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)

        title = QLabel("EduScan")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setObjectName("appTitle")
        logo_layout.addWidget(title)
        
        logo_container.setLayout(logo_layout)
        self.sidebar.addWidget(logo_container)

        # Professional buttons
        from run_attendance import start_attendance
        buttons = [
            ("🏠", "Dashboard", self.show_home),
            ("➕", "Register Student", self.open_register_student),
            ("👥", "View Students", self.view_students),
            ("📋", "Manage Units", self.open_manage_units),
            ("📊", "View Attendance", self.open_attendance),
            ("🎥", "Start Attendance", self.start_attendance),
            ("💾", "Export Attendance", self.export_attendance),
            ("🔄", "Refresh", self.refresh_dashboard),
        ]

        for icon, label, action in buttons:
            btn = QPushButton(f"{icon}  {label}")
            btn.clicked.connect(action)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setObjectName("sidebarButton")
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()

        # Theme Toggle Button
        theme_btn = QPushButton("🌙  Dark Mode")
        theme_btn.setFixedHeight(40)
        theme_btn.setCursor(Qt.PointingHandCursor)
        theme_btn.setObjectName("themeButton")
        theme_btn.clicked.connect(lambda: (toggle_theme(), None)[-1])
        self.sidebar.addWidget(theme_btn)
        
        # Logout button
        logout_btn = QPushButton("🔒  Logout")
        logout_btn.clicked.connect(self.logout_admin)
        logout_btn.setFixedHeight(40)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setObjectName("logoutButton")
        self.sidebar.addWidget(logout_btn)

    def init_home(self):
        home_page = QFrame()
        home_page.setObjectName("homePage")
        layout = QVBoxLayout()
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(25)

        # Professional welcome section
        welcome_section = QVBoxLayout()
        welcome_section.setSpacing(8)
        
        heading = QLabel("Dashboard")
        heading.setFont(QFont("Segoe UI", 28, QFont.Bold))
        heading.setObjectName("pageHeading")
        welcome_section.addWidget(heading)
        
        date_text = datetime.now().strftime('%A, %d %B %Y')
        date_label = QLabel(date_text)
        date_label.setFont(QFont("Segoe UI", 13))
        date_label.setObjectName("dateLabel")
        welcome_section.addWidget(date_label)
        
        layout.addLayout(welcome_section)

        # Stats Cards with professional design
        card_layout = QHBoxLayout()
        card_layout.setSpacing(18)

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

        def create_professional_card(icon, title, value):
            card = QFrame()
            card.setObjectName("statCard")
            card.setMinimumHeight(130)
            vbox = QVBoxLayout()
            vbox.setContentsMargins(22, 18, 22, 18)
            vbox.setSpacing(6)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 32))
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vbox.addWidget(icon_lbl)
            
            val_lbl = QLabel(str(value))
            val_lbl.setFont(QFont("Segoe UI", 26, QFont.Bold))
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setObjectName("statValue")
            vbox.addWidget(val_lbl)
            
            title_lbl = QLabel(title)
            title_lbl.setFont(QFont("Segoe UI", 11, QFont.Medium))
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_lbl.setObjectName("statTitle")
            vbox.addWidget(title_lbl)
            
            vbox.addStretch()
            card.setLayout(vbox)
            return card

        # Professional stat cards
        card_layout.addWidget(create_professional_card("👨‍🎓", "Total Students", total_students))
        card_layout.addWidget(create_professional_card("📚", "Total Units", total_units))
        card_layout.addWidget(create_professional_card("✅", "Today's Attendance", attendance_today))
        card_layout.addWidget(create_professional_card("🎯", "Active Unit", active_unit))
        
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

    def start_attendance(self):
        from run_attendance import start_attendance
        start_attendance()