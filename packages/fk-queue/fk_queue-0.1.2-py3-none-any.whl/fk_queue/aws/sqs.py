import boto3
import json
import base64
from fk_queue import SETTINGS


class SQSMessageSender:
    def __init__(self, queue_url):
        session = boto3.Session(region_name=SETTINGS.AWS_REGION_NAME)
        self.queue_url = queue_url
        self.sqs = session.client('sqs')

    def send_message(self, message: str, path: str, method: str) -> bool:
        """
        Envía un mensaje a la cola SQS.

        :param message: El cuerpo del mensaje que se enviará.
        :param path: La ruta lambda a consumir.
        :param method: El método a utilizar en el consumo.
        :return: El ID del mensaje enviado.
        """

        # Serializa el objeto JSON a una cadena
        json_string = json.dumps(message)

        # Codifica la cadena en Base64
        base64_encoded = base64.b64encode(json_string.encode()).decode()
        python_obj = {"data": base64_encoded, "path": path, "method": method}

        # Convierte el objeto a una cadena JSON
        message_body = json.dumps(python_obj)

        if SETTINGS.DD_ENV in ["localhost"]:
            print("Sending message in test DD_ENV:")
            print(f"Message: {message_body}")
            return True

        try:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body
            )
            return True
        except Exception as e:
            print(f"Error al enviar el mensaje: {str(e)}")
            return False
