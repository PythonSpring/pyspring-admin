import os
import smtplib
import threading
import time
from email.message import EmailMessage
from enum import Enum
from typing import Optional

from loguru import logger
from py_spring_core import Component, Properties
from pydantic import Field


class ServiceProvider(Enum):
    Google = "google"


class EmailDomainNowAllowedError(Exception): ...


class SmtpProperties(Properties):
    __key__ = "smtp"
    company_name: str
    host: str
    port: int
    sender_email: str
    sender_password: str
    allowed_domains: list[str]
    is_dry_run: bool = Field(default=True)

    service_provider: Optional[ServiceProvider] = Field(default=None)


class _GoogleSmtpProperties(SmtpProperties):
    host: str = Field(default="smtp.gmail.com")
    port: int = Field(default=587)
    sender_email: str
    sender_password: str


class EmailContentType(str, Enum):
    PLAIN = "plain"
    HTML = "html"


class SmtpService(Component):
    smtp_properties: SmtpProperties

    def __init__(self) -> None:
        self.email_queue: list[EmailMessage] = []
        self._handle_email_messages()
        self.queue_lock = threading.Lock()  # Initialize a lock

    def post_construct(self) -> None:
        self._properties_post_init()

    def _properties_post_init(self) -> None:
        match self.smtp_properties.service_provider:
            case ServiceProvider.Google:
                logger.info(f"[SMTP SERVICE] Using Google SMTP Service...")
                self.smtp_properties = _GoogleSmtpProperties(
                    company_name=self.smtp_properties.company_name,
                    sender_email=self.smtp_properties.sender_email,
                    sender_password=self.smtp_properties.sender_password,
                    allowed_domains=self.smtp_properties.allowed_domains,
                    is_dry_run=self.smtp_properties.is_dry_run,
                )

    def get_company_name(self) -> str:
        return self.smtp_properties.company_name

    @classmethod
    def create_email_message(
        cls,
        receiver_email: str,
        subject: str,
        content: str,
        content_type: EmailContentType,
        attachment_path: Optional[str] = None,
        attachment_file_name: Optional[str] = None,
    ) -> EmailMessage:
        is_allowed = False
        for domain in cls.smtp_properties.allowed_domains:
            if receiver_email.endswith(domain):
                is_allowed = True
                break
        if not is_allowed:
            raise EmailDomainNowAllowedError(
                f"Email Domain: {receiver_email} is not allowed"
            )

        message = EmailMessage()
        message["From"] = cls.smtp_properties.sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.set_content(content, subtype=content_type)
        if attachment_path is not None:
            cls._attach_file(message, attachment_path, attachment_file_name)
        return message

    @classmethod
    def _attach_file(
        cls,
        message: EmailMessage,
        attachment_path: str,
        attachment_file_name: Optional[str] = None,
    ) -> None:
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = attachment_file_name or os.path.basename(attachment_path)
            logger.info(f"[EMAIL ATTACHMENT] Attaching file {file_name} to email...")
            message.add_attachment(
                file_data,
                maintype="application",
                subtype="octet-stream",
                filename=file_name,
            )

    def async_send_email(self, email_message: EmailMessage) -> bool:
        with self.queue_lock:
            self.email_queue.append(email_message)  # Acquire lock before appending
        return True

    def _get_email(self) -> Optional[EmailMessage]:
        with self.queue_lock:
            if len(self.email_queue) == 0:
                return None
            return self.email_queue.pop(0)

    def _push_back_email_to_queue(self, email_message: EmailMessage) -> None:
        with self.queue_lock:
            self.email_queue.append(email_message)  # Acquire lock before appending

    def _send_email(self, email_message: EmailMessage) -> bool:
        try:
            with smtplib.SMTP(
                self.smtp_properties.host, self.smtp_properties.port
            ) as smtp:
                smtp.starttls()
                sender = self.smtp_properties.sender_email
                password = self.smtp_properties.sender_password
                smtp.login(sender, password)
                smtp.sendmail(sender, email_message["To"], email_message.as_string())
                logger.success(
                    f"[EMAIL SENDING SUCCESSFULLY] Sending email to {email_message['To']}"
                )
        except Exception as error:
            logger.error(error)
            return False
        return True

    def _handle_email_messages(self) -> None:
        def wrapper() -> None:
            while True:
                time.sleep(1)
                email_message = self._get_email()
                if email_message is None:
                    continue

                if self.smtp_properties.is_dry_run:
                    logger.info(f"[DRY RUN] Sending email to {email_message['To']}")
                    continue

                is_sent = self._send_email(email_message)
                if not is_sent:
                    logger.error(
                        f"[EMAIL SENDING FAILED] Failed to send email to {email_message['To']}, push back to queue."
                    )
                    self._push_back_email_to_queue(email_message)

        threading.Thread(target=wrapper).start()
