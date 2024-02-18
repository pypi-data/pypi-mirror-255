from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS


class SlackSender:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_SLACK}-{SETTINGS.DD_ENV}"
        self.path = "/slack/notification"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def send_slack(self, title: str, message: str, channel: str) -> bool:
        """
        Envía un mensaje a un canal de Slack.

        :param title: El título del mensaje.
        :param message: El contenido del mensaje.
        :param channel: El canal de Slack al que se enviará el mensaje.
        :return: True si el mensaje se envía con éxito, False en caso contrario.
        """
        try:
            message_data = {
                "title": title,
                "message": message,
                "channel": channel
            }
            send = self.client.send_message(message_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al enviar el mensaje a Slack: {str(e)}")
            return False
