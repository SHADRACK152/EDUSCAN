from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sqlite3

class ViewAttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Attendance Logs")
        self.setGeometry(400, 200, 900, 550)
        # self.setStyleSheet("background-color: #f8f9fa;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📋 Attendance Logs")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px;")
        layout.addWidget(title)

        # Unit dropdown
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Select Unit:")
        unit_label.setFont(QFont("Segoe UI", 12))
        unit_layout.addWidget(unit_label)
        self.unit_combo = QComboBox()
        unit_layout.addWidget(self.unit_combo)
        layout.addLayout(unit_layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or date...")
        self.search_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Attendance table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Student ID", "Name", "Timestamp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("font-size: 14px; border: none;")
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_units()
        self.unit_combo.currentIndexChanged.connect(self.load_attendance)
        self.load_attendance()

    def load_units(self):
        conn = sqlite3.connect("database/students.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, unit_name, unit_code FROM units")
        self.units = cursor.fetchall()
        self.unit_combo.clear()
        for uid, name, code in self.units:
            self.unit_combo.addItem(f"{name} ({code})", uid)
        conn.close()

    def load_attendance(self):
        conn = sqlite3.connect("database/students.db")
        cursor = conn.cursor()
        unit_index = self.unit_combo.currentIndex()
        if unit_index < 0 or not hasattr(self, 'units') or not self.units:
            self.attendance_data = []
            self.populate_table(self.attendance_data)
            conn.close()
            return
        unit_id = self.unit_combo.currentData()
        cursor.execute("""
            SELECT attendance.student_id, students.name, attendance.timestamp
            FROM attendance
            JOIN students ON attendance.student_id = students.student_id
            JOIN student_units ON students.student_id = student_units.student_id
            WHERE student_units.unit_id = ?
            ORDER BY attendance.timestamp DESC
        """, (unit_id,))
        self.attendance_data = cursor.fetchall()
        conn.close()
        self.populate_table(self.attendance_data)

    def populate_table(self, data):
        self.table.setRowCount(0)
        for row_idx, (sid, name, ts) in enumerate(data):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(sid)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(ts))

    def filter_table(self, text):
        text = text.lower()
        filtered = [
            row for row in self.attendance_data
            if text in str(row[0]).lower() or text in str(row[1]).lower() or text in str(row[2]).lower()
        ]
        self.populate_table(filtered)
