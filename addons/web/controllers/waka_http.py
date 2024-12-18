from odoo.http import Dispatcher
from abc import ABC, abstractmethod
import logging

_dispatchers = {}

def pre_dispatch(self, rule, args):
    """
    Prepare the system before dispatching the request to its
    controller. This method is often overridden in ir.http to
    extract some info from the request query-string or headers and
    to save them in the session or in the context.
    """
    routing = rule.endpoint.routing
    self.request.session.can_save = routing.get('save_session', True)
    set_header = self.request.future_response.headers.set
    cors = routing.get('cors')
    if cors:
        set_header('Access-Control-Allow-Origin', cors)
        set_header('Access-Control-Allow-Methods', (
            'POST' if routing['type'] == 'json'
            else ', '.join(routing['methods'] or ['GET', 'POST'])
        ))
    if cors and self.request.httprequest.method == 'OPTIONS':
        set_header('Access-Control-Max-Age', CORS_MAX_AGE)
        set_header('Access-Control-Allow-Headers',
                    'Origin, X-Requested-With, Content-Type, Accept, Authorization')
        werkzeug.exceptions.abort(Response(status=204))
Dispatcher.pre_dispatch = pre_dispatch