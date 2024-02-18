from fk_queue.aws.sqs import SQSMessageSender
from fk_queue import SETTINGS


class EventLogger:
    def __init__(self):
        self.queue_url = f"{SETTINGS.AWS_SQS_URL}{SETTINGS.AWS_SQS_LOG}-{SETTINGS.DD_ENV}"
        self.path = "/log/"
        self.method = "POST"
        self.client = SQSMessageSender(self.queue_url)

    def create_log(self, user: str, rol: str, type_event: str, response_code: int,
                   request: dict, output: dict, server: dict, event: str,
                   execution_time: float) -> bool:
        """
        Registra un evento en el registro de eventos.

        :param user: El usuario relacionado con el evento.
        :param rol: El rol del usuario en el evento.
        :param type_event: El tipo de evento.
        :param response_code: El código de respuesta relacionado con el evento.
        :param request: Un diccionario que representa los datos de la solicitud.
        :param output: Un diccionario que representa la salida del evento.
        :param server: Un diccionario que representa información del servidor relacionada con el evento.
        :param event: Una descripción del evento.
        :param execution_time: El tiempo de ejecución del evento.

        :return: True si el registro del evento se envía con éxito, False en caso contrario.
        """
        try:
            event_data = {
                "user": user,
                "rol": rol,
                "type_event": type_event,
                "response_code": response_code,
                "request": request,
                "output": output,
                "server": server,
                "event": event,
                "execution_time": execution_time
            }
            send = self.client.send_message(event_data, self.path, self.method)
            return send
        except Exception as e:
            print(f"Error al registrar el evento: {str(e)}")
            return False
