from velocity.misc.format import to_json

class Result(object):
    def __init__(self, cursor=None):
        self._cursor = cursor
        if hasattr(cursor,'description') and cursor.description:
            self._headers = [x[0].lower() for x in cursor.description]
        else:
            self._headers = []
        self.as_dict()
        self.__as_strings = False
        self.__enumerate = False
        self.__count = -1

    @property
    def headers(self):
        if not self._headers:
            if self._cursor and hasattr(self._cursor, 'description'):
                self._headers = [x[0].lower() for x in self._cursor.description]
        return self._headers

    def __str__(self):
        return repr(self.all())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def __next__(self):
        if self._cursor:
            row = self._cursor.fetchone()
            if row:
                if self.__as_strings:
                    row = ['' if x is None else str(x)  for x in row]
                if self.__enumerate:
                    self.__count += 1
                    return (self.__count, self.transform(row))
                else:
                    return self.transform(row)
        raise StopIteration

    def batch(self, qty=1):
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                if results:
                    yield results
                    results = []
                    continue
                raise
            if len(results) == qty:
                yield results
                results = []

    def all(self):
        results = []
        while True:
            try:
                results.append(next(self))
            except StopIteration:
                break
        return results

    def __iter__(self):
        return self

    @property
    def cursor(self):
        return self._cursor

    def close(self):
        self._cursor.close()

    def as_dict(self):
        self.transform = lambda row: dict(list(zip(self.headers,row)))
        return self

    def as_json(self):
        self.transform = lambda row: to_json(dict(list(zip(self.headers,row))))
        return self

    def as_named_tuple(self):
        self.transform = lambda row: list(zip(self.headers,row))
        return self

    def as_list(self):
        self.transform = lambda row: list(row)
        return self

    def as_tuple(self):
        self.transform = lambda row: row
        return self

    def as_simple_list(self, pos=0):
        self.transform = lambda row: row[pos]
        return self

    def strings(self, as_strings=True):
        self.__as_strings = as_strings
        return self

    def scalar(self, default=None):
        if not self._cursor:
            return None
        val = self._cursor.fetchone()
        self._cursor.fetchall()
        return val[0] if val else default

    def one(self,default=None):
        try:
            return next(self)
        except StopIteration:
            return default
        finally:
            if self._cursor:
                self._cursor.fetchall()

    def get_table_data(self, headers=True, strings=True):
        self.as_list()
        rows = []
        for row in self:
            rows.append(['' if x is None else str(x)  for x in row])
        if isinstance(headers,list):
            rows.insert(0,[x.replace('_',' ').title() for x in headers])
        elif headers:
            rows.insert(0,[x.replace('_',' ').title() for x in self.headers])
        return rows

    def enum(self):
        self.__enumerate = True
        return self
    enumerate = enum
