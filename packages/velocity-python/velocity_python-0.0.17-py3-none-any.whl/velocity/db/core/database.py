class Database(object):
    
    def __init__(self, tx, name=None):
        self.tx = tx
        self.name = name or self.tx.engine.config['database']
        self.sql = tx.engine.sql

    def __str__(self):
        return """
    Engine: %s
    Database: %s
    (db exists) %s
    Tables: %s
        """ % (
        self.tx.engine.sql.server,
        self.name,
        self.exists(),
        len(self.tables)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.close()

    def close(self):
        try:
            self._cursor.close()
            #print("*** database('{}').cursor.close()".format(self.name))
        except AttributeError:
            pass

    @property
    def cursor(self):
        try:
            return self._cursor
        except AttributeError:
            #print("*** database('{}').cursor.open()".format(self.name))
            self._cursor = self.tx.cursor()
        return self._cursor

    def drop(self):
        sql, vals = self.engine.sql.drop_database(self.name)
        self.tx.execute(sql, vals, single=True, cursor=self.cursor)

    def create(self):
        sql, vals = self.engine.sql.create_database(self.name)
        self.tx.execute(sql, vals, single=True, cursor=self.cursor)

    def exists(self):
        sql, vals = self.sql.databases()
        result = self.tx.execute(sql, vals, cursor=self.cursor)
        return bool(self.name in [x[0] for x in result.as_tuple()])

    @property
    def tables(self):
        sql, vals = self.sql.tables()
        result = self.tx.execute(sql ,vals, cursor=self.cursor)
        return ["%s.%s" % x for x in result.as_tuple()]

    def reindex(self):
        sql, vals = "REINDEX DATABASE {}".format(self.name), tuple()
        self.tx.execute(sql, vals, cursor=self.cursor)
