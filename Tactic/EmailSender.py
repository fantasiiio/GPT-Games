import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

class EmailSender:
    def __init__(self, gmail_user, gmail_app_password):
        self.gmail_user = gmail_user
        self.gmail_app_password = gmail_app_password

    def _connect_to_server(self):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)  # 587 for TLS
            server.starttls()
            server.login(self.gmail_user, self.gmail_app_password)
            return server
        except Exception as e:
            print(f"Failed to connect to the Gmail SMTP server: {e}")
            return None

    def _send_email(self, to_email, verification_link):
        # Email properties
        subject = "Verify your email address"
        body = f"Please click the following link to verify your email address: {verification_link}"

        msg = MIMEMultipart()
        msg['From'] = self.gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = self._connect_to_server()
        if server is None:
            return

        # Send email
        try:
            server.sendmail(self.gmail_user, to_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()

    def send_verification_email(self, to_email, verification_link):
        email_thread = threading.Thread(target=self._send_email, args=(to_email, verification_link))
        email_thread.start()

# EmailSender.send_verification_email("receiveremail@gmail.com", "https://verification-link.com")            
