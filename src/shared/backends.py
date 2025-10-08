"""Backend to send email using Office 365 SMTP server."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Tuple

import jinja2
from django.conf import settings


class Email365Client:
    """Office 365 email client com suporte a filas"""

    def __init__(
        self, mail_to: str, mail_subject: str, type_message: str, extra: Dict
    ) -> None:
        self.__extra = extra
        self.__type = type_message
        self.__mail_to = mail_to
        self.__message = MIMEMultipart("alternative")
        self.__message["Subject"] = mail_subject
        self.__message["From"] = settings.EMAIL_SOLUTIS_365
        self.__message["To"] = mail_to

    def __prepare_approval_message(self) -> str:
        """Build email"""
        template_loader = jinja2.FileSystemLoader(
            searchpath="./src/supplier/templates/"
        )
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template("resquet_approval.html")
        return template.render(
            approver_name=self.__extra.get("approver_name", ""),
            supplier=self.__extra.get("supplier", ""),
            step=self.__extra.get("step", ""),
            approval_link=self.__extra.get("approval_link", ""),
            reprove_link=self.__extra.get("reprove_link", ""),
        )

    def __prepare_message(self) -> None:
        """Build email"""
        output_text = ""
        if self.__type == "approval":
            output_text = self.__prepare_approval_message()
        self.__message.attach(MIMEText(output_text, "html"))

    def send_message(self, fake: bool = False) -> Tuple[bool, str]:
        """Try send message"""
        self.__prepare_message()
        try:
            with smtplib.SMTP(
                "smtp.office365.com", 587, local_hostname="solutis.com.br"
            ) as server:
                server.starttls()
                server.login(
                    settings.EMAIL_SOLUTIS_365, settings.EMAIL_PASSWORD_SOLUTIS_365
                )
                if fake:
                    return True, self.__mail_to
                server.sendmail(
                    settings.EMAIL_SOLUTIS_365,
                    self.__mail_to,
                    self.__message.as_string(),
                )
            return True, self.__mail_to
        except smtplib.SMTPAuthenticationError:
            return False, self.__mail_to
        except smtplib.SMTPRecipientsRefused:
            return False, self.__mail_to
