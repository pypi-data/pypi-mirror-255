import decimal
import json
from datetime import datetime, date, time, timedelta


def gallons(data):
    if data is None:
        return ''
    data = decimal.Decimal(data)
    return "{:.2f}".format(data)
    # return "{:1,.2f} gals".format(data)


def gallons2liters(data):
    if data is None:
        return ''
    data = decimal.Decimal(data) * decimal.Decimal(3.78541)
    return "{:.2f}".format(data)
    # return "{:1,.2f} liters".format(data)


def currency(data):
    if data is None:
        return ''
    decimal.Decimal(data)
    return "{:.2f}".format(data)
    # return "${:1,.2f}".format(data)


def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    Usage:
        # 149 day(s) 8 hr(s) 36 min 19 sec
        print(human_delta(datetime(2014, 3, 30) - datetime.now()))
    Example Results:
        23 sec
        12 min 45 sec
        1 hr(s) 11 min 2 sec
        3 day(s) 13 hr(s) 56 min 34 sec
    :param tdelta: The timedelta object.
    :return: The human formatted timedelta
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] == 0:
        fmt = '{sec} sec'
    elif d['hrs'] == 0:
        fmt = '{min} min {sec} sec'
    elif d['days'] == 0:
        fmt = '{hrs} hr(s) {min} min {sec} sec'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'

    return fmt.format(**d)


def to_json(o, datefmt="%Y-%m-%d", timefmt="%H:%M:%S"):
    class JsonEncoder(json.JSONEncoder):
        def default(self, o):
            if hasattr(o, 'to_json'):
                return o.to_json()
            elif o is None:
                return 0
            elif isinstance(o, decimal.Decimal):
                return float(o)
            elif isinstance(o, date):
                return o.strftime(datefmt)
            elif isinstance(o, datetime):
                return o.strftime("{} {}".format(datefmt, timefmt))
            elif isinstance(o, time):
                return o.strftime(timefmt)
            elif isinstance(o, timedelta):
                return human_delta(o)
            try:
                return super(JsonEncoder, self).default(o)
            except:
                return str(o)
    return json.dumps(o, cls=JsonEncoder)
