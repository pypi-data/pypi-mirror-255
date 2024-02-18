import os
import re
import hashlib
import decimal
import datetime
from velocity.db.servers.sql import Query
from velocity.db import exceptions


def initialize(config = {
        'database': os.environ['DBDatabase'],
        'host': os.environ['DBHost'],
        'port': os.environ['DBPort'],
        'user': os.environ['DBUser'],
        'password': os.environ['DBPassword'],
    }, database=None, host=None, port=None, user=None, password=None):
    import psycopg2
    from velocity.db.core.engine import Engine
    
    if database:
        config['database'] = database
    if host:
        config['host'] = host
    if port:
        config['port'] = port
    if user:
        config['user'] = user
    if password:
        config['password'] = password
    return Engine(psycopg2, config, SQL)

def make_where(where, sql, vals, is_join=False):
    if not where:
        return
    sql.append('WHERE')
    if isinstance(where, str):
        sql.append(where)
        return
    if isinstance(where, dict):
        where = list(where.items())
    if not isinstance(where, list):
        raise Exception("Parameter `where` is not a valid datatype.")
    alias = 'A'
    if is_join and isinstance(is_join, str):
        alias = is_join
    connect = ''
    for key, val in where:
        if connect: sql.append(connect)
        if is_join:
            if '.' not in key:
                key = alias + '.' + quote(key.lower())
        if val == None:
            if '!' in key:
                key = key.replace('!', '')
                sql.append('{} is not NULL'.format(key))
            else:
                sql.append('{} is NULL'.format(key))
        elif isinstance(val, (list, tuple)) and '><' not in key:
            if '!' in key:
                key = key.replace('!', '')
                sql.append('{} not in %s'.format(key))
                vals.append(tuple(val))
            else:
                sql.append('{} in %s'.format(key))
                vals.append(tuple(val))
        elif isinstance(val, Query):
            sql.append('{} in ({})'.format(key, val))
        else:
            case = None
            if '<>' in key:
                key = key.replace('<>', '')
                op = '<>'
            elif '!=' in key:
                key = key.replace('!=', '')
                op = '<>'
            elif '!><' in key:
                key = key.replace('!><', '')
                op = 'not between'
            elif '><' in key:
                key = key.replace('><', '')
                op = 'between'
            elif '!%' in key:
                key = key.replace('!%', '')
                op = 'not like'
            elif '%%' in key:
                key = key.replace('%%', '')
                op = '%'
            elif '%>' in key:
                key = key.replace('%>', '')
                op = '%>'
            elif '<%' in key:
                key = key.replace('<%', '')
                op = '<%'
            elif '==' in key:
                key = key.replace('==', '')
                op = '='
            elif '<=' in key:
                key = key.replace('<=', '')
                op = '<='
            elif '>=' in key:
                key = key.replace('>=', '')
                op = '>='
            elif '<' in key:
                key = key.replace('<', '')
                op = '<'
            elif '>' in key:
                key = key.replace('>', '')
                op = '>'
            elif '%' in key:
                key = key.replace('%', '')
                op = 'like'
                case = 'lower'
            elif '!' in key:
                key = key.replace('!', '')
                op = '<>'
            elif '=' in key:
                key = key.replace('=', '')
                op = '='
            else:
                op = '='
            if '#' in key:
                key = key.replace('#', '')
                op = '='
                case = 'lower'
            if isinstance(val, str) and val[:2] == '@@' and val[2:]:
                sql.append('{} {} {}'.format(key, op, val[2:]))
            elif op in ['between', 'not between']:
                sql.append('{} {} %s and %s'.format(key, op))
                vals.extend(val)
            else:
                if case:
                    sql.append('{2}({0}) {1} {2}(%s)'.format(key, op, case))
                else:
                    sql.append('{0} {1} %s'.format(key, op))
                vals.append(val)
        connect = 'AND'


def quote(data):
    if isinstance(data, list):
        new = []
        for item in data:
            new.append(quote(item))
        return new
    else:
        parts = data.split('.')
        new = []
        for part in parts:
            if '"' in part:
                new.append(part)
            elif part.upper() in reserved_words:
                new.append('"' + part + '"')
            elif re.findall('[/]', part):
                new.append('"' + part + '"')
            else:
                new.append(part)
        return '.'.join(new)


