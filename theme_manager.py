from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream

current_theme = "light"


def apply_theme(theme_name):
    global current_theme
    current_theme = theme_name
    file_path = f"themes/{theme_name}.qss"
    file = QFile(file_path)
    open_mode = QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text
    if file.open(open_mode):
        stream = QTextStream(file)
        qss = stream.readAll()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setStyleSheet(qss)
        file.close()


def toggle_theme():
    new_theme = "dark" if current_theme == "light" else "light"
    apply_theme(new_theme)
    return new_theme
