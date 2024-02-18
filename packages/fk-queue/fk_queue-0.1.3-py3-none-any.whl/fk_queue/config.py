import os


class Config:
    def __init__(self):
        self.ENVIRONMENT = os.environ.get('ENVIRONMENT', 'localhost')
        self.DD_ENV = os.environ.get('DD_ENV', 'localhost')
        self.AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME', 'us-east-1')
        self.AWS_SQS_URL = os.environ.get('AWS_SQS_URL')
        self.AWS_SQS_SMS = os.environ.get('AWS_SQS_SMS', 'sqs-send-sms')
        self.AWS_SQS_EMAIL = os.environ.get('AWS_SQS_EMAIL', 'sqs-send-email')
        self.AWS_SQS_SLACK = os.environ.get('AWS_SQS_SLACK', 'sqs-send-slack')
        self.AWS_SQS_LOG = os.environ.get('AWS_SQS_LOG', 'sqs-send-logs')
        self.AWS_SQS_AUDIT = os.environ.get('AWS_SQS_AUDIT', 'sqs-send-audit')
        self.AWS_SQS_BITACORA = os.environ.get('AWS_SQS_BITACORA', 'sqs-send-bitacora')
