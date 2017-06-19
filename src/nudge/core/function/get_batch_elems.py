import datetime as dt

import revolio as rv

from nudge.core.entity.subscription import Subscription
from nudge.core.util import autocommit


class GetBatchElements(rv.Function):

    def __init__(self, ctx, elem_srv, db):
        super().__init__(ctx)
        self._elem_srv = elem_srv
        self._db = db

    def format_request(self, sub_id, batch_id, *, offset=0, limit=None):
        return {
            'SubscriptionId': sub_id,
            'BatchId': batch_id,
            'Offset': offset,
            'Limit': limit,
        }

    def handle_request(self, request):
        sub_id = request['SubscriptionId']
        assert isinstance(sub_id, str)

        batch_id = request['BatchId']
        assert isinstance(batch_id, str)

        offset = request.get('Offset', 0)
        assert isinstance(offset, int)

        limit = request.get('Limit', None)
        assert isinstance(limit, int) or (limit is None)

        # make call
        elems = self(
            sub_id=sub_id,
            batch_id=batch_id,
            offset=offset,
            limit=limit,
        )

        # format response
        return {
            'SubscriptionId': sub_id,
            'BatchId': batch_id,
            'Elements': [
                {
                    'Id': elem.id,
                    'Bucket': elem.bucket,
                    'Key': elem.key,
                    'Size': elem.size,
                    'Created': elem.s3_created.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for elem in elems
            ],
        }

    @autocommit
    def __call__(self, sub_id, batch_id, *, offset=0, limit=None):
        return self._elem_srv.get_batch_elems(
            sub_id=sub_id,
            batch_id=batch_id,
            offset=offset,
            limit=limit,
        )