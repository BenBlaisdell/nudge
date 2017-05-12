import enum
import re
import uuid

import marshmallow as mm
import sqlalchemy as sa
from nudge.endpoint import Endpoint

from nudge.entity.entity import Entity
from nudge.orm import SubscriptionOrm
from nudge.util import Serializable


class SubscriptionService:

    def __init__(self, db):
        super(SubscriptionService, self).__init__()
        self._db = db

    def get_subscription(self, sub_id):
        orm = self._db \
            .query(SubscriptionOrm) \
            .get(sub_id)

        if orm is None:
            raise Exception('No subscription with id {}'.format(sub_id))

        return Subscription(orm)

    def find_matching_subscriptions(self, bucket, key):
        return [
            Subscription(orm)
            for orm in self._db
                .query(SubscriptionOrm)
                .filter(SubscriptionOrm.bucket == bucket)
                .filter(sa.sql.expression.bindparam('k', key).startswith(SubscriptionOrm.prefix))
                .all()
        ]


class Subscription(Entity):

    @property
    def id(self):
        return self._orm.id

    class State(enum.Enum):
        Active = 'Active'
        Inactive = 'Inactive'

    @property
    def state(self):
        return Subscription.State[self._orm.state]

    @state.setter
    def state(self, state):
        assert isinstance(state, Subscription.State)
        self._orm.state = state.value

    @property
    def bucket(self):
        return self._orm.bucket

    @property
    def prefix(self):
        return self._orm.prefix

    @property
    def regex(self):
        return re.compile(self._orm.data['regex'])

    @property
    def threshold(self):
        return self._orm.data['threshold']

    @property
    def endpoint(self):
        return Endpoint.deserialize(self._orm.data['endpoint'])

    @staticmethod
    def create(bucket, endpoint, *, prefix=None, regex=None, threshold=0):
        return Subscription(SubscriptionOrm(
            id=str(uuid.uuid4()),
            state=Subscription.State.Active.value,
            bucket=bucket,
            prefix=prefix,
            data=dict(
                regex=regex,
                threshold=threshold,
                endpoint=endpoint,
            )
        ))


# schema


class SubscriptionEndpointSchema(mm.Schema):
    Protocol = mm.fields.Str()
    Params = mm.fields.Dict()


class SubscriptionSchema(mm.Schema):
    id = mm.fields.UUID(
        required=True,
    )

    state = mm.fields.Str(
        required=True,
    )

    bucket = mm.fields.Str(
        required=True,
    )

    prefix = mm.fields.Str(
        default=None,
    )

    regex = mm.fields.Str(
        default=None,
        help=' '.join([
            'The regular expression against which',
            'the remainder of the key is matched.',
            'Syntax follows that of the python re package.',
        ]),
    )

    threshold = mm.fields.Int(
        default=0,
        help='The byte threshold at which a subscription batch is created',
    )

    endpoint = mm.fields.Nested(
        SubscriptionEndpointSchema(),
    )

    @mm.post_load
    def return_subscription_entity(self, data):
        return Subscription(**data)
