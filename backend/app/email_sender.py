import smtplib
from email.message import EmailMessage
from app.logger import LogConfig
import logging
from logging.config import dictConfig

dictConfig(LogConfig().dict())
logger = logging.getLogger("GreenEcoHub")


class EmailSender:
    def __init__(self, smtp_server, smtp_port, username, password, use_ssl=False):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_ssl = use_ssl

    async def send_email(self, empfaenger_email, subject, body):
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = empfaenger_email

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)

            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
        except smtplib.SMTPException as smtp_error:
            logger.error(f"SMTP-Fehler aufgetreten: {smtp_error}")
            raise smtp_error
        except Exception as e:
            logger.error(f"Beim Senden einer E-Mail ist ein Fehler aufgetreten: {e}")
            raise e
