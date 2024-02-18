from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS


class SMSSender:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_SMS}-{SETTINGS.DD_ENV}"
        self.path = "/sms/single"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Envía un mensaje de texto (SMS) a un número de teléfono.

        :param phone_number: El número de teléfono en formato E.164 (por ejemplo, +1234567890).
        :param message: El mensaje de texto que se enviará maximo 160 caracteres.
        :return: True si el mensaje se envía con éxito, False en caso contrario.
        """
        try:
            message_data = {
                "phone_number": phone_number,
                "message": message
            }
            send = self.client.send_message(message_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al enviar el mensaje: {str(e)}")
            return False
