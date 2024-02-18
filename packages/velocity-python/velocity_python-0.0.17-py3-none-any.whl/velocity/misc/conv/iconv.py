import re
import codecs
import decimal
from email.utils import parseaddr
from datetime import datetime


def none(data):
    if data == '':
        return None
    if data == 'null':
        return None
    if data == '@NULL':
        return None
    return data


def phone(data):
    if data == 'None':
        return None
    if not data:
        return data
    return re.search(r'\d{10}$', re.sub("[^0-9]", "", data)).group()


def day_of_week(data):
    if not data:
        return data
    return {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
        'sunday': 7,
        'mon': 1,
        'tue': 2,
        'wed': 3,
        'thu': 4,
        'fri': 5,
        'sat': 6,
        'sun': 7
    }[data.lower()]


def date(*args, **kwds):
    kwds.setdefault('fmt', '%Y-%m-%d')
    def _(param):
        if isinstance(param,str):
            return datetime.strptime(param, kwds['fmt']).date()
        else:
            return param
    if args and args[0]:
        return _(args[0])
    return _


def time(*args, **kwds):
    kwds.setdefault('fmt','%X')
    def _(param):
        if isinstance(param, str):
            return datetime.strptime(param, kwds['fmt']).time()
        else:
            return param
    if args and args[0]:
        return _(args[0])
    return _


def timestamp(*args, **kwds):
    kwds.setdefault('fmt','%c')
    def _(param):
        if isinstance(param, str):
            return datetime.strptime(param, kwds['fmt'])
        else:
            return param
    if args and args[0]:
        return _(args[0])
    return _


def email(data):
    if not data:
        return None
    if data == 'None':
        return None
    data = data.strip().lower()
    if '@' not in data:
        raise Exception()
    email = parseaddr(data)[1]
    mailbox,domain = email.split('@')
    if '.' in domain:
        if len(domain.split('.')[1]) < 1:
            raise Exception()
    else:
        raise Exception()
    return data


def integer(data):
    return int(re.sub("[^0-9\.-]", "", str(data)))


def boolean(data):
    if isinstance(data,str):
        if data.lower() in ['false','','f','off','no']:
            return False
    return bool(data)


def rot13(data):
    return codecs.encode(data,'rot13')


def pointer(data):
    if data == '@new': return data
    if data == '': return None
    if data == None: return None
    if data == '@NULL': return None
    return int(data)


def money(data):
    if data == 'None':
        return None
    if not data:
        return data
    return decimal.Decimal(re.sub("[^0-9\.-]", "", str(data)))


def round(precision, data=None):
    def function(data):
        if data == 'None':
            return None
        if not data:
            return data
        if isinstance(data, str):
            data = re.sub("[^0-9\.-]", "", data)
        return decimal.Decimal(data).quantize(decimal.Decimal(10) ** -precision, rounding=decimal.ROUND_HALF_UP)
    if data == None:
        return function
    return function(data)


def decimal(data):
    if data == 'None':
        return None
    if not data:
        return data
    return decimal.Decimal(re.sub("[^0-9\.-]", "", str(data)))


def ein(data):
    if data == 'None':
        return None
    if not data:
        return data
    return re.search(r'^\d{9}$', re.sub("[^0-9]", "", data)).group()


def list(data):
    if data in (None,'None'):
        return None
    if isinstance(data, str):
        if data[0] == '[':
            return data
    if not isinstance(data, list):
        data = [data]
    return repr(data)


def title(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    return str(data).title()


def lower(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    return str(data).lower()



def upper(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    return str(data).upper()


def padding(length, char):
    def inner(data):
        if data in [None,'None','']:
            return None
        return str(data).rjust(length, char)
    return inner


def string(data):
    if data == '':
        return None
    return str(data)


