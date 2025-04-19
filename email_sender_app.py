import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from email_sender_ui import Ui_Form
import send_emails

class EmailSenderThread(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_update = pyqtSignal(str)

    def __init__(self, subject, body):
        super().__init__()
        self.subject = subject
        self.body = body

    def run(self):
        try:
            # Redirect stdout to our log update signal
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            send_emails.send_emails_to_clients(self.subject, self.body)
            
            # Get the captured output and emit it
            output = sys.stdout.getvalue()
            self.log_update.emit(output)
            
            # Restore stdout
            sys.stdout = old_stdout
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class EmailSenderApp(Ui_Form):
    def __init__(self):
        super().__init__()
        
        # Get the application directory
        if getattr(sys, 'frozen', False):
            # Running as a bundled app
            if sys.platform == 'darwin':
                # For macOS app bundle, we need to use the MacOS directory
                application_path = os.path.dirname(sys.executable)
            else:
                application_path = os.path.dirname(sys.executable)
        else:
            # Running as a script
            application_path = os.path.dirname(os.path.abspath(__file__))

        # Create necessary directories
        self.data_dir = os.path.join(application_path, 'data')
        self.logs_dir = os.path.join(application_path, 'logs')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set log file path
        self.log_file_path = os.path.join(self.logs_dir, 'email_log.txt')

        # Connect the send button
        self.sendButton.clicked.connect(self.send_emails)

        # Set up log update timer
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log_display)
        self.log_timer.start(1000)  # kas sekundę

        self.update_log_display()

    def send_emails(self):
        subject = self.subjectLineEdit.text().strip()
        body = self.bodyTextEdit.toHtml()  # Get HTML content

        if not subject or not body:
            QMessageBox.warning(self, "Klaida", "Prašome užpildyti laiško antraštę ir tekstą!")
            return

        self.sendButton.setEnabled(False)

        self.thread = EmailSenderThread(subject, body)
        self.thread.finished.connect(self.on_sending_finished)
        self.thread.error.connect(self.on_sending_error)
        self.thread.log_update.connect(self.update_log_display)
        self.thread.start()

    def on_sending_finished(self):
        self.sendButton.setEnabled(True)
        QMessageBox.information(self, "Sėkmė", "Laiškai sėkmingai išsiųsti!")

    def on_sending_error(self, error_message):
        self.sendButton.setEnabled(True)
        QMessageBox.critical(self, "Klaida", f"Klaida siunčiant laiškus: {error_message}")

    def update_log_display(self, new_log_content=None):
        try:
            if new_log_content:
                # If we received new log content from the thread, append it
                current_content = self.logTextEdit.toPlainText()
                self.logTextEdit.setPlainText(current_content + new_log_content)
            else:
                # Otherwise, read from the log file
                with open(self.log_file_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                self.logTextEdit.setPlainText(log_content)
            
            # Scroll to the bottom
            self.logTextEdit.verticalScrollBar().setValue(
                self.logTextEdit.verticalScrollBar().maximum())
        except FileNotFoundError:
            # Create empty log file if it doesn't exist
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write('')
            self.logTextEdit.setPlainText('')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailSenderApp()
    window.show()
    sys.exit(app.exec_())
