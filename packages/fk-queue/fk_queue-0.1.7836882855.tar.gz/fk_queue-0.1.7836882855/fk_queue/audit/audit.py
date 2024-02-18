from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS
from typing import Union


class EventAudit:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_AUDIT}-{SETTINGS.DD_ENV}"
        self.path = "/audit/"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def create_audit(self, content_type: str, object_pk: str, object_repr: Union[dict, str],
                     action: str, changes: Union[dict, str], user: str,
                     remote_addr: Union[dict, str]) -> bool:
        """
        Registra una entrada en el registro de auditoría.

        :param content_type: El tipo de contenido relacionado con la auditoría.
        :param object_pk: La clave primaria del objeto relacionado con la auditoría.
        :param object_repr: Representación del objeto (puede ser un diccionario o una cadena).
        :param action: La acción realizada en la auditoría (por ejemplo, "CREATE", "UPDATE", "DELETE").
        :param changes: Cambios realizados en el objeto (puede ser un diccionario o una cadena).
        :param user: El usuario que realizó la acción de auditoría.
        :param remote_addr: La dirección remota desde la que se realizó la acción.

        :return: True si el registro de auditoría se envía con éxito, False en caso contrario.
        """
        try:
            audit_data = {
                "content_type": content_type,
                "object_pk": object_pk,
                "object_repr": object_repr,
                "action": action,
                "changes": changes,
                "user": user,
                "remote_addr": remote_addr
            }
            send = self.client.send_message(audit_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al registrar en el registro de auditoría: {str(e)}")
            return False
