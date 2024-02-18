from functools import wraps
from velocity.db import exceptions

def retry_on_dup_key(function):
    @wraps(function)
    def retry_decorator(self, *args, **kwds):
        if hasattr(self, 'cursor'):
            cursor = self.cursor
        elif hasattr(self, 'table'):
            cursor = self.table.cursor
        sp = self.tx.create_savepoint(cursor=cursor)
        while True:
            try:
                return function(self, *args, **kwds)
            except exceptions.DbDuplicateKeyError:
                self.tx.rollback_savepoint(sp, cursor=cursor)
                continue
    return retry_decorator

def return_default(default=None):
    def decorator(function):
        function.default = default
        @wraps(function)
        def return_default(self, *args, **kwds):
            if hasattr(self, 'cursor'):
                cursor = self.cursor
            elif hasattr(self, 'table'):
                cursor = self.table.cursor
            sp = self.tx.create_savepoint(cursor=cursor)
            try:
                result = function(self, *args, **kwds)
            except (exceptions.DbApplicationError,
                    exceptions.DbTableMissingError,
                    exceptions.DbColumnMissingError,
                    exceptions.DbTruncationError,
                    StopIteration,
                    exceptions.DbObjectExistsError):
                self.tx.rollback_savepoint(sp, cursor=cursor)
                return function.default
            self.tx.release_savepoint(sp, cursor=cursor)
            return result
        return return_default
    return decorator


def create_missing(function):
    @wraps(function)
    def create_missing_decorator(self, *args, **kwds):
        if hasattr(self, 'cursor'):
            cursor = self.cursor
        elif hasattr(self, 'table'):
            cursor = self.table.cursor
        sp = self.tx.create_savepoint(cursor=cursor)
        try:
            result = function(self, *args, **kwds)
            self.tx.release_savepoint(sp, cursor=cursor)
        except exceptions.DbColumnMissingError:
            self.tx.rollback_savepoint(sp, cursor=cursor)
            data = {}
            if 'pk' in kwds:
                data.update(kwds['pk'])
            if 'data' in kwds:
                data.update(kwds['data'])
            for i in range(len(args)):
                if args[i]:
                    data.update(args[i])
            self.alter(data)
            result = function(self, *args, **kwds)
        except exceptions.DbTableMissingError:
            self.tx.rollback_savepoint(sp, cursor=cursor)
            data = {}
            if 'pk' in kwds:
                data.update(kwds['pk'])
            if 'data' in kwds:
                data.update(kwds['data'])
            for i in range(len(args)):
                data.update(args[i])
            self.create(data)
            result = function(self, *args, **kwds)
        return result
    return create_missing_decorator
