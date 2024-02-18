class Sequence(object):
    def __init__(self, tx, name, start=1000):
        self.tx = tx
        self.name = name.lower()
        self.sql = tx.engine.sql
        self.start = start

        self.create()

    def __str__(self):
        return """
    Sequence: %s
        """ % ( self.name )

    def create(self):
        sql, vals = "CREATE SEQUENCE IF NOT EXISTS {} START {};".format(self.name, self.start), tuple()
        return self.tx.execute(sql, vals)

    def next(self):
        sql, vals = "SELECT nextval('{}');".format(self.name), tuple()
        return self.tx.execute(sql, vals).scalar()

    def current(self):
        sql, vals = "SELECT currval('{}');".format(self.name), tuple()
        return self.tx.execute(sql, vals).scalar()

    def reset(self, start=None):
        sql, vals = "ALTER SEQUENCE {} RESTART WITH {};".format(self.name, start or self.start), tuple()
        return self.tx.execute(sql, vals).scalar()

    def drop(self):
        sql, vals = "DROP SEQUENCE IF EXISTS {};".format(self.name), tuple()
        return self.tx.execute(sql, vals)
