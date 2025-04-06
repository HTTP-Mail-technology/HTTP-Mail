import sys
import requests
from PyQt6.QtGui import QIcon, QPixmap
from time import sleep
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QListWidget, QMessageBox, QInputDialog, QSplashScreen

class MailClientApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("HTTP Mail Client")
        self.setWindowIcon(QIcon('icon_.ico'))
        self.setGeometry(100, 100, 800, 600)
        
        self.server_url = self.get_server_url()

        layout = QVBoxLayout()

        # Форма отправки письма
        form_layout = QVBoxLayout()

        self.from_email = QLineEdit(self)
        self.from_email.setPlaceholderText("From")
        form_layout.addWidget(self.from_email)

        self.to_email = QLineEdit(self)
        self.to_email.setPlaceholderText("To")
        form_layout.addWidget(self.to_email)

        self.theme_entry = QLineEdit(self)
        self.theme_entry.setPlaceholderText("Theme")
        form_layout.addWidget(self.theme_entry)

        self.message_entry = QTextEdit(self)
        self.message_entry.setPlaceholderText("Message")
        form_layout.addWidget(self.message_entry)
        
        self.about_button = QPushButton("About", self)
        self.about_button.clicked.connect(self.about)
        form_layout.addWidget(self.about_button)

        self.send_button = QPushButton("Send Mail", self)
        self.send_button.clicked.connect(self.send_mail)
        form_layout.addWidget(self.send_button)

        layout.addLayout(form_layout)

        # Кнопка для получения сообщений
        self.get_button = QPushButton("Get Mails", self)
        self.get_button.clicked.connect(self.get_mails)
        layout.addWidget(self.get_button)

        # Кнопка для удаления сообщений
        self.delete_button = QPushButton("Delete Mail", self)
        self.delete_button.clicked.connect(self.delete_mail)
        layout.addWidget(self.delete_button)

        # Список писем
        self.mails_listbox = QListWidget(self)
        layout.addWidget(self.mails_listbox)

        self.setLayout(layout)
        
    def about(self):
        QMessageBox.about(self, "About", "HTTP Mail Project. Created by 'HTTP Mail Technology' on Github!")

    def send_mail(self):
        from_ = self.from_email.text()
        to = self.to_email.text()
        theme = self.theme_entry.text()
        message = self.message_entry.toPlainText()

        data = {
            'from': from_,
            'to': to,
            'theme': theme,
            'message': message.strip()
        }

        try:
            response = requests.post(f'{self.server_url}/mail/send', json=data)
            if response.json().get("status") == "OK":
                QMessageBox.information(self, "Success", "Mail Sent!")
            else:
                QMessageBox.critical(self, "Error", f"Failed to send mail. {response.json().get("message")}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            
    def get_server_url(self):
        # Показать окно ввода
        while True:
            text, ok = QInputDialog.getText(self, "Input Dialog", "Enter Server URL (e.g. http://localhost:8888):")
            if ok and text:
                return text
            else:
                QMessageBox.warning(self, "No Input", "Server URL cannot be empty. Please enter a valid URL.")

    def get_mails(self):
        to = self.to_email.text()
        data = {'to': to}

        try:
            response = requests.post(f'{self.server_url}/mail/get', json=data)
            mails = response.json()
            self.mails_listbox.clear()

            if mails:
                for mail_id, mail in mails.items():
                    self.mails_listbox.addItem(f"ID: {mail_id}, From: {mail['from']}, Theme: {mail['theme']}, message: {mail['message']}, Time: {mail['time']}")
            else:
                QMessageBox.information(self, "No Mails", "No mails found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_mail(self):
        item = self.mails_listbox.currentItem()

        if item is None:
            QMessageBox.warning(self, "No Selection", "Please select a mail to delete.")
            return

        mail_id = item.text().split(',')[0].split(":")[1].strip()

        data = {'id': mail_id}

        try:
            response = requests.post(f'{self.server_url}/mail/delete', json=data)
            if response.json().get("status") == "OK":
                QMessageBox.information(self, "Success", "Mail Deleted!")
                self.get_mails()  # Обновить список
            else:
                QMessageBox.critical(self, "Error", f"Failed to delete mail. {response.json().get("message")}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap('splash.png'))
    splash.show()
    sleep(3)
    splash.close()
    window = MailClientApp()
    window.show()
    sys.exit(app.exec())
