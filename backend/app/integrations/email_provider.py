import smtplib
import ssl
import email.utils
from email.message import EmailMessage
from typing import Optional
from datetime import datetime

from app.config.settings import Settings
from app.config.logging import get_logger

logger = get_logger(__name__)


class EmailNotificationProvider:
    """Email notification provider using SMTP.
    
    Configurable via environment variables:
    - APP_SMTP_HOST: SMTP server hostname
    - APP_SMTP_PORT: SMTP server port
    - APP_SMTP_TLS: Whether to use TLS (default: True)
    - APP_SMTP_USER: SMTP authentication username
    - APP_SMTP_PASSWORD: SMTP authentication password (reference only in env)
    - NOTIFICATIONS_RECIPIENT: Default email recipient
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or __import__("app.config.settings", fromlist=["Settings"]).Settings()
        self.host = self.settings.smtp_host or "smtp.gmail.com"
        self.port = self.settings.smtp_port or 587
        self.use_tls = self.settings.smtp_tls if hasattr(self.settings, "smtp_tls") else True
        self.username = self.settings.smtp_user
        self.password = self.settings.smtp_password
        self.default_recipient = self.settings.notifications_recipient
    
    def send_mail(
        self,
        subject: str,
        body: str,
        recipient: Optional[str] = None,
        sender: Optional[str] = None,
    ) -> bool:
        """Send an email notification.
        
        Args:
            subject: Email subject line
            body: Email body text
            recipient: Email address to send to (uses default if None)
            sender: Email address to send from (uses configured if None)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not self.username or not self.password:
            logger.warning("SMTP credentials not configured; skipping email send")
            return False
        
        recipient_email = recipient or self.default_recipient
        sender_email = sender or self.username
        
        if not recipient_email:
            logger.error("No recipient email configured; skipping email send")
            return False
        
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Date"] = email.utils.formatdate(localtime=True)
        message.set_content(body)
        
        context = ssl.create_default_context()
        try:
            if self.use_tls:
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls(context=context)
                    server.login(self.username, self.password)
                    server.send_message(message)
            else:
                with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
                    server.login(self.username, self.password)
                    server.send_message(message)
            
            logger.info(f"Email sent successfully to {recipient_email}: {subject}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False
    
    def send_alert_notification(self, alert_title: str, alert_description: str, alert_severity: str, alert_id: str) -> bool:
        """Send alert-specific notification.
        
        Args:
            alert_title: Title of the alert
            alert_description: Description of the alert
            alert_severity: Severity level (critical, high, medium, low)
            alert_id: Alert identifier
            
        Returns:
            True if email was sent successfully
        """
        severity_labels = {
            "critical": "CRITICAL",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
        }
        
        severity_label = severity_labels.get(alert_severity, "MEDIUM")
        
        subject = f"[{severity_label}] Security Alert: {alert_title}"
        body = f"""
Security Alert Detected

Alert ID: {alert_id}
Severity: {severity_label}
Title: {alert_title}
Description: {alert_description}

This is an automated notification from the Data Integrity & Security Monitoring Platform.

Please log in to the application to investigate and take appropriate action.
"""
        
        return self.send_mail(subject=subject, body=body)
    
    def send_file_integrity_notification(
        self,
        file_path: str,
        event_type: str,
        directory_name: str,
        severity: str,
    ) -> bool:
        """Send file integrity event notification.
        
        Args:
            file_path: Path of the file that changed
            event_type: Type of event (CREATED, MODIFIED, DELETED, etc.)
            directory_name: Name of the monitored directory
            severity: Severity level
            
        Returns:
            True if email was sent successfully
        """
        event_labels = {
            "CREATED": "File Created",
            "MODIFIED": "File Modified",
            "DELETED": "File Deleted",
            "MOVED": "File Moved",
            "PERMISSION_CHANGED": "Permission Changed",
            "SCAN_ERROR": "Scan Error",
        }
        
        event_label = event_labels.get(event_type, "File Event")
        
        subject = f"[FIM] {event_label} in {directory_name}"
        body = f"""
File Integrity Monitoring Alert

Directory: {directory_name}
File Path: {file_path}
Event Type: {event_label}
Severity: {severity}

A file integrity event has been detected. Please review the alert in the application for more details and take appropriate action if needed.
"""
        
        return self.send_mail(subject=subject, body=body)


# Singleton instance (lazy initialization)
_email_provider_instance: Optional[EmailNotificationProvider] = None


def get_email_notification_provider() -> EmailNotificationProvider:
    """Get the singleton email notification provider instance."""
    global _email_provider_instance
    if _email_provider_instance is None:
        _email_provider_instance = EmailNotificationProvider()
    return _email_provider_instance