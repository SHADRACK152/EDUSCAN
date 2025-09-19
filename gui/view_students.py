from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from database.student_db import load_all_encodings
import sqlite3
import os


class ViewStudentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All Registered Students")
        self.setGeometry(400, 200, 1100, 580)
        # self.setStyleSheet("background-color: #f8f9fa;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("All Registered Students")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 10px;")

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or ID...")
        self.search_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 8px;")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Face", "Student ID", "Name", "Voice Path", "Action"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setIconSize(QSize(80, 80))

        self.table.setStyleSheet("font-size: 14px; border: none;")

        layout.addWidget(title)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        ids, names, _ = load_all_encodings()
        conn = sqlite3.connect("database/students.db")
        cursor = conn.cursor()
        self.rows_data = []

        for sid in ids:
            cursor.execute(
                "SELECT name, voice_path FROM students WHERE student_id = ?",
                (sid,)
            )
            result = cursor.fetchone()
            if result:
                name, voice_path = result
                img_path = f"students/{sid}_face.jpg"
                self.rows_data.append((sid, name, voice_path, img_path))

        conn.close()
        self.populate_table(self.rows_data)

    def populate_table(self, data):
        self.table.setRowCount(0)
        for row_idx, (sid, name, voice_path, img_path) in enumerate(data):
            self.table.insertRow(row_idx)

            # Face image
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path).scaled(
                    80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                icon = QIcon(pixmap)
                item = QTableWidgetItem()
                item.setIcon(icon)
                self.table.setItem(row_idx, 0, item)
            else:
                self.table.setItem(row_idx, 0, QTableWidgetItem("No Image"))

            self.table.setItem(row_idx, 1, QTableWidgetItem(sid))
            self.table.setItem(row_idx, 2, QTableWidgetItem(name))
            self.table.setItem(row_idx, 3, QTableWidgetItem(voice_path))

            # Delete Button
            delete_btn = QPushButton("🗑️ Delete")
            delete_btn.setStyleSheet("padding: 6px; border-radius: 6px;")
            delete_btn.clicked.connect(lambda _, s=sid: self.delete_student(s))
            self.table.setCellWidget(row_idx, 4, delete_btn)

    def delete_student(self, student_id):
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            (
                f"Are you sure you want to delete student "
                f"'{student_id}'?"
            ),
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect("database/students.db")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM students WHERE student_id = ?", (student_id,)
            )
            conn.commit()
            conn.close()

            # Remove files
            face_path = f"students/{student_id}_face.jpg"
            voice_path = f"students/{student_id}_voice.wav"
            if os.path.exists(face_path):
                os.remove(face_path)
            if os.path.exists(voice_path):
                os.remove(voice_path)

            QMessageBox.information(
                self, "Deleted",
                f"Student {student_id} deleted."
            )
            self.load_table()

    def filter_table(self, text):
        text = text.lower()
        filtered = [
            row for row in self.rows_data
            if text in row[0].lower() or text in row[1].lower()
        ]
        self.populate_table(filtered)