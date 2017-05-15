from nudge.entity.element import Element


class HandleObjectCreated:

    def __init__(self, db, sub_srv, batch_srv, elem_srv, log):
        self._db = db
        self._sub_srv = sub_srv
        self._batch_srv = batch_srv
        self._elem_srv = elem_srv
        self._log = log

    def __call__(self, bucket, key, **kwargs):
        self._log.info('Calling HandleObjectCreated')
        result = [
            self._handle_matching_sub(sub, bucket=bucket, key=key, **kwargs)
            for sub in self._sub_srv.find_matching_subscriptions(bucket, key)
        ]

        self._db.commit()
        return result

    def _handle_matching_sub(self, sub, **kwargs):
        elem = Element.create(sub_id=sub.id, **kwargs)
        self._db.add(elem)
        return elem, self._evaluate_sub(sub)

    def _evaluate_sub(self, sub):
        elems = self._elem_srv.get_sub_elems(sub)
        if _batch_size(elems) >= sub.threshold:
            self._batch_srv.send_batch(sub, elems)
            return True

        return False


def _batch_size(elems):
    return sum(e.size for e in elems)
