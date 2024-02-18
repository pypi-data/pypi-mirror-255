
import decimal
import datetime
import re
from velocity.db import exceptions

class Query(str):
    pass

class SQL(object):
    server = "Generic SQL"
    type_column_identifier = 'data_type'
    default_schema = 'schema'
    lquote = '"'
    rquote = '"'

    DatabaseMissingErrorCodes = []
    TableMissingErrorCodes = []
    ColumnMissingErrorCodes = []
    ForeignKeyMissingErrorCodes =[]

    ConnectionErrorCodes = []
    DuplicateKeyErrorCodes = []
    RetryTransactionCodes = []
    TruncationErrorCodes = []
    LockTimeoutErrorCodes = []
    DatabaseObjectExistsErrorCodes = []

    @classmethod
    def quote(self, data):
        if isinstance(data, list):
            new = []
            for item in data:
                new.append(self.quote(item))
            return new
        else:
            parts = data.split('.')
            new = []
            for part in parts:
                if self.lquote in part:
                    new.append(part)
                elif part.upper() in reserved_words:
                    new.append(self.lquote+part+self.rquote)
                elif re.findall('[/]',part):
                    new.append(self.lquote+part+self.rquote)
                else:
                    new.append(part)
            return '.'.join(new)

    @classmethod
    def version(cls):
        return "select @@version"

    @classmethod
    def timestamp(cls):
        return "select current_timestamp"

    @classmethod
    def user(cls):
        return "select current_user"

    @classmethod
    def databases(cls):
        return "select name from master.dbo.sysdatabases"

    @classmethod
    def schemas(cls):
        return 'select schema_name from information_schema.schemata'

    @classmethod
    def current_schema(cls):
        return 'select schema_name()'

    @classmethod
    def current_database(cls):
        return 'select db_name() as current_database'

    @classmethod
    def tables(cls, system=False):
        return """
        select table_schema, table_name
        from information_schema.tables
        where table_type = 'BASE TABLE'
        order by table_schema,table_name
        """

    @classmethod
    def views(cls, system=False):
        return """
        select table_schema, table_name
        from information_schema.views
        order by table_schema,table_name
        """

    @classmethod
    def __has_pointer(cls,columns):
        if columns:
            if isinstance(columns,list):
                columns = ','.join(columns)
            if '>' in columns:
                return True
        return False

    @classmethod
    def select(cls,columns=None,table=None,where=None,orderby=None,groupby=None,having=None,start=None,qty=None):
        if cls.__has_pointer(columns):
            if isinstance(columns,str):
                columns = columns.split(',')
            letter = 65
            tables = {table: chr(letter)}
            letter += 1
            __select = []
            __from = ['{} AS {}'.format(self.quote(table),tables.get(table))]
            __left_join = []

            for column in columns:
                if '>' in column:
                    parts = column.split('>')
                    foreign = self.GetForeignKeyInfo(parts[0])
                    ref_table = foreign[0]['referenced_table_name']
                    ref_schema = foreign[0]['referenced_table_schema']
                    ref_column = foreign[0]['referenced_column_name']
                    lookup = "{}:{}".format(ref_table,parts[0])
                    if lookup in tables:
                        __select.append('{}."{}" as "{}"'.format(tables.get(lookup),parts[1],'_'.join(parts)))
                    else:
                        tables[lookup] = chr(letter)
                        letter += 1
                        __select.append('{}."{}" as "{}"'.format(tables.get(lookup),parts[1],'_'.join(parts)))
                        __left_join.append('LEFT OUTER JOIN "{}"."{}" AS {}'.format(ref_schema,ref_table,tables.get(lookup)))
                        __left_join.append('ON {}."{}" = {}."{}"'.format(
                            tables.get(table),
                            parts[0],
                            tables.get(lookup),
                            ref_column
                        ))
                    if orderby and column in orderby:
                        orderby = orderby.replace(column,"{}.{}".format(tables.get(lookup),parts[1]))
                else:
                    if '(' in column:
                        __select.append(column)
                    else:
                        __select.append("{}.{}".format(tables.get(self.table),column))
            sql = ['SELECT']
            sql.append(','.join(__select))
            sql.append('FROM')
            sql.extend(__from)
            sql.extend(__left_join)
        else:
            if columns:
                if isinstance(columns,str):
                    columns = columns.split(',')
                if isinstance(columns,list):
                    columns = self.quote(columns)
                    columns = ','.join(columns)
            else:
                columns = '*'
            sql = [
                'SELECT',
                columns,
                'FROM',
                self.quote(table),
                ]
        values = []
        if where:
            sql.append('WHERE')
            if isinstance(where,dict):
                join = ''
                for key in sorted(where.keys()):
                    if join: sql.append(join)
                    if where[key] == None:
                        sql.append('{} is NULL'.format(self.quote(key.lower())))
                    else:
                        sql.append('{} = %s'.format(self.quote(key.lower())))
                        values.append(where[key])
                    join = 'AND'
            else:
                sql.append(where)
        if groupby:
            sql.append('GROUP BY')
            sql.append(groupby)
        if having:
            sql.append('HAVING')
            sql.append(having)
        if orderby:
            sql.append('ORDER BY')
            sql.append(orderby)
        if start and qty:
            sql.append('OFFSET {} ROWS FETCH NEXT {} ROWS ONLY'.format(start,qty))
        elif start:
            sql.append('OFFSET {} ROWS'.format(start))
        elif qty:
            sql.append('FETCH {} ROWS ONLY'.format(qty))
        sql = ' '.join(sql)
        values = cls.massage_values(values)
        return sql, values

    @classmethod
    def create_database(cls, name):
        return 'create database ' + name

    @classmethod
    def drop_database(cls, name):
        return 'drop database ' + name

    @classmethod
    def create_table(cls, name, columns={}, drop=False):
        if '.' in name:
            fqtn = name
        else:
            fqtn = cls.default_schema + name
        schema,table = fqtn.split('.')
        name = fqtn.replace('.','_')
        trigger = 'on_update_row_{0}'.format(name)
        sql = []
        sql.append('DECLARE @script1 nVarChar(MAX);')
        sql.append('DECLARE @script2 nVarChar(MAX);')
        if drop:
            sql.append(cls.drop_table(fqtn))
        sql.append("""
            SET @script1 = '
            CREATE TABLE {0} (
              sys_id int identity(1000,1) primary key,
              sys_modified datetime not null default(getdate()),
              sys_created datetime not null default(getdate())
            )'
        """.format(fqtn,  table, trigger))
        sql.append("""
            SET @script2 = '
            CREATE TRIGGER {2}
            ON {0}
            AFTER UPDATE
            AS
            BEGIN
                UPDATE t
                SET t.sys_modified = CURRENT_TIMESTAMP,
                    t.sys_created = d.sys_created
                FROM {0} AS t
                INNER JOIN deleted AS d on t.sys_id=i.sys_id
            END'
        """.format(fqtn,  table, trigger))
        sql.append('EXEC (@script1);')
        sql.append('EXEC (@script2);')
        for key,val in columns.items():
            sql.append("ALTER TABLE {} ADD COLUMN {} {};".format(fqtn,key,cls.get_type(val)))
        return '\n\t'.join(sql)

    @classmethod
    def drop_table(cls, name):
        return "IF OBJECT_ID('%s', 'U') IS NOT NULL DROP TABLE %s;" % (self.quote(name),self.quote(name))

    @classmethod
    def columns(cls, name):
        if '.' in name:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_schema ) = UPPER(%s)
            and UPPER(table_name) = UPPER(%s)
            """, tuple(name.split('.'))
        else:
            return """
            select column_name
            from information_schema.columns
            where UPPER(table_name) = UPPER(%s)
            """, tuple([name])

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
        if '.' in table:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND UPPER(table_schema ) = UPPER(%s) AND UPPER(table_name) = UPPER(%s)
            """, tuple(params)
        else:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND UPPER(table_name) = UPPER(%s)
            """, tuple(params)

    @classmethod
    def xforeign_keys(cls, table):
        params = table.split('.')
        if '.' in table:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND UPPER(table_schema ) = UPPER(%s) AND UPPER(table_name) = UPPER(%s)
            """, tuple(params)
        else:
            return """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
            AND UPPER(table_name) = UPPER(%s)
            """, tuple(params)

    @classmethod
    def insert(cls, table, data={}):
        keys = []
        vals = []
        args = []
        for key,val in data.items():
            keys.append(self.quote(key.lower()))
            if isinstance(val,str) \
            and len(val) > 2 \
            and val[:2] == '@@':
                vals.append(val[2:])
            else:
                vals.append('%s')
                args.append(val)

        sql = ['INSERT INTO']
        sql.append(self.quote(table))
        sql.append('(')
        sql.append(','.join(keys))
        sql.append(')')
        sql.append('VALUES')
        sql.append('(')
        sql.append(','.join(vals))
        sql.append(')')
        sql = ' '.join(sql)
        values = cls.massage_values(args)
        return sql,values

    @classmethod
    def get_type(cls, v):
        if isinstance(v, str):
            if v[:2] == '@@':
                return v[2:]
        elif isinstance(v, str) \
        or v is str:
            return  cls.TYPES.TEXT
        elif isinstance(v, bool) \
        or v is bool:
            return cls.TYPES.BOOLEAN
        elif isinstance(v, int) \
        or v is int:
            if v > 2147483647 or v < -2147483648:
                return cls.TYPES.BIGINT
            else:
                return  cls.TYPES.INTEGER
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
        elif v in cls.TYPES.TEXT:
            return str
        elif v == cls.TYPES.BOOLEAN:
            return bool
        elif v == cls.TYPES.DATE:
            return datetime.date
        elif v == cls.TYPES.TIME:
            return datetime.time
        elif v == cls.TYPES.DATETIME:
            return datetime.datetime
        else:
            raise Exception("unmapped type %s" % v)

    @classmethod
    def massage_data(cls,data):
        """

        :param :
        :param :
        :param :
        :returns:
        """
        data = {key.lower():val for key,val in data.items()}
        primaryKey = set(cls.GetPrimaryKeyColumnNames())
        if not primaryKey:
            if not cls.Exists():
                raise exceptions.DbTableMissingError
        dataKeys = set(data.keys()).intersection( primaryKey )
        dataColumns = set(data.keys()).difference( primaryKey )
        pk = {}
        pk.update([(k,data[k]) for k in dataKeys])
        d = {}
        d.update([(k,data[k]) for k in dataColumns])
        return d,pk

    @classmethod
    def massage_values(cls, values):
        return tuple(values)

    @classmethod
    def alter_add(cls, table, columns, null_allowed=True):
        sql = []
        null = 'NOT NULL' if not null_allowed else ''
        if isinstance(columns,dict):
            for key,val in columns.items():
                sql.append("ALTER TABLE {} ADD {} {} {};".format(self.quote(table), self.quote(key), cls.get_type(val), null))
        return '\n\t'.join(sql)

    @classmethod
    def alter_drop(cls, table, columns):
        sql = ["ALTER TABLE {} DROP COLUMN".format(self.quote(table))]
        if isinstance(columns,dict):
            for key,val in columns.items():
                sql.append("{},".format(key))
        if sql[-1][-1] == ',':
            sql[-1] = sql[-1][:-1]
        return '\n\t'.join(sql)

    @classmethod
    def alter_column_by_type(cls, table, column, value, null_allowed=True):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(self.quote(table))]
        sql.append("{} {}".format(self.quote(column), cls.get_type(value)))
        if not null_allowed:
            sql.append('NOT NULL')
        return '\n\t'.join(sql)

    @classmethod
    def alter_column_by_sql(cls, table, column, value):
        sql = ["ALTER TABLE {} ALTER COLUMN".format(self.quote(table))]
        sql.append("{} {}".format(self.quote(column), value))
        return ' '.join(sql)


    @classmethod
    def rename_column(cls, table, name, new):
        if '.' in table:
            schema, table = table.split('.')
        else:
            schema = cls.default_schema
        return "sp_rename '{}.{}.{}', '{}', 'COLUMN';".format(self.quote(schema), self.quote(table), self.quote(name), new)

    @classmethod
    def rename_table(cls, table, name, new):
        if '.' in table:
            schema, table = table.split('.')
        else:
            schema = cls.default_schema
        return "sp_rename '{}.{}', '{}';".format(self.quote(schema), self.quote(name), new)

    @classmethod
    def create_savepoint(cls, sp):
        return None #"SAVE TRANSACTION {}".format(sp)

    @classmethod
    def release_savepoint(cls, sp):
        return None

    @classmethod
    def rollback_savepoint(cls, sp):
        return None #"ROLLBACK TRANSACTION {}".format(sp)

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
        """.format(table, ','.join(self.quote(columns)), key), tuple()

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
        """.format(table, ','.join(self.quote(columns)), key), tuple()

    @classmethod
    def delete(cls, table, where):
        sql = ['DELETE FROM {}'.format(table)]
        sql.append('WHERE')
        values = []
        if isinstance(where,dict):
            join = ''
            for key in sorted(where.keys()):
                if join: sql.append(join)
                if where[key] == None:
                    sql.append('{} is NULL'.format(self.quote(key.lower())))
                else:
                    sql.append('{} = %s'.format(self.quote(key.lower())))
                    values.append(where[key])
                join = 'AND'
        else:
            sql.append(where)
        return ' '.join(sql), tuple(values)

    @classmethod
    def truncate(cls, table):
        return "truncate table {}".format(self.quote(table)), tuple()


    class TYPES(object):
        TEXT = 'VARCHAR(MAX)'
        INTEGER = 'INT'
        NUMERIC = 'NUMERIC'
        DATETIME = 'DATETIME'
        TIMESTAMP = 'DATETIME'
        DATE = 'DATE'
        TIME = 'TIME'
        BIGINT = 'BIGINT'
        BOOLEAN = 'BIT'
        BINARY = 'VARBINARY(MAX)'

