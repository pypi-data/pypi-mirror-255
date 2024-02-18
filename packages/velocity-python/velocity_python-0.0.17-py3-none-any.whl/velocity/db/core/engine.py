from velocity.db import exceptions
from velocity.db.core.transaction import Transaction

from functools import wraps
import inspect, sys, re, traceback

class Engine(object):
    MAX_RETRIES = 100

    def __init__(self, driver, config, sql):
        self.__config = config
        self.__sql = sql
        self.__driver = driver

    def __str__(self):
        return """[{}] engine({})""".format(self.sql.server, self.config)

    def connect(self):
            """
            Connects to the database and returns the connection object.

            If the database is missing, it creates the database and then connects to it.

            Returns:
                conn: The connection object to the database.
            """
            try:
                conn = self.__connect()
            except exceptions.DbDatabaseMissingError:
                self.create_database()
                conn = self.__connect()
            if self.sql.server == 'SQLite3':
                conn.isolation_level = None
            return conn

    def __connect(self):
            """
            Connects to the database using the provided configuration.

            Returns:
                A connection object representing the connection to the database.

            Raises:
                Exception: If the configuration parameter is not handled properly.
                ProcessError is called to handle other exceptions.
            """
            try:
                if isinstance(self.config, dict):
                    return self.driver.connect(**self.config)
                elif isinstance(self.config, (tuple, list)):
                    return self.driver.connect(*self.config)
                elif isinstance(self.config, str):
                    return self.driver.connect(self.config)
                else:
                    raise Exception("Unhandled configuration parameter")
            except:
                self.ProcessError()
         

    def transaction(self, func_or_cls=None):
        """
        Decorator for defining a transaction. Use this to wrap a function, method, or class to automatically 
            start a transaction if necessary. If the function, method or class is called with a `tx` keyword argument, 
            it will use that transaction object instead of creating a new one. If the function, method or class 
            is called with a `tx` positional argument, it will use that transaction object instead of creating a new one. 
            If the function, method or class is called with a `tx` positional argument and a `tx` keyword argument, it will use the positional
            argument and ignore the keyword argument. If the function, method or class is called without a `tx` argument,
            it will create a new transaction object and use that.
        Args:
            func_or_cls: The function or class to be decorated.

        Returns:
            If `func_or_cls` is a function or method, returns a wrapped version of the function or method that
            automatically starts a transaction if necessary. If `func_or_cls` is a class, returns a subclass of
            `func_or_cls` that wraps all its methods with the transaction decorator. 
            
 

        If `func_or_cls` is not provided, returns a new `Transaction` object associated with the engine.
        """
        # If you are having trouble passing TWO transaction objects, for
        # example as a source database to draw data from, pass the second as
        # a keyword. For example:
        #       @engine.transaction
        #       def function(tx, src=src) <-- pass second as a kwd and tx will populate correctly.
        #           ...
        #
        engine = self
        if inspect.isfunction(func_or_cls) \
        or inspect.ismethod(func_or_cls):
            @wraps(func_or_cls)
            def NewFunction(*args, **kwds):
                tx = None
                names = list(inspect.signature(func_or_cls).parameters.keys())
                if '_tx' in names:
                    raise NameError(f'In function named `{func_or_cls.__name__}` You may not name a paramater `_tx`')
                if 'tx' not in names:
                    return func_or_cls(*args, **kwds)
                elif 'tx' in kwds:
                    if isinstance(kwds['tx'], Transaction):
                        tx = kwds['tx']
                    else:
                        raise TypeError(f'In function named `{func_or_cls.__name__}` keyword `tx` must be a Transaction object')
                elif 'tx' in names:
                    pos = names.index('tx')
                    if len(args) > pos \
                    and isinstance(args[pos], Transaction):
                        tx = args[pos]
                if tx:
                    return engine.exec_function(func_or_cls, tx, *args, **kwds)
                else:
                    with Transaction(engine) as tx:
                        pos = names.index('tx')
                        args = list(args)
                        args.insert(pos, tx)
                        args = tuple(args)
                        return engine.exec_function(func_or_cls, tx, *args, **kwds) 
            return NewFunction
        elif inspect.isclass(func_or_cls):
            class NewCls(func_or_cls):
                def __getattribute__(self, key):
                    attr = super(NewCls, self).__getattribute__(key)
                    if key in ['start_response']:
                        return attr
                    if inspect.ismethod(attr):
                        return engine.transaction(attr)
                    return attr
            return NewCls

        return Transaction(engine)
    

    def exec_function(self, function, _tx, *args, **kwds):
        """
        Executes the given function with the provided arguments and keyword arguments.
        If there is no transaction object, it executes the function without a transaction.
        
        If there is a transaction object, it executes the function within the transaction.
        If the function raises a `DbRetryTransaction` exception, it rolls back the transaction and retries.
        If the function raises a `DbLockTimeoutError` exception, it rolls back the transaction and retries.
        If any other exception occurs, it raises the exception.

        Args:
            function: The function to be executed.
            tx: The transaction object to be passed to the function.
            *args: Positional arguments to be passed to the function.
            **kwds: Keyword arguments to be passed to the function.

        Returns:
            The result of the function execution.

        Raises:
            DbRetryTransaction: If the maximum number of retries is exceeded.
            DbLockTimeoutError: If the maximum number of retries is exceeded.
            Any other exception raised by the function.
        """
        retry_count = 0
        tmout_count = 0
        if _tx is None:
            return function(*args, **kwds)
        else:
            while True:
                try:
                    return function(*args, **kwds)
                except exceptions.DbRetryTransaction as e:
                    if e.args and e.args[0]:
                        _tx.rollback()
                        continue
                    retry_count += 1
                    if retry_count > self.MAX_RETRIES:
                        raise
                    print('**Retry Transaction. Rollback and start over')
                    _tx.rollback()
                    continue
                except exceptions.DbLockTimeoutError:
                    tmout_count += 1
                    if tmout_count > self.MAX_RETRIES:
                        raise
                    print('**DbLockTimeoutError. Rollback and start over')
                    _tx.rollback()
                    continue
                except:
                    raise

    @property
    def driver(self):
        return self.__driver

    @property
    def config(self):
        return self.__config

    @property
    def sql(self):
        return self.__sql

    @property
    def version(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.version()
            return tx.execute(sql, vals).scalar()

    @property
    def timestamp(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.timestamp()
            return tx.execute(sql, vals).scalar()

    @property
    def user(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.user()
            return tx.execute(sql, vals).scalar()

    @property
    def databases(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.databases()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_database(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.current_database()
            return tx.execute(sql, vals).scalar()

    def create_database(self, name=None):
        old = None
        if name == None:
            old = self.config['database']
            self.set_config({'database':'postgres'})
            name = old
        with Transaction(self) as tx:
            sql, vals = self.sql.create_database(name)
            tx.execute(sql, vals, single=True)
        if old:
            self.set_config({'database':old})
        return self

    def switch_to_database(self, database):
        conf  = self.config
        if 'database' in conf:
            conf['database'] = database
        if 'dbname' in conf:
            conf['dbname'] = database
        return self

    def set_config(self, config):
        self.config.update(config)

    @property
    def schemas(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.schemas()
            result = tx.execute(sql, vals)
            return [x[0] for x in result.as_tuple()]

    @property
    def current_schema(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.current_schema()
            return tx.execute(sql, vals).scalar()

    @property
    def tables(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.tables()
            result = tx.execute(sql, vals)
            return ["%s.%s" % x for x in result.as_tuple()]

    @property
    def views(self):
        with Transaction(self) as tx:
            sql, vals = self.sql.views()
            result = tx.execute(sql, vals)
            return ["%s.%s" % x for x in result.as_tuple()]


    def ProcessError(self, sql_stmt=None, sql_params=None):
        sql = self.sql
        e = sys.exc_info()[1]
        msg = str(e).strip().lower()
        if isinstance(e,exceptions.DbException):
            raise
        if hasattr(e,'pgcode'):
            error_code = e.pgcode
            error_mesg = e.pgerror
        elif hasattr(e,'args') \
        and isinstance(e.args,(tuple,list)) \
        and len(e.args) > 1:
            error_code = e[0]
            error_mesg = e[1]
        elif hasattr(e,'number') \
        and hasattr(e,'text'):
            error_code = e.number
            error_mesg = e.text
        elif hasattr(e,'args') \
        and hasattr(e,'message'):
            # SQLite3
            error_code = None
            error_mesg = e.message
        else:
            raise
        if error_code in sql.ApplicationErrorCodes:
            raise exceptions.DbApplicationError(e)
        elif error_code in sql.ColumnMissingErrorCodes:
            raise exceptions.DbColumnMissingError(e)
        elif error_code in sql.TableMissingErrorCodes:
            raise exceptions.DbTableMissingError(e)
        elif error_code in sql.DatabaseMissingErrorCodes:
            raise exceptions.DbDatabaseMissingError(e)
        elif error_code in sql.ForeignKeyMissingErrorCodes:
            raise exceptions.DbForeignKeyMissingError(e)
        elif error_code in sql.TruncationErrorCodes:
            raise exceptions.DbTruncationError(e)
        elif error_code in sql.DataIntegrityErrorCodes:
            raise exceptions.DbDataIntegrityError(e)
        elif error_code in sql.ConnectionErrorCodes:
            raise exceptions.DbConnectionError(e)
        elif error_code in sql.DuplicateKeyErrorCodes:
            raise exceptions.DbDuplicateKeyError(e)
        elif re.search('key \(sys_id\)=\(\d+\) already exists.', msg, re.M):
            raise exceptions.DbDuplicateKeyError(e)
        elif error_code in sql.DatabaseObjectExistsErrorCodes:
            raise exceptions.DbObjectExistsError(e)
        elif error_code in sql.LockTimeoutErrorCodes:
            raise exceptions.DbLockTimeoutError(e)
        elif error_code in sql.RetryTransactionCodes:
            raise exceptions.DbRetryTransaction(e)
        elif re.findall('database.*does not exist', msg, re.M):
            raise exceptions.DbDatabaseMissingError(e)
        elif re.findall('no such database', msg, re.M):
            raise exceptions.DbDatabaseMissingError(e)
        elif re.findall('already exists', msg, re.M):
            raise exceptions.DbObjectExistsError(e)
        elif re.findall('server closed the connection unexpectedly', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('no connection to the server', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('connection timed out', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('could not connect to server', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('cannot connect to server', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('connection already closed', msg, re.M):
            raise exceptions.DbConnectionError(e)
        elif re.findall('cursor already closed', msg, re.M):
            raise exceptions.DbConnectionError(e)
        # SQLite3 errors
        elif 'no such table:' in msg:
            raise exceptions.DbTableMissingError(e)
        print("Unhandled/Unknown Error in connection.ProcessError")
        print('EXC_TYPE = {}'.format(type(e)))
        print('EXC_MSG = {}'.format(str(e).strip()))
        print('ERROR_CODE = {}'.format(error_code))
        print('ERROR_MSG = {}'.format(error_mesg))
        if sql_stmt:
            print("\n")
            print("sql_stmt [velocity.db.engine]: {}".format(sql_stmt))
            print("\n")
        if sql_params:
            print(sql_params)
            print("\n")
        traceback.print_exc()
        raise
