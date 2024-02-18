from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS
from typing import List, Dict


class EmailSender:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_EMAIL}-{SETTINGS.DD_ENV}"
        self.path = "/email/"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def send_email(self, to: str, cc: List, data: Dict,
                   subject: str, message: str, attachment: List,
                   alpha2: str, template: str) -> bool:
        """
        Envía un correo electrónico.

        :param to: El destinatario del correo electrónico.
        :param cc: Lista de destinatarios en copia (CC).
        :param data: Datos adicionales para el correo electrónico.
        :param subject: El asunto del correo electrónico.
        :param message: El contenido del correo electrónico.
        :param attachment: Lista de archivos adjuntos.
        :param alpha2: Código alfa-2 (por ejemplo, 'CO').
        :param template: Nombre del template a utilizar.
        :return: True si el correo se envía con éxito, False en caso contrario.
        """

        try:
            email_data = {
                "to": to,
                "cc": cc,
                "data": data,
                "subject": subject,
                "message": message,
                "attachment": attachment,
                "alpha2": alpha2,
                "template": template
            }
            send = self.client.send_message(email_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al enviar el correo electrónico: {str(e)}")
            return False