class SQL(object):
    server = "PostGreSQL"
    type_column_identifier = 'data_type'
    is_nullable = 'is_nullable'

    default_schema = 'public'

    ApplicationErrorCodes = ['22P02', '42883']

    DatabaseMissingErrorCodes = []
    TableMissingErrorCodes = ['42P01']
    ColumnMissingErrorCodes = ['42703']
    ForeignKeyMissingErrorCodes = ['42704']

    ConnectionErrorCodes = ['08001', '08S01']
    DuplicateKeyErrorCodes = []  # Handled in regex check.
    RetryTransactionCodes = []
    TruncationErrorCodes = []
    LockTimeoutErrorCodes = ['55P03']
    DatabaseObjectExistsErrorCodes = ['42710', '42P07', '42P04']
    DataIntegrityErrorCodes = ['23503']

    @classmethod
    def version(cls):
        return "select version()", tuple()

    @classmethod
    def timestamp(cls):
        return "select current_timestamp", tuple()

    @classmethod
    def user(cls):
        return "select current_user", tuple()

    @classmethod
    def databases(cls):
        return "select datname from pg_database where datistemplate = false", tuple(
        )

    @classmethod
    def schemas(cls):
        return 'select schema_name from information_schema.schemata', tuple()

    @classmethod
    def current_schema(cls):
        return 'select current_schema', tuple()

    @classmethod
    def current_database(cls):
        return 'select current_database()', tuple()

    @classmethod
    def tables(cls, system=False):
        if system:
            return "select table_schema,table_name from information_schema.tables where table_type = 'BASE TABLE' order by table_schema,table_name", tuple(
            )
        else:
            return "select table_schema, table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema NOT IN ('pg_catalog', 'information_schema')", tuple(
            )

    @classmethod
    def views(cls, system=False):
        if system:
            return 'select table_schema, table_name from information_schema.views order by table_schema,table_name', tuple(
            )
        else:
            return 'select table_schema, table_name from information_schema.views where table_schema = any (current_schemas(false)) order by table_schema,table_name', tuple(
            )

    @classmethod
    def __has_pointer(cls, columns):
        if columns:
            if isinstance(columns, list):
                columns = ','.join(columns)
            if '>' in columns:
                return True
        return False

    @classmethod
    def select(cls,
               columns=None,
               table=None,
               where=None,
               orderby=None,
               groupby=None,
               having=None,
               start=None,
               qty=None,
               tbl=None):
        if not table:
            raise Exception("Table name required")
        is_join = False

        if isinstance(columns,str)\
        and 'distinct' in columns.lower():
            sql = [
                'SELECT',
                columns,
                'FROM',
                quote(table),
            ]
        elif cls.__has_pointer(columns):
            is_join = True
            if isinstance(columns, str):
                columns = columns.split(',')
            letter = 65
            tables = {table: chr(letter)}
            letter += 1
            __select = []
            __from = ['{} AS {}'.format(quote(table), tables.get(table))]
            __left_join = []

            for column in columns:
                if '>' in column:
                    parts = column.split('>')
                    foreign = tbl.foreign_key_info(parts[0])
                    if not foreign:
                        raise exceptions.DbApplicationError("Foreign key not defined")
                    ref_table = foreign['referenced_table_name']
                    ref_schema = foreign['referenced_table_schema']
                    ref_column = foreign['referenced_column_name']
                    lookup = "{}:{}".format(ref_table, parts[0])
                    if lookup in tables:
                        __select.append('{}."{}" as "{}"'.format(
                            tables.get(lookup), parts[1], '_'.join(parts)))
                    else:
                        tables[lookup] = chr(letter)
                        letter += 1
                        __select.append('{}."{}" as "{}"'.format(
                            tables.get(lookup), parts[1], '_'.join(parts)))
                        __left_join.append(
                            'LEFT OUTER JOIN "{}"."{}" AS {}'.format(
                                ref_schema, ref_table, tables.get(lookup)))
                        __left_join.append('ON {}."{}" = {}."{}"'.format(
                            tables.get(table), parts[0], tables.get(lookup),
                            ref_column))
                    if orderby and column in orderby:
                        orderby = orderby.replace(
                            column, "{}.{}".format(tables.get(lookup),
                                                   parts[1]))

                else:
                    if '(' in column:
                        __select.append(column)
                    else:
                        __select.append("{}.{}".format(tables.get(table),
                                                       column))
            sql = ['SELECT']
            sql.append(','.join(__select))
            sql.append('FROM')
            sql.extend(__from)
            sql.extend(__left_join)
        else:
            if columns:
                if isinstance(columns, str):
                    columns = columns.split(',')
                if isinstance(columns, list):
                    columns = quote(columns)
                    columns = ','.join(columns)
            else:
                columns = '*'
            sql = [
                'SELECT',
                columns,
                'FROM',
                quote(table),
            ]
        vals = []
        make_where(where, sql, vals, is_join)
        if groupby:
            sql.append('GROUP BY')
            if isinstance(groupby, (list, tuple)):
                groupby = ','.join(groupby)
            sql.append(groupby)
        if having:
            sql.append('HAVING')
            if isinstance(having, (list, tuple)):
                having = ','.join(having)
            sql.append(having)
        if orderby:
            sql.append('ORDER BY')
            if isinstance(orderby, (list, tuple)):
                orderby = ','.join(orderby)
            sql.append(orderby)
        if start and qty:
            sql.append('OFFSET {} ROWS FETCH NEXT {} ROWS ONLY'.format(
                start, qty))
        elif start:
            sql.append('OFFSET {} ROWS'.format(start))
        elif qty:
            sql.append('FETCH NEXT {} ROWS ONLY'.format(qty))
        sql = ' '.join(sql)
        return sql, tuple(vals)

    @classmethod
    def create_database(cls, name):
        return 'create database ' + name, tuple()

    @classmethod
    def last_id(cls, table):
        return "SELECT CURRVAL(PG_GET_SERIAL_SEQUENCE(%s, 'sys_id'))", tuple(
            [table])

    @classmethod
    def set_id(cls, table, start):
        return "SELECT SETVAL(PG_GET_SERIAL_SEQUENCE(%s, 'sys_id'), %s)", tuple(
            [table, start])

    @classmethod
    def drop_database(cls, name):
        return 'drop database if exists ' + name, tuple()

    @classmethod
    def create_table(cls, name, columns={}, drop=False):
        if '.' in name:
            fqtn = name
        else:
            fqtn = 'public.' + name
        schema, table = fqtn.split('.')
        name = fqtn.replace('.', '_')
        trigger = ''.format(name)
        sql = []
        if drop:
            sql.append(cls.drop_table(fqtn))
        sql.append("""
            CREATE TABLE {0} (
              sys_id SERIAL PRIMARY KEY,
              sys_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
              sys_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('{0}', 'sys_id'),1000,TRUE);

            CREATE OR REPLACE FUNCTION {1}.update_sys_modified()
              RETURNS TRIGGER AS
            $BODY$
                        BEGIN
                        -- update sys_modified on each update.
                        NEW.sys_modified := now();
                        -- Do not allow sys_created to be modified.
                        NEW.sys_created := OLD.sys_created;
                        RETURN NEW;
                        END;
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;
            --ALTER FUNCTION {1}.update_sys_modified()
            --OWNER TO postgres;

            CREATE TRIGGER on_update_row_{3}
            BEFORE UPDATE ON {0}
            FOR EACH ROW EXECUTE PROCEDURE {1}.update_sys_modified();

        """.format(fqtn, schema, table, fqtn.replace('.', '_')))

        for key, val in columns.items():
            key = re.sub('<>!=%', '', key.lower())
            if key in ['sys_id', 'sys_created', 'sys_modified']:
                continue
            sql.append("ALTER TABLE {} ADD COLUMN {} {};".format(
                quote(fqtn), quote(key), cls.get_type(val)))
        return '\n\t'.join(sql), tuple()

    @classmethod
    def drop_table(cls, name):
        return "drop table if exists %s cascade;" % quote(name), tuple()

    @classmethod
    def drop_column(cls, table, name, cascade=True):
        if cascade:
            return "ALTER TABLE %s DROP COLUMN %s CASCADE" % (
                quote(table), quote(name)), tuple()
        else:
            return "ALTER TABLE %s DROP COLUMN %s " % (quote(table),
                                                       quote(name)), tuple()

    @classmethod
    def columns(cls, name):
        if '.' in name:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_schema) = UPPER(%s)
            and UPPER(table_name) = UPPER(%s)
            """, tuple(name.split('.'))
        else:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_name) = UPPER(%s)
            """, tuple([
                name,
            ])

    @classmethod
    def column_info(cls, table, name):
        params = table.split('.')
        params.append(name)
        if '.' in table:
            return """
            select *
            from information_schema.columns
            where UPPER(table_schema ) = UPPER(%s)
            and UPPER(table_name) = UPPER(%s)
            and UPPER(column_name) = UPPER(%s)
            """, tuple(params)
        else:
            return """
            select *
            from information_schema.columns
            where UPPER(table_name) = UPPER(%s)
            and UPPER(column_name) = UPPER(%s)
            """, tuple(params)

    @classmethod
    def primary_keys(cls, table):
        params = table.split('.')
        params.reverse()
        if '.' in table:
            return """
            SELECT
              pg_attribute.attname
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            WHERE
              pg_class.oid = %s::regclass AND
              indrelid = pg_class.oid AND
              nspname = %s AND
              pg_class.relnamespace = pg_namespace.oid AND
              pg_attribute.attrelid = pg_class.oid AND
              pg_attribute.attnum = any(pg_index.indkey)
             AND indisprimary
            """, tuple(params)
        else:
            return """
            SELECT
              pg_attribute.attname
            FROM pg_index, pg_class, pg_attribute, pg_namespace
            WHERE
              pg_class.oid = %s::regclass AND
              indrelid = pg_class.oid AND
              pg_class.relnamespace = pg_namespace.oid AND
              pg_attribute.attrelid = pg_class.oid AND
              pg_attribute.attnum = any(pg_index.indkey)
             AND indisprimary
            """, tuple(params)

    @classmethod
    def foreign_key_info(cls, table=None, column=None, schema=None):
        if '.' in table:
            schema, table = table.split('.')

        sql = [
            """
        SELECT
             KCU1.CONSTRAINT_NAME AS "FK_CONSTRAINT_NAME"
           , KCU1.CONSTRAINT_SCHEMA AS "FK_CONSTRAINT_SCHEMA"
           , KCU1.CONSTRAINT_CATALOG AS "FK_CONSTRAINT_CATALOG"
           , KCU1.TABLE_NAME AS "FK_TABLE_NAME"
           , KCU1.COLUMN_NAME AS "FK_COLUMN_NAME"
           , KCU1.ORDINAL_POSITION AS "FK_ORDINAL_POSITION"
           , KCU2.CONSTRAINT_NAME AS "UQ_CONSTRAINT_NAME"
           , KCU2.CONSTRAINT_SCHEMA AS "UQ_CONSTRAINT_SCHEMA"
           , KCU2.CONSTRAINT_CATALOG AS "UQ_CONSTRAINT_CATALOG"
           , KCU2.TABLE_NAME AS "UQ_TABLE_NAME"
           , KCU2.COLUMN_NAME AS "UQ_COLUMN_NAME"
           , KCU2.ORDINAL_POSITION AS "UQ_ORDINAL_POSITION"
           , KCU1.CONSTRAINT_NAME AS "CONSTRAINT_NAME"
           , KCU2.CONSTRAINT_SCHEMA AS "REFERENCED_TABLE_SCHEMA"
           , KCU2.TABLE_NAME AS "REFERENCED_TABLE_NAME"
           , KCU2.COLUMN_NAME AS "REFERENCED_COLUMN_NAME"
        FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS RC
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU1
        ON KCU1.CONSTRAINT_CATALOG = RC.CONSTRAINT_CATALOG
           AND KCU1.CONSTRAINT_SCHEMA = RC.CONSTRAINT_SCHEMA
           AND KCU1.CONSTRAINT_NAME = RC.CONSTRAINT_NAME
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU2
        ON KCU2.CONSTRAINT_CATALOG = RC.UNIQUE_CONSTRAINT_CATALOG
           AND KCU2.CONSTRAINT_SCHEMA = RC.UNIQUE_CONSTRAINT_SCHEMA
           AND KCU2.CONSTRAINT_NAME = RC.UNIQUE_CONSTRAINT_NAME
           AND KCU2.ORDINAL_POSITION = KCU1.ORDINAL_POSITION
        """
        ]
        vals = []
        where = {}
        if schema:
            where['LOWER(KCU1.CONSTRAINT_SCHEMA)'] = schema.lower()
        if table:
            where['LOWER(KCU1.TABLE_NAME)'] = table.lower()
        if column:
            where['LOWER(KCU1.COLUMN_NAME)'] = column.lower()
        make_where(where, sql, vals)
        return ' '.join(sql), tuple(vals)

    @classmethod
    def create_foreign_key(cls,
                           table,
                           columns,
                           key_to_table,
                           key_to_columns,
                           name=None,
                           schema=None):
        if '.' not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(key_to_columns, str):
            key_to_columns = [key_to_columns]
        if isinstance(columns, str):
            columns = [columns]
        if not name:
            m = hashlib.md5()
            m.update(table.encode('utf-8'))
            m.update(' '.join(columns).encode('utf-8'))
            m.update(key_to_table.encode('utf-8'))
            m.update(' '.join(key_to_columns).encode('utf-8'))
            name = 'FK_' + m.hexdigest()
        sql = "ALTER TABLE {} ADD CONSTRAINT {} FOREIGN KEY ({}) REFERENCES {} ({});".format(
            table, name, ','.join(columns), key_to_table,
            ','.join(key_to_columns))

        return sql, tuple()

    @classmethod
    def drop_foreign_key(cls,
                         table,
                         columns,
                         key_to_table=None,
                         key_to_columns=None,
                         name=None,
                         schema=None):
        if '.' not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(key_to_columns, str):
            key_to_columns = [key_to_columns]
        if isinstance(columns, str):
            columns = [columns]
        if not name:
            m = hashlib.md5()
            m.update(table.encode('utf-8'))
            m.update(' '.join(columns).encode('utf-8'))
            m.update(key_to_table.encode('utf-8'))
            m.update(' '.join(key_to_columns).encode('utf-8'))
            name = 'FK_' + m.hexdigest()
        sql = "ALTER TABLE {} DROP CONSTRAINT {};".format(table, name)
        return sql, tuple()

    @classmethod
    def create_index(cls,
                     table=None,
                     columns=None,
                     unique=False,
                     direction=None,
                     where=None,
                     name=None,
                     schema=None,
                     trigram=None,
                     tbl=None):
        """
        The following statements must be executed on the database instance once to enable respective trigram features.
        CREATE EXTENSION pg_trgm; is required to use  gin.
        CREATE EXTENSION btree_gist; is required to use gist
        """
        if '.' not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(columns, (list, set)):
            columns = ','.join([quote(c.lower()) for c in columns])
        else:
            columns = quote(columns)
        sql = ['CREATE']
        if unique:
            sql.append('UNIQUE')
        sql.append('INDEX')
        tablename = quote(table)
        if not name:
            name = re.sub(
                r'\([^)]*\)', '',
                columns.replace(' ', '').replace(',', '_').replace('"', ''))
        if trigram:
            sql.append('IDX__TRGM_{}_{}__{}'.format(table.replace('.', '_'),
                                                    trigram.upper(), name))
        else:
            sql.append('IDX__{}__{}'.format(table.replace('.', '_'), name))

        sql.append('ON')
        sql.append(quote(tablename))

        if trigram:
            sql.append('USING')
            sql.append(trigram)
        sql.append('(')
        if tbl:
            join = ''
            for column_name in columns.split(','):
                if join:
                    sql.append(join)
                column = tbl.column(column_name)
                if column.py_type == str:
                    sql.append("lower({})".format(quote(column_name)))
                else:
                    sql.append(quote(column_name))
                join = ','
        else:
            sql.append(columns)
        if trigram:
            sql.append('{}_trgm_ops'.format(trigram.lower()))
        sql.append(')')
        vals = []
        make_where(where, sql, vals)
        return ' '.join(sql), tuple(vals)

    @classmethod
    def drop_index(cls,
                   table=None,
                   columns=None,
                   name=None,
                   schema=None,
                   trigram=None):
        if '.' not in table and schema:
            table = "{}.{}".format(schema, table)
        if isinstance(columns, (list, set)):
            columns = ','.join([quote(c.lower()) for c in columns])
        else:
            columns = quote(columns)
        sql = ['DROP']
        sql.append('INDEX IF EXISTS')
        tablename = quote(table)
        if not name:
            name = re.sub(
                r'\([^)]*\)', '',
                columns.replace(' ', '').replace(',', '_').replace('"', ''))
        if trigram:
            sql.append('IDX__TRGM_{}_{}__{}'.format(table.replace('.', '_'),
                                                    trigram.upper(), name))
        else:
            sql.append('IDX__{}__{}'.format(table.replace('.', '_'), name))
        return ' '.join(sql), tuple()

    @classmethod
    def insert(cls, table, data):
        keys = []
        vals = []
        args = []
        for key, val in data.items():
            keys.append(quote(key.lower()))
            if isinstance(val,str) \
            and len(val) > 2 \
            and val[:2] == '@@' and val[2:]:
                vals.append(val[2:])
            else:
                vals.append('%s')
                args.append(val)

        sql = ['INSERT INTO']
        sql.append(quote(table))
        sql.append('(')
        sql.append(','.join(keys))
        sql.append(')')
        sql.append('VALUES')
        sql.append('(')
        sql.append(','.join(vals))
        sql.append(')')
        sql = ' '.join(sql)
        return sql, tuple(args)

    @classmethod
    def update(cls,
               table,
               data,
               pk,
               left_join=None,
               inner_join=None,
               outer_join=None):
        alias = 'A'
        if ' ' in table:
            alias, table = table.split(' ')
        is_join = bool(left_join or inner_join or outer_join)
        sql = ['UPDATE']

        sql.append(quote(table))
        sql.append('SET')
        vals = []
        connect = ''
        for key, val in data.items():
            if connect:
                sql.append(connect)
            if isinstance(val, str) and val[:2] == '@@' and val[2:]:
                sql.append("{} = {}".format(key, val[2:]))
            else:
                sql.append('{} = %s'.format(key))
                vals.append(val)
            connect = ','
        if is_join:
            sql.append('FROM')
            sql.append(table)
            sql.append('AS')
            sql.append(alias)
        if left_join:
            for k, v in left_join.items():
                sql.append('LEFT JOIN')
                sql.append(k)
                sql.append('ON')
                sql.append(v)
        if outer_join:
            for k, v in outer_join.items():
                sql.append('OUTER JOIN')
                sql.append(k)
                sql.append('ON')
                sql.append(v)
        if inner_join:
            for k, v in inner_join.items():
                sql.append('INNER JOIN')
                sql.append(k)
                sql.append('ON')
                sql.append(v)
        make_where(pk, sql, vals, is_join)
        return ' '.join(sql), tuple(vals)

    @classmethod
    def get_type(cls, v):
        if isinstance(v, str):
            if v[:2] == '@@':
                return v[2:] or cls.TYPES.TEXT
        elif isinstance(v, str) \
        or v is str:
            return cls.TYPES.TEXT
        elif isinstance(v, bool) \
        or v is bool:
            return cls.TYPES.BOOLEAN
        elif isinstance(v, int) \
        or v is int:
            return cls.TYPES.BIGINT
        elif isinstance(v, int) \
        or v is int:
            if v is int:
                return cls.TYPES.INTEGER
            if v > 2147483647 or v < -2147483648:
                return cls.TYPES.BIGINT
            else:
                return cls.TYPES.INTEGER
        elif isinstance(v, float) \
        or v is float:
            return cls.TYPES.NUMERIC + '(19, 6)'
        elif isinstance(v, decimal.Decimal) \
        or v is decimal.Decimal:
            return cls.TYPES.NUMERIC + '(19, 6)'
        elif isinstance (v, datetime.datetime) \
        or v is datetime.datetime:
            return cls.TYPES.DATETIME
        elif isinstance (v, datetime.date) \
        or v is datetime.date:
            return cls.TYPES.DATE
        elif isinstance(v, datetime.time) \
        or v is datetime.time:
            return cls.TYPES.TIME
        elif isinstance(v, datetime.timedelta) \
        or v is datetime.timedelta:
            return cls.TYPES.INTERVAL
        elif isinstance (v, bytes) \
        or v is bytes:
            return cls.TYPES.BINARY
        # Everything else defaults to TEXT, incl. None
        return cls.TYPES.TEXT

    @classmethod
    def get_conv(cls, v):
        if isinstance(v, str):
            if v[:2] == '@@':
                return v[2:] or cls.TYPES.TEXT
        elif isinstance(v, str) \
        or v is str:
            return cls.TYPES.TEXT
        elif isinstance(v, bool) \
        or v is bool:
            return cls.TYPES.BOOLEAN
        elif isinstance(v, int) \
        or v is int:
            return cls.TYPES.BIGINT
        elif isinstance(v, int) \
        or v is int:
            if v is int:
                return cls.TYPES.INTEGER
            if v > 2147483647 or v < -2147483648:
                return cls.TYPES.BIGINT
            else:
                return cls.TYPES.INTEGER
        elif isinstance(v, float) \
        or v is float:
            return cls.TYPES.NUMERIC
        elif isinstance(v, decimal.Decimal) \
        or v is decimal.Decimal:
            return cls.TYPES.NUMERIC
        elif isinstance (v, datetime.datetime) \
        or v is datetime.datetime:
            return cls.TYPES.DATETIME
        elif isinstance (v, datetime.date) \
        or v is datetime.date:
            return cls.TYPES.DATE
        elif isinstance(v, datetime.time) \
        or v is datetime.time:
            return cls.TYPES.TIME
        elif isinstance(v, datetime.timedelta) \
        or v is datetime.timedelta:
            return cls.TYPES.INTERVAL
        elif isinstance (v, bytes) \
        or v is bytes:
            return cls.TYPES.BINARY
        # Everything else defaults to TEXT, incl. None
        return cls.TYPES.TEXT

    @classmethod
    def py_type(cls, v):
        v = str(v).upper()
        if v == cls.TYPES.INTEGER:
            return int
        elif v == cls.TYPES.SMALLINT:
            return int
        elif v == cls.TYPES.BIGINT:
            return int
        elif v == cls.TYPES.NUMERIC:
            return decimal.Decimal
        elif v == cls.TYPES.TEXT:
            return str
        elif v == cls.TYPES.BOOLEAN:
            return bool
        elif v == cls.TYPES.DATE:
            return datetime.date
        elif v == cls.TYPES.TIME:
            return datetime.time
        elif v == cls.TYPES.DATETIME:
            return datetime.datetime
        elif v == cls.TYPES.INTERVAL:
            return datetime.timedelta
        else:
            raise Exception("unmapped type %s" % v)

    @classmethod
    def massage_data(cls, data):
        """

        :param :
        :param :
        :param :
        :returns:
        """
        data = {key.lower(): val for key, val in data.items()}
        primaryKey = set(cls.GetPrimaryKeyColumnNames())
        if not primaryKey:
            if not cls.Exists():
                raise exceptions.DbTableMissingError
        dataKeys = set(data.keys()).intersection(primaryKey)
        dataColumns = set(data.keys()).difference(primaryKey)
        pk = {}
        pk.update([(k, data[k]) for k in dataKeys])
        d = {}
        d.update([(k, data[k]) for k in dataColumns])
        return d, pk

    @classmethod
    def alter_add(cls, table, columns, null_allowed=True):
        sql = []
        null = 'NOT NULL' if not null_allowed else ''
        if isinstance(columns, dict):
            for key, val in columns.items():
                key = re.sub('<>!=%', '', key.lower())
                sql.append("ALTER TABLE {} ADD {} {} {};".format(
                    quote(table), quote(key), cls.get_type(val), null))
        return '\n\t'.join(sql), tuple()

    @classmethod
    def alter_drop(cls, table, columns):
        sql = ["ALTER TABLE {} DROP COLUMN".format(quote(table))]
        if isinstance(columns, dict):
            for key, val in columns.items():
                key = re.sub('<>!=%', '', key.lower())
                sql.append("{},".format(key))
        if sql[-1][-1] == ',':
            sql[-1] = sql[-1][:-1]
        return '\n\t'.join(sql), tuple()

    @classmethod
    def alter_column_by_type(cls, table, column, value, nullable=True):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(quote(table))]
        sql.append("{} TYPE {}".format(quote(column), cls.get_type(value)))
        sql.append("USING {}::{}".format(quote(column), cls.get_conv(value)))
        if not nullable:
            sql.append('NOT NULL')
        return '\n\t'.join(sql), tuple()

    @classmethod
    def alter_column_by_sql(cls, table, column, value):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(quote(table))]
        sql.append("{} {}".format(quote(column), value))
        return ' '.join(sql), tuple()

    @classmethod
    def rename_column(cls, table, orig, new):
        return "ALTER TABLE {} RENAME COLUMN {} TO {};".format(
            quote(table), quote(orig), quote(new)), tuple()

    @classmethod
    def rename_table(cls, table, new):
        return "ALTER TABLE {} RENAME TO {};".format(quote(table),
                                                     quote(new)), tuple()

    @classmethod
    def create_savepoint(cls, sp):
        return 'SAVEPOINT "{}"'.format(sp), tuple()

    @classmethod
    def release_savepoint(cls, sp):
        return 'RELEASE SAVEPOINT "{}"'.format(sp), tuple()

    @classmethod
    def rollback_savepoint(cls, sp):
        return 'ROLLBACK TO SAVEPOINT "{}"'.format(sp), tuple()

    @classmethod
    def find_duplicates(cls, table, columns, key):
        if isinstance(columns, str):
            columns = [columns]
        return """
        SELECT {2}
        FROM (SELECT {2},
              ROW_NUMBER() OVER (partition BY {1} ORDER BY {2}) AS rnum
            FROM {0}) t
        WHERE t.rnum > 1;
        """.format(table, ','.join(quote(columns)), key), tuple()

    @classmethod
    def delete_duplicates(cls, table, columns, key):
        if isinstance(columns, str):
            columns = [columns]
        return """
        DELETE FROM {0}
        WHERE {2} IN (SELECT {2}
              FROM (SELECT {2},
                         ROW_NUMBER() OVER (partition BY {1} ORDER BY {2}) AS rnum
                     FROM {0}) t
              WHERE t.rnum > 1);
        """.format(table, ','.join(quote(columns)), key), tuple()

    @classmethod
    def delete(cls, table, where):
        sql = ['DELETE FROM {}'.format(table)]
        vals = []
        make_where(where, sql, vals)
        return ' '.join(sql), tuple(vals)

    @classmethod
    def truncate(cls, table):
        return "truncate table {}".format(quote(table)), tuple()

    @classmethod
    def create_view(cls, name, query, temp=False, silent=True):
        sql = ['CREATE']
        if silent:
            sql.append('OR REPLACE')
        if temp:
            sql.append('TEMPORARY')
        sql.append('VIEW')
        sql.append(name)
        sql.append('AS')
        sql.append(query)
        return ' '.join(sql), tuple()

    @classmethod
    def drop_view(cls, name, silent=True):
        sql = ['DROP VIEW']
        if silent:
            sql.append('IF EXISTS')
        sql.append(name)
        return ' '.join(sql), tuple()

    @classmethod
    def alter_trigger(cls, table, state='ENABLE', name='USER'):
        return 'ALTER TABLE {} {} TRIGGER {}'.format(table, state,
                                                     name), tuple()

    @classmethod
    def set_sequence(cls, table, next_value):
        return "SELECT SETVAL(PG_GET_SERIAL_SEQUENCE('{0}', 'sys_id'),{1},FALSE)".format(
            table, next_value), tuple()

    @classmethod
    def missing(cls, table, list, column='SYS_ID', where=None):
        sql = [
            'SELECT * FROM',
            f"UNNEST('{{{','.join([str(x) for x in list])}}}'::int[]) id",
            'EXCEPT ALL',
            f"SELECT {column} FROM {table}",
        ]
        vals = []
        make_where(where, sql, vals)
        return ' '.join(sql), tuple(vals)

    class TYPES(object):
        TEXT = 'TEXT'
        INTEGER = 'INTEGER'
        NUMERIC = 'NUMERIC'
        DATETIME = 'TIMESTAMP WITHOUT TIME ZONE'
        TIMESTAMP = 'TIMESTAMP WITHOUT TIME ZONE'
        DATE = 'DATE'
        TIME = 'TIME WITHOUT TIME ZONE'
        BIGINT = 'BIGINT'
        SMALLINT = 'SMALLINT'
        BOOLEAN = 'BOOLEAN'
        BINARY = 'BYTEA'
        INTERVAL = 'INTERVAL'


