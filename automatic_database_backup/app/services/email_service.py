from flask_mail import Message
from flask import current_app
from app import mail

class EmailService:
    @staticmethod
    def send_backup_report(success, details):
        """Отправка отчета о бэкапе"""
        try:
            recipient = current_app.config.get('MAIL_RECIPIENT')
            sender = current_app.config.get('MAIL_DEFAULT_SENDER', 'backup@cubinez.ru')

            if not recipient:
                current_app.logger.warning("MAIL_RECIPIENT not configured, skipping email")
                return

            # Форматируем детали в читаемый вид
            if isinstance(details, dict):
                details_text = "\n".join([f"{k}: {v}" for k, v in details.items()])
            else:
                details_text = str(details)

            # Статус с эмодзи
            status_emoji = "✅" if success else "❌"
            status_text = "Success" if success else "Failed"
            
            subject = f"{status_emoji} Backup {status_text}"
            body = f"Backup status: {status_text} {status_emoji}\n\n{details_text}"

            msg = Message(
                subject=subject,
                sender=sender,
                recipients=[recipient],
                body=body
            )

            mail.send(msg)
            current_app.logger.info(f"Email sent to {recipient}")
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")

    @staticmethod
    def send_error_notification(error_msg):
        """Отправка уведомления об ошибке"""
        EmailService.send_backup_report(False, {'error': error_msg})