reserved_words = ['ABSOLUTE', 'ACTION', 'ADA', 'ADD', 'ALL', 'ALLOCATE', 'ALTER', 'AND', 'ANY', 'ARE', 'AS', 'ASC', 'ASSERTION', 'AT', 'AUTHORIZATION', 'AVG', 'BACKUP', 'BEGIN', 'BETWEEN', 'BIT', 'BIT_LENGTH', 'BOTH', 'BREAK', 'BROWSE', 'BULK', 'BY', 'CASCADE', 'CASCADED', 'CASE', 'CAST', 'CATALOG', 'CHAR', 'CHARACTER', 'CHARACTER_LENGTH', 'CHAR_LENGTH', 'CHECK', 'CHECKPOINT', 'CLOSE', 'CLUSTERED', 'COALESCE', 'COLLATE', 'COLLATION', 'COLUMN', 'COMMIT', 'COMPUTE', 'CONNECT', 'CONNECTION', 'CONSTRAINT', 'CONSTRAINTS', 'CONTAINS', 'CONTAINSTABLE', 'CONTINUE', 'CONVERT', 'CORRESPONDING', 'COUNT', 'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURSOR', 'DATABASE', 'DATE', 'DAY', 'DBCC', 'DEALLOCATE', 'DEC', 'DECIMAL', 'DECLARE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DENY', 'DESC', 'DESCRIBE', 'DESCRIPTOR', 'DIAGNOSTICS', 'DISCONNECT', 'DISK', 'DISTINCT', 'DISTRIBUTED', 'DOMAIN', 'DOUBLE', 'DROP', 'DUMP', 'ELSE', 'END', 'END-EXEC', 'ERRLVL', 'ESCAPE', 'EXCEPT', 'EXCEPTION', 'EXEC', 'EXECUTE', 'EXISTS', 'EXIT', 'EXTERNAL', 'EXTRACT', 'FALSE', 'FETCH', 'FILE', 'FILLFACTOR', 'FIRST', 'FLOAT', 'FOR', 'FOREIGN', 'FORTRAN', 'FOUND', 'FREETEXT', 'FREETEXTTABLE', 'FROM', 'FULL', 'FUNCTION', 'GET', 'GLOBAL', 'GO', 'GOTO', 'GRANT', 'GROUP', 'HAVING', 'HOLDLOCK', 'HOUR', 'IDENTITY', 'IDENTITYCOL', 'IDENTITY_INSERT', 'IF', 'IMMEDIATE', 'IN', 'INCLUDE', 'INDEX', 'INDICATOR', 'INITIALLY', 'INNER', 'INPUT', 'INSENSITIVE', 'INSERT', 'INT', 'INTEGER', 'INTERSECT', 'INTERVAL', 'INTO', 'IS', 'ISOLATION', 'JOIN', 'KEY', 'KILL', 'LANGUAGE', 'LAST', 'LEADING', 'LEFT', 'LEVEL', 'LIKE', 'LINENO', 'LOAD', 'LOCAL', 'LOWER', 'MATCH', 'MAX', 'MERGE', 'MIN', 'MINUTE', 'MODULE', 'MONTH', 'NAMES', 'NATIONAL', 'NATURAL', 'NCHAR', 'NEXT', 'NO', 'NOCHECK', 'NONCLUSTERED', 'NONE', 'NOT', 'NULL', 'NULLIF', 'NUMERIC', 'OCTET_LENGTH', 'OF', 'OFF', 'OFFSETS', 'ON', 'ONLY', 'OPEN', 'OPENDATASOURCE', 'OPENQUERY', 'OPENROWSET', 'OPENXML', 'OPTION', 'OR', 'ORDER', 'OUTER', 'OUTPUT', 'OVER', 'OVERLAPS', 'PAD', 'PARTIAL', 'PASCAL', 'PERCENT', 'PIVOT', 'PLAN', 'POSITION', 'PRECISION', 'PREPARE', 'PRESERVE', 'PRIMARY', 'PRINT', 'PRIOR', 'PRIVILEGES', 'PROC', 'PROCEDURE', 'PUBLIC', 'RAISERROR', 'READ', 'READTEXT', 'REAL', 'RECONFIGURE', 'REFERENCES', 'RELATIVE', 'REPLICATION', 'RESTORE', 'RESTRICT', 'RETURN', 'REVERT', 'REVOKE', 'RIGHT', 'ROLLBACK', 'ROWCOUNT', 'ROWGUIDCOL', 'ROWS', 'RULE', 'SAVE', 'SCHEMA', 'SCROLL', 'SECOND', 'SECTION', 'SECURITYAUDIT', 'SELECT', 'SEMANTICKEYPHRASETABLE', 'SEMANTICSIMILARITYDETAILSTABLE', 'SEMANTICSIMILARITYTABLE', 'SESSION', 'SESSION_USER', 'SET', 'SETUSER', 'SHUTDOWN', 'SIZE', 'SMALLINT', 'SOME', 'SPACE', 'SQL', 'SQLCA', 'SQLCODE', 'SQLERROR', 'SQLSTATE', 'SQLWARNING', 'STATISTICS', 'SUBSTRING', 'SUM', 'SYSTEM_USER', 'TABLE', 'TABLESAMPLE', 'TEMPORARY', 'TEXTSIZE', 'THEN', 'TIME', 'TIMESTAMP', 'TIMEZONE_HOUR', 'TIMEZONE_MINUTE', 'TO', 'TOP', 'TRAILING', 'TRAN', 'TRANSACTION', 'TRANSLATE', 'TRANSLATION', 'TRIGGER', 'TRIM', 'TRUE', 'TRUNCATE', 'TRY_CONVERT', 'TSEQUAL', 'UNION', 'UNIQUE', 'UNKNOWN', 'UNPIVOT', 'UPDATE', 'UPDATETEXT', 'UPPER', 'USAGE', 'USE', 'USER', 'USING', 'VALUE', 'VALUES', 'VARCHAR', 'VARYING', 'VIEW', 'WAITFOR', 'WHEN', 'WHENEVER', 'WHERE', 'WHILE', 'WITH', 'WITHIN GROUP', 'WORK', 'WRITE', 'WRITETEXT', 'YEAR', 'ZONE',]
