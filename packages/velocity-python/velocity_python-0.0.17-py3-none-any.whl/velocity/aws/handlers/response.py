from velocity.misc.format import to_json
import sys
import traceback
from velocity.aws import DEBUG


variants = [
    'success',
    'error',
    'warning',
    'info'
]


class Response:
    def __init__(self):
        self.actions = []
        self.body = {
            'actions': self.actions
        }
        self.raw = {
            'statusCode': 200,
            'body': '{}',
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
        }

    def render(self):
        self.raw['body'] = to_json(self.body)
        return self.raw

    def alert(self, message, title="Notification"):
        self.actions.append({
            'action': 'alert',
            'payload':  {
                'title': title,
                'message':  message,
            }
        })
        return self

    def toast(self, message, variant='success'):
        variant = variant.lower()
        if variant not in variants:
            raise Exception(f"Notistack variant {variant} not in {variants}")
        self.actions.append({
            'action': 'toast',
            'payload': {
                'options': {
                    'variant': variant,
                },
                'message': message
            }
        })
        return self

    def load_object(self, payload):
        self.actions.append({
            'action': 'load-object',
            'payload': payload
        })
        return self

    def update_store(self, payload):
        self.actions.append({
            'action': 'update-store',
            'payload': payload
        })
        return self

    def file_download(self, payload):
        self.actions.append({
            'action': 'file-download',
            'payload': payload
        })
        return self

    def status(self, code=None):
        if code:
            self.raw['statusCode'] = int(code)
        return self.raw['statusCode']

    def headers(self, headers=None):
        if headers:
            new = {}
            for key in headers.keys():
                new["-".join(w.capitalize()
                             for w in key.split('-'))] = headers[key]
            self.raw['headers'].update(new)
        return self.raw['headers']

    def set_status(self, code):
        self.status(code)
        return self

    def set_headers(self, headers):
        self.headers(headers)
        return self

    def set_body(self, body):
        self.body.update(body)
        return self

    def exception(self):
        t, v, tb = sys.exc_info()
        self.set_status(500)
        self.set_body({
            'python_exception': {
                'type': str(t),
                'value': str(v),
                'traceback': traceback.format_exc() if DEBUG else None,
                'tb': traceback.format_tb(tb) if DEBUG else None
            }
        })

    def console(self, message, title="Notification"):
        self.actions.append({
            'action': 'console',
            'payload':  {
                'title': title,
                'message':  message,
            }
        })
        return self

    def redirect(self, location):
        self.actions.append({
            'action': 'redirect',
            'payload': {'location': location}
        })
        return self

    def signout(self, location):
        self.actions.append({
            'action': 'signout',

        })
        return self

    def set_table(self, payload):
        self.actions.append({
            'action': 'set-table',
            'payload': payload
        })
        return self

    def set_repo(self, payload):
        self.actions.append({
            'action': 'set-repo',
            'payload': payload
        })
        return self