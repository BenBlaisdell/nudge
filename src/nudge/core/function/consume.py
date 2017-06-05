import revolio as rv

from nudge.core.entity import Element, Batch


class Consume(rv.Function):

    def __init__(self, ctx, log, db, batch_srv, elem_srv):
        super().__init__(ctx)
        self._log = log
        self._db = db
        self._batch_srv = batch_srv
        self._elem_srv = elem_srv

    def format_request(self, sub_id, batch_id):
        return {
            'SubscriptionId': sub_id,
            'BatchId': batch_id,
        }

    def handle_request(self, request):
        self._log.info('Handling request: Consume')

        # parse parameters

        sub_id = request['SubscriptionId']
        assert isinstance(sub_id, str)

        batch_id = request['BatchId']
        assert isinstance(batch_id, str)

        # make call

        self(
            sub_id=sub_id,
            batch_id=batch_id,
        )

        # format response

        return {'Message': 'Success'}

    def __call__(self, sub_id, batch_id):
        self._log.info('Handling call: Consume')

        batch = self._batch_srv.get_batch(batch_id)
        assert batch.sub_id == sub_id
        batch.state = Batch.State.Consumed

        for elem in self._elem_srv.get_batch_elems(batch):
            elem.state = Element.State.Consumed

        self._db.commit()
