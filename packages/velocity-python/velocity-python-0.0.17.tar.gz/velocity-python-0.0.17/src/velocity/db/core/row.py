import pprint

class Row(object):
    def __init__(self, table, key):
        if  isinstance(table, str):
            raise Exception("table parameter of row class must `table` instance")
        self.table = table
        if isinstance(key,(dict,Row)):
            pk = {}
            try:
                for k in self.key_cols:
                    pk[k] = key[k]
            except KeyError:
                pk = key
        else:
            pk = { self.key_cols[0]: key }
        self.pk = pk
        self.cache = key

    def __repr__(self):
        return repr(self.to_dict())

    def __str__(self):
        return pprint.pformat(self.to_dict())

    def __len__(self):
        return int(self.table.count(self.pk))

    def __getitem__(self, key):
        if key in self.pk:
            return self.pk[key]
        return self.table.get_value(key, self.pk)

    def __setitem__(self, key, val):
        if key in self.pk:
            raise Exception("Can't update a primary key, idiot!")
        self.table.upsert({key: val}, self.pk)

    def __delitem__(self, key):
        if key in self.pk:
            raise Exception("Can't delete a primary key, idiot!")
        if key not in self:
            return
        self[key] = None

    def __contains__(self, key):
        return key.lower() in [x.lower() for x in self.keys()]

    def clear(self):
        self.table.delete(where=self.pk)
        return self

    def keys(self):
        return self.table.sys_columns

    def values(self, *args):
        d = self.table.select(where=self.pk).as_dict().one()
        if args:
            values = []
            for arg in args:
                values.append(d[arg])
            return values
        else:
            return list(d.values())

    def items(self):
        d = self.table.select(where=self.pk).as_dict().one()
        return list(d.items())

    def get(self, key, failobj=None):
        data = self[key]
        if data == None:
            return failobj
        return data

    def setdefault(self, key, default=None):
        data = self[key]
        if data == None:
            self[key] = default
            return default
        return data


    def update(self, dict=None, **kwds):
        data = {}
        if dict:
            data.update(dict)
        if kwds:
            data.update(kwds)
        if data:
            self.table.upsert(data, self.pk)
        return self

    def iterkeys(self):
        return list(self.keys())

    def itervalues(self):
        return list(self.values())

    def iteritems(self):
        return list(self.items())

    def __cmp__(self, other):
        # zero == same (not less than or greater than other)
        diff = -1
        if hasattr(other,'keys'):
            k1 = list(self.keys())
            k2 = list(other.keys())
            if k1 == k2:
                diff = 0
                for k in k1:
                    if self[k] != other[k]:
                        diff = -1
                        break
        return diff

    def __bool__(self):
        return bool(self.__len__())

    def copy(self):
        old = self.to_dict()
        for key in list(old.keys()):
            if 'sys_' in key:
                old.pop(key)
        return self.table.new(old)

    #================================================================
    # This stuff is not implemented

    def pop(self): raise NotImplementedError
    def popitem(self): raise NotImplementedError


    def __lt__(self,other): raise NotImplementedError
    def __gt__(self,other): raise NotImplementedError
    def __le__(self,other): raise NotImplementedError
    def __ge__(self,other): raise NotImplementedError

    @classmethod
    def fromkeys(cls, iterable, value=None): raise NotImplementedError

    def to_dict(self):
        return self.table.select(where=self.pk).as_dict().one()

    def extract(self, *args):
        data = {}
        for key in args:
            if isinstance(key,(tuple,list)):
                data.update(self.extract(*key))
            else:
                data[key] = self[key]
        return data

    @property
    def key_cols(self):
        #result = self.execute(*self.sql.primary_keys(self.tablename))
        #return [x[0] for x in result.as_tuple()]
        return ['sys_id']

    def split(self):
        old = self.to_dict()
        for key in old.keys():
            if 'sys_' in key:
                old.pop(key)
        return old, self.pk

    @property
    def data(self):
        return self.split()[0]

    def row(self, key):
        tx = self.table.tx
        value = self[key]
        if value is None:
            return None
        fk = self.table.foreign_key_info(key)
        if not fk:
            raise Exception("Column `{}` is not a foreign key in `{}`".format(key, self.table.name))
        return tx.Row(fk['referenced_table_name'],value)

    def match(self, other):
        for key in other:
            if self[key] != other[key]:
                return False
        return True

    def touch(self):
        self['sys_modified'] = '@@CURRENT_TIMESTAMP'
        return self

    delete = clear
