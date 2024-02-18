# FK Queue Communicator Documentation

FK Queue Communicator is a Python library that provides a range of functionalities for different communication channels and audit logging. It enables you to send messages via SMS, Slack, and email, and also allows you to manage audit logs, audit events, and event bitacora.

## Installation

You can install FK Queue Communicator using `pip`:

```bash
pip install  fk-queue --index-url https://__token__:glpat-1f8XR4U8qbG4shQyq8Lr@gitlab.com/api/v4/groups/76606224/-/packages/pypi/simple
```

# Usage

To use this library, first import the necessary classes and functions from the library. Here are the main components:

## Communication Channels

### Sending an SMS

```python
from fk_queue.communicator.sms import SMSSender

data_sms = {
    "message": "string",
    "phone_number": "+570000000000"
}

client_sms = SMSSender()
sms = client_sms.send_sms(**data_sms)
```

### Sending a Slack Message

```python
from fk_queue.communicator.slack import SlackSender

data_slack = {
    "title": "string",
    "channel": "string",
    "message": "string"
}

client_slack = SlackSender()
slack = client_slack.send_slack(**data_slack)
```

### Sending an Email

```python
from fk_queue.communicator.email import EmailSender

data_email = {
    "to": "user@example.com",
    "cc": [
        "user@example.com"
    ],
    "data": {
        "additionalProp1": "string",
        "additionalProp2": "string",
        "additionalProp3": "string"
    },
    "subject": "string",
    "message": "string",
    "attachment": [
        "string"
    ],
    "alpha2": "str",
    "template": "string"
}

client_email = EmailSender()
slack = client_email.send_email(**data_email)
```

### Audit Logging

```python
from fk_queue.audit.logs import EventLogger

data_log = {
    "user": "string",
    "rol": "string",
    "type_event": "string",
    "response_code": 0,
    "request": {},
    "output": {},
    "server": {},
    "event": "string",
    "execution_time": 0
}

client_log = EventLogger()
log = client_log.create_log(**data_log)
```

### Audit Events

```python
from fk_queue.audit.audit import EventAudit

data_audit = {
    "content_type": "string",
    "object_pk": "string",
    "object_repr": {},
    "action": "string",
    "changes": {},
    "user": "string",
    "remote_addr": {}
}

client_audit = EventAudit()
audit = client_audit.create_audit(**data_audit)
```

### Event Bitacora

Creating an Event Bitacora Entry

```python
from fk_queue.audit.bitacora import EventBitacora

data_bitacora = {
    "object_id": "string",
    "type": "USER_REQUEST",
    "observation": "string",
    "context": {},
    "automatic": true,
    "id_files": [
        0
    ],
    "user_created": {}
}

client_bitacora = EventBitacora()
bitacora = client_bitacora.create_bitacora(**data_bitacora)
```

## Dependencies

- boto3>=1.28.74

## License

[MIT](https://choosealicense.com/licenses/mit/)
