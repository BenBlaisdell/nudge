from nudge.entity.subscription import Subscription


class Unsubscribe:

    def __init__(self, db, sub_srv, log):
        self._db = db
        self._sub_srv = sub_srv
        self._log = log

    def handle_request(self, request):
        self._log.info('Handling request: Unsubscribe')

        # parse parameters

        sub_id = request['SubscriptionId']
        assert isinstance(sub_id, str)

        # make call

        self(sub_id)

        # format response

        return {'Message': 'Success'}

    def __call__(self, sub_id):
        self._log.info('Handling call: Unsubscribe')

        sub = self._sub_srv.get_subscription(sub_id)
        assert sub.state == Subscription.State.Active

        sub.state = Subscription.State.Inactive
        self._db.commit()