reserved_words = [
    'ADMIN',
    'ALIAS',
    'ALL',
    'ALLOCATE',
    'ANALYSE',
    'ANALYZE',
    'AND',
    'ANY',
    'ARE',
    'ARRAY',
    'AS',
    'ASC',
    'AUTHORIZATION',
    'BETWEEN',
    'BINARY',
    'BLOB',
    'BOTH',
    'BREADTH',
    'CALL',
    'CASCADED',
    'CASE',
    'CAST',
    'CATALOG',
    'CHECK',
    'CLOB',
    'COLLATE',
    'COLLATION',
    'COLUMN',
    'COMPLETION',
    'CONNECT',
    'CONNECTION',
    'CONSTRAINT',
    'CONSTRUCTOR',
    'CONTINUE',
    'CORRESPONDING',
    'CREATE',
    'CROSS',
    'CUBE',
    'CURRENT',
    'CURRENT_DATE',
    'CURRENT_PATH',
    'CURRENT_ROLE',
    'CURRENT_TIME',
    'CURRENT_TIMESTAMP',
    'CURRENT_USER',
    'DATA',
    'DATE',
    'DEFAULT',
    'DEFERRABLE',
    'DEPTH',
    'DEREF',
    'DESC',
    'DESCRIBE',
    'DESCRIPTOR',
    'DESTROY',
    'DESTRUCTOR',
    'DETERMINISTIC',
    'DIAGNOSTICS',
    'DICTIONARY',
    'DISCONNECT',
    'DISTINCT',
    'DO',
    'DYNAMIC',
    'ELSE',
    'END',
    'END-EXEC',
    'EQUALS',
    'EVERY',
    'EXCEPT',
    'EXCEPTION',
    'EXEC',
    'FALSE',
    'FIRST',
    'FOR',
    'FOREIGN',
    'FOUND',
    'FREE',
    'FREEZE',
    'FROM',
    'FULL',
    'GENERAL',
    'GO',
    'GOTO',
    'GRANT',
    'GROUP',
    'GROUPING',
    'HAVING',
    'HOST',
    'IDENTITY',
    'IGNORE',
    'ILIKE',
    'IN',
    'INDICATOR',
    'INITIALIZE',
    'INITIALLY',
    'INNER',
    'INTERSECT',
    'INTO',
    'IS',
    'ISNULL',
    'ITERATE',
    'JOIN',
    'LARGE',
    'LAST',
    'LATERAL',
    'LEADING',
    'LEFT',
    'LESS',
    'LIKE',
    'LIMIT',
    'LOCALTIME',
    'LOCALTIMESTAMP',
    'LOCATOR',
    'MAP',
    'MODIFIES',
    'MODIFY',
    'MODULE',
    'NAME',
    'NATURAL',
    'NCLOB',
    'NEW',
    'NOT',
    'NOTNULL',
    'NULL',
    'OBJECT',
    'OFF',
    'OFFSET',
    'OLD',
    'ON',
    'ONLY',
    'OPEN',
    'OPERATION',
    'OR',
    'ORDER',
    'ORDINALITY',
    'OUTER',
    'OUTPUT',
    'OVERLAPS',
    'PAD',
    'PARAMETER',
    'PARAMETERS',
    'PLACING',
    'POSTFIX',
    'PREFIX',
    'PREORDER',
    'PRESERVE',
    'PRIMARY',
    'PUBLIC',
    'READS',
    'RECURSIVE',
    'REF',
    'REFERENCES',
    'REFERENCING',
    'RESULT',
    'RETURN',
    'RIGHT',
    'ROLE',
    'ROLLUP',
    'ROUTINE',
    'ROWS',
    'SAVEPOINT',
    'SCOPE',
    'SEARCH',
    'SECTION',
    'SELECT',
    'SESSION_USER',
    'SETS',
    'SIMILAR',
    'SIZE',
    'SOME',
    'SPACE',
    'SPECIFIC',
    'SPECIFICTYPE',
    'SQL',
    'SQLCODE',
    'SQLERROR',
    'SQLEXCEPTION',
    'SQLSTATE',
    'SQLWARNING',
    'STATE',
    'STATIC',
    'STRUCTURE',
    'SYSTEM_USER',
    'TABLE',
    'TERMINATE',
    'THAN',
    'THEN',
    'TIMESTAMP',
    'TIMEZONE_HOUR',
    'TIMEZONE_MINUTE',
    'TO',
    'TRAILING',
    'TRANSLATION',
    'TRUE',
    'UNDER',
    'UNION',
    'UNIQUE',
    'UNNEST',
    'USER',
    'USING',
    'VALUE',
    'VARIABLE',
    'VERBOSE',
    'WHEN',
    'WHENEVER',
    'WHERE',
]
