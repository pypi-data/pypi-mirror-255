import re
import codecs
import decimal
from datetime import datetime, date, time
from pprint import pformat

def none(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    if data == 'null':
        return ''
    return data


def phone(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    if not data:
        return data
    data = re.search(r'\d{10}$', re.sub("[^0-9]", "", data)).group()
    return "({}) {}-{}".format(data[:3],data[3:6],data[6:])

def day_of_week(data, abbrev=False):
    if isinstance(data, list):
        new = []
        for day in data:
            new.append(day_of_week(day, abbrev=abbrev))
        return ','.join(new)
    if data == None:
        return ''
    if data == 'None':
        return ''
    if not data:
        return data
    if abbrev:
        return {
            1: 'Mon',
            2: 'Tue',
            3: 'Wed',
            4: 'Thu',
            5: 'Fri',
            6: 'Sat',
            7: 'Sun'
        }[int(data)]
    return {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday'
    }[int(data)]


def date(*args, **kwds):
    kwds.setdefault('fmt','%Y-%m-%d')
    def _(param):
        if isinstance(param,(datetime, date)):
            return param.strftime( kwds['fmt'] )
        else:
            return param
    if args and args[0]:
        return _(args[0])
    return _


def time(*args, **kwds):
    kwds.setdefault('fmt','%X')
    def _(param):
        if isinstance(param,(datetime, time)):
            return param.strftime( kwds['fmt'] )
        else:
            return param
    if args and args[0]:
        return _(args[0])
    return _


def timestamp(*args, **kwds):
    kwds.setdefault('fmt','%c')
    def _(param):
        if isinstance(param,(datetime)):
            return param.strftime( kwds['fmt'] )
        else:
            return param
    if args:
        return _(args[0])
    return _


def email(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    return data.lower()


def pointer(data):
    try:
        return int(data)
    except:
        return ''


def rot13(data):
    return codecs.decode(data,'rot13')


def boolean(data):
    if isinstance(data,str):
        if data.lower() in ['false','','f','off','no']:
            return False
    return bool(data)


def money(data):
    if data in [None,'']:
        return ''
    data = re.sub("[^0-9\.-]", "", str(data))
    return '${:,.2f}'.format(decimal.Decimal(data))


def round(precision, data=None):
    def function(data):
        data = re.sub("[^0-9\.]", "", str(data))
        if data == '':
            return '0'
        return '{:.{prec}f}'.format(decimal.Decimal(data), prec=precision)
    if data == None:
        return function
    return function(data)


def ein(data):
    if data == None:
        return ''
    if data == 'None':
        return ''
    if not data:
        return data
    data = re.search(r'\d{9}$', re.sub("[^0-9]", "", data)).group()
    return "{}-{}".format(data[:2],data[2:])


def list(data):
    if data in (None,'None'):
        return None
    if isinstance(data, list):
        return data
    if isinstance(data, str):
        if data[0] == '[':
            return eval(data)
    return [data]


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
        if data is None:
            return ''
        return str(data).rjust(length, char)
    return inner


def pprint(data):
    try:
        return pformat(eval(data))
    except:
        return data


def string(data):
    if data == None:
        return ''
    return str(data)
