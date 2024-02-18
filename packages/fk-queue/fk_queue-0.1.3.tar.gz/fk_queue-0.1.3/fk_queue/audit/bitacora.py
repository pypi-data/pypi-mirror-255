from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS
from enum import Enum


class BitacoraType(Enum):
    USER_REQUEST = 'USER_REQUEST'
    CREDIT_REQUEST = 'CREDIT_REQUEST'
    OPERATION = 'OPERATION'
    DISBURSEMENT = 'DISBURSEMENT'
    REJECT_OPERATION = 'REJECT_OPERATION'


class EventBitacora:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_BITACORA}-{SETTINGS.DD_ENV}"
        self.path = "/bitacora/"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def create_bitacora(self, object_id: str, type: BitacoraType, observation: str, context: dict,
                        automatic: bool, id_files: list[int], user_created: dict) -> bool:
        """
        Registra una entrada en la bitácora.

        :param object_id: El identificador del objeto o entidad relacionada con el registro.
        :param type: El tipo de entrada en la bitácora.
        :param observation: Una descripción detallada del evento registrado.
        :param context: Un diccionario con información adicional relacionada con el registro.
        :param automatic: Indica si el registro es automático o no.
        :param id_files: Una lista de identificadores de archivos relacionados con el registro.
        :param user_created: Un diccionario que representa al usuario que creó el registro.

        :return: True si el registro se envía con éxito, False en caso contrario.
        """
        try:
            log_data = {
                "object_id": object_id,
                "type": type,
                "observation": observation,
                "context": context,
                "automatic": automatic,
                "id_files": id_files,
                "user_created": user_created
            }
            send = self.client.send_message(log_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al registrar en la bitácora: {str(e)}")
            return False
