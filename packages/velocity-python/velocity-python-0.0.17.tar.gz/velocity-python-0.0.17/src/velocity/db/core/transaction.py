import re
from velocity.db.core.row import Row
from velocity.db.core.table import Table
from velocity.db.core.result import Result
from velocity.db.core.column import Column
from velocity.db.core.database import Database
from velocity.db.core.sequence import Sequence
from velocity.misc.db import randomword


debug = False

class Transaction(object):

    def __init__(self, engine, connection=None):
        self.engine = engine
        self.connection = connection

    def __str__(self):
        c = self.engine.config
        server = c.get('host',c.get('server'))
        database = c.get('database')
        return "{}.transaction({}:{})".format(
            self.engine.sql.server,
            server,
            database)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        self.close()

    def cursor(self):
        if not self.connection:
            if debug:
                print('>>> {} open connection to {database}'.format(id(self), **self.engine.config))
            self.connection = self.engine.connect()
        if debug:
           print("*** {} open {database}.transaction.connection.cursor".format(id(self), **self.engine.config))
        return self.connection.cursor()

    def close(self):
        if self.connection:
            self.commit()
            if debug:
                print('<<< {} close connection to {database}'.format(id(self), **self.engine.config))
            self.connection.close()

    def execute(self, sql, parms=None, single=False, cursor=None):
        return self._execute(sql, parms=parms, single=single, cursor=cursor)

    def _execute(self, sql, parms=None, single=False, cursor=None):
        if single:
            cursor = None
        if not self.connection:
            if debug:
                print('>>> {} open connection to {database}'.format(id(self), **self.engine.config))
            self.connection = self.engine.connect()
        action = re.search(r'(\w+)', sql, re.I)
        if action:
            action = action.group().lower()
        else:
            action = 'None'
        if debug:
            print(action)
            print(id(self), '------------>', sql, '::', parms)
            print()
        if single:
            self.commit()
            self.connection.autocommit = True
        if not cursor:
            cursor = self.cursor()
        try:
            if parms:
                cursor.execute(sql, parms)
            else:
                cursor.execute(sql)
        except:
            self.engine.ProcessError(sql,parms)
        if single:
            self.connection.autocommit = False
        return Result(cursor)

    def server_execute(self, sql, parms=None):
        return self._execute(sql, parms, cursor=self.cursor())

    def commit(self):
        if self.connection:
            if debug:
                print('{} --- connection commit {database}'.format(id(self), **self.engine.config))
            self.connection.commit()

    def rollback(self):
        if self.connection:
            if debug:
                print('{} --- connection rollback {database}'.format(id(self), **self.engine.config))
            self.connection.rollback()

    def create_savepoint(self, sp=None, cursor=None):
        if not sp:
            sp = randomword()
        sql, vals = self.engine.sql.create_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)
        return sp

    def release_savepoint(self, sp=None, cursor=None):
        sql, vals = self.engine.sql.release_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)

    def rollback_savepoint(self, sp=None, cursor=None):
        sql, vals = self.engine.sql.rollback_savepoint(sp)
        if sql:
            self._execute(sql, vals, cursor=cursor)

    def database(self, name=None):
        return Database(self, name)

    def table(self, tablename):
        return Table(self, tablename)

    def sequence(self, name):
        return Sequence(self, name)

    def row(self, tablename, pk):
        """
        Returns exactly one row based on primary key.
        raise exception if primary key not provided.
        """
        return Row(self.table(tablename), pk)

    def get(self, tablename, where):
        """
        Search for row. return row if 1 found.
        raise exception if duplicates found.
        return new if not found. (creates new/use find otherwise)
        """
        return self.table(tablename).get(where)

    def find(self, tablename, where):
        """
        Search for row. return row if 1 found.
        raise exception if duplicates found.
        return {} if not found. (Does not create new)
        """
        return self.table(tablename).find(where)

    def column(self, tablename, colname):
        return Column(self.table(tablename), colname)

    def current_database(self):
        sql, vals = self.engine.sql.current_database()
        return self.execute(sql, vals).scalar()

    def vacuum(self, analyze=True, full=False, reindex=True):
        self.connection = self.engine.connect()
        old_isolation_level = self.connection.isolation_level
        self.connection.set_isolation_level(0)
        sql = ["VACUUM"]
        if full:
            sql.append('FULL')
        if analyze:
            sql.append('ANALYZE')
        self.execute(' '.join(sql))
        print(self.current_database())
        if reindex:
            database = self.engine.config.get('database')
            self.execute("REINDEX DATABASE {}".format(database))
        self.connection.set_isolation_level(old_isolation_level)

    def tables(self):
        sql, vals = self.engine.sql.tables()
        result = self.execute(sql, vals)
        return ["%s.%s" % x for x in result.as_tuple()]
