import abc
import enum

import revolio as rv


class EndpointProtocol(enum.Enum):
    SQS = 'SQS'


class Endpoint(rv.Serializable):

    @staticmethod
    def deserialize(data):
        protocol = EndpointProtocol[data['Protocol']]
        params = data['Parameters']

        if protocol == EndpointProtocol.SQS:
            return SqsEndpoint.deserialize(params)

    @abc.abstractmethod
    def send_message(self, ctx, msg):
        pass


class SqsEndpoint(Endpoint):

    def __init__(self, queue_url):
        super(SqsEndpoint, self).__init__()
        self._queue_url = queue_url

    def serialize(self):
        return {
            'Protocol': 'SQS',
            'Parameters': {
                'QueueUrl': self._queue_url,
            },
        }

    @staticmethod
    def deserialize(data):
        return SqsEndpoint(queue_url=data['QueueUrl'])

    def send_message(self, ctx, msg):
        ctx.sqs.send_message(
            QueueUrl=self._queue_url,
            MessageBody=msg,
        )