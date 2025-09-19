from PyQt5.QtWidgets import QApplication
from gui.splash import SplashScreen
from gui.login import LoginWindow
import sys

app = QApplication(sys.argv)


def show_login():
    global login_window
    login_window = LoginWindow()
    login_window.show()


splash = SplashScreen()
splash.start(show_login)

sys.exit(app.exec_())
