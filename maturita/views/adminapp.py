from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QStackedWidget
)

from sql import get_data

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()


class LoginWin(QWidget):
    def __init__(self, switch):
        QWidget.__init__(self)
        self.switch = switch # Uložíme si odkaz na přepínač, abychom ho mohli ovládat
        
        self.winlayout = QVBoxLayout()

        self.emailcheck = QLabel('Enter e-mail:')
        self.winlayout.addWidget(self.emailcheck)

        self.input_email = QLineEdit()
        self.winlayout.addWidget(self.input_email)

        self.passwordcheck = QLabel('Enter password:')
        self.winlayout.addWidget(self.passwordcheck)

        self.input_pass = QLineEdit()
        self.winlayout.addWidget(self.input_pass)

        self.btn = QPushButton('Login')
        self.winlayout.addWidget(self.btn)

        self.login_status = QLabel('')
        self.winlayout.addWidget(self.login_status)

        self.setLayout(self.winlayout)

        self.btn.clicked.connect(self.login)

    def login(self):
        email = self.input_email.text()
        password = self.input_pass.text()
        
        users = get_data("MATURITA_HOL_USERS")
        for u in users:
            if u["email"] == email:
                    try:
                        if ph.verify(u["password"], password) and u["role"] == 1:
                            self.login_status.setText("")
                            return self.switch.setCurrentIndex(1)
                    except VerifyMismatchError: # without this, it would spit out an error
                        pass
        return self.login_status.setText("Incorrect login info!")
        
class SelectWin(QWidget):
    def __init__(self, switch):
        QWidget.__init__(self)
        self.switch = switch
        
        self.winlayout = QVBoxLayout()
        self.text = QLabel("Toney Admin Manager")
        self.users = QPushButton("Manage users")
        self.logout = QPushButton("Logout")
        
        self.winlayout.addWidget(self.text)
        self.winlayout.addWidget(self.users)
        self.winlayout.addWidget(self.logout)
        self.setLayout(self.winlayout)
        
        self.logout.clicked.connect(self.backlogout)
        self.users.clicked.connect(self.showusers)
        
    def backlogout(self):
        self.switch.setCurrentIndex(0)
    def showusers(self):
        self.switch.setCurrentIndex(2)

class UserWin(QWidget):
    def __init__(self, switch):
        QWidget.__init__(self)
        self.switch = switch
        
        self.winlayout = QVBoxLayout()
        self.text = QLabel("Users")
        self.winlayout.addWidget(self.text)

        users = get_data("MATURITA_HOL_USERS")
        for u in users:
            btn = QPushButton(u["username"])
            btn.setProperty("user_data", u) # put all the cool info in the button

            self.winlayout.addWidget(btn)

            btn.clicked.connect(self.userwindow)

        self.back = QPushButton("Return")
        self.logout = QPushButton("Logout")
        
        self.winlayout.addWidget(self.back)
        self.winlayout.addWidget(self.logout)
        self.setLayout(self.winlayout)
        


        self.back.clicked.connect(self.backreturn)
        self.logout.clicked.connect(self.backlogout)
    
    def userwindow(self):
        pressed_btn = self.sender() # gets the button that called this
        data = pressed_btn.property("user_data") # gets the button's data

        self.win = UserInfoWin(
            data["id"], 
            data["username"], 
            data["email"], 
            data["password"], 
            data["role"]
        )
        self.win.show()

    def backlogout(self):
        self.switch.setCurrentIndex(0)
    def backreturn(self):
        self.switch.setCurrentIndex(1)

class UserInfoWin(QWidget):
    def __init__(self, id, username, email, password, role):
        QWidget.__init__(self)
        self.winlayout = QVBoxLayout()
        self.username = username
        self.id = id
        self.email = email
        self.password = password
        self.role = role

        self.UI()

    def UI(self):
        self.setWindowTitle(f"Details of {self.username}")

        username_label = QLabel(f"Username: {self.username}")
        self.winlayout.addWidget(username_label)
        id_label = QLabel(f"ID: {self.id}")
        self.winlayout.addWidget(id_label)
        email_label = QLabel(f"E-mail: {self.email}")
        self.winlayout.addWidget(email_label)
        password_label = QLabel(f"Password: {self.password}")
        self.winlayout.addWidget(password_label)
        role_label = QLabel(f"Role: {self.role}")
        self.winlayout.addWidget(role_label)

        self.setLayout(self.winlayout)

app = QApplication([])

# main window that other windows change 
win = QStackedWidget() 

pg0 = LoginWin(win)
pg1 = SelectWin(win)
pg2 = UserWin(win)

win.addWidget(pg0)
win.addWidget(pg1)
win.addWidget(pg2)

win.setWindowTitle("Toney Admin Manager")
win.resize(300, 200)
win.show()

app.exec()