from velocity.db import exceptions
from velocity.db.core.decorators import return_default

class Column(object):
    """
    Represents a column in a database table.
    """
    def __init__(self, table, name):
        """
        Initializes a column object with the specified table and name.

        Args:
            table (table): The table object that the column belongs to.
            name (str): The name of the column.
        
        Raises:
            Exception: If the table parameter is not of type 'table'.
        """
        if isinstance(table,str):
            raise Exception("column table parameter must be a `table` class.")
        self.tx = table.tx
        self.sql = table.tx.engine.sql
        self.name = name
        self.table = table

    def __str__(self):
        """
        Returns a string representation of the column object.

        Returns:
            str: A string representation of the column object.
        """
        return """
    Table: %s
    Column: %s
    Column Exists: %s
    Py Type: %s
    SQL Type: %s
    NULL OK: %s
    Foreign Key: %s
        """ % (
        self.table.name,
        self.name,
        self.exists(),
        self.py_type,
        self.sql_type,
        self.is_nullok,
        self.foreign_key_to
        )

    @property
    def info(self):
        """
        Retrieves information about the column from the database.

        Returns:
            dict: A dictionary containing information about the column.
        
        Raises:
            DbColumnMissingError: If the column does not exist in the database.
        """
        sql, vals = self.sql.column_info(self.table.name, self.name)
        result = self.tx.execute(sql, vals).one()
        if not result:
            raise exceptions.DbColumnMissingError
        return result

    @property
    def foreign_key_info(self):
        """
        Retrieves information about the foreign key constraint on the column.

        Returns:
            dict: A dictionary containing information about the foreign key constraint.
        
        Raises:
            DbColumnMissingError: If the column does not exist in the database.
        """
        sql, vals = self.sql.foreign_key_info(table=self.table.name, column=self.name)
        result = self.tx.execute(sql, vals).one()
        if not result:
            raise exceptions.DbColumnMissingError
        return result

    @property
    def foreign_key_to(self):
        """
        Retrieves the name of the referenced table and column for the foreign key constraint.

        Returns:
            str: The name of the referenced table and column in the format 'referenced_table_name.referenced_column_name'.
        
        Raises:
            DbColumnMissingError: If the column does not exist in the database.
        """
        try:
            return "{referenced_table_name}.{referenced_column_name}".format(**self.foreign_key_info)
        except exceptions.DbColumnMissingError:
            return None

    @property
    def foreign_key_table(self):
        """
        Retrieves the name of the referenced table for the foreign key constraint.

        Returns:
            str: The name of the referenced table.
        
        Raises:
            DbColumnMissingError: If the column does not exist in the database.
        """
        try:
            return self.foreign_key_info['referenced_table_name']
        except exceptions.DbColumnMissingError:
            return None

    def exists(self):
        """
        Checks if the column exists in the table.

        Returns:
            bool: True if the column exists, False otherwise.
        """
        return self.name in self.table.columns

    @property
    def py_type(self):
        """
        Retrieves the Python data type of the column.

        Returns:
            type: The Python data type of the column.
        """
        return self.sql.py_type(self.sql_type)

    @property
    def sql_type(self):
        """
        Retrieves the SQL data type of the column.

        Returns:
            str: The SQL data type of the column.
        """
        return self.info[self.sql.type_column_identifier]

    @property
    def is_nullable(self):
        """
        Checks if the column is nullable.

        Returns:
            bool: True if the column is nullable, False otherwise.
        """
        return self.info[self.sql.is_nullable]

    is_nullok = is_nullable

    def rename(self, name):
        """
        Renames the column.

        Args:
            name (str): The new name for the column.
        """
        sql, vals = self.sql.rename_column(self.table.name, self.name, name)
        self.tx.execute(sql, vals)
        self.name = name

    @return_default([])
    def distinct(self, order='asc', qty=None):
        """
        Retrieves distinct values from the column.

        Args:
            order (str, optional): The order in which the values should be sorted. Defaults to 'asc'.
            qty (int, optional): The maximum number of distinct values to retrieve. Defaults to None.

        Returns:
            list: A list of distinct values from the column.
        """
        sql, vals = self.sql.select(columns="distinct {}".format(self.name), table=self.table.name, orderby="{} {}".format(self.name,order), qty=qty)
        return self.tx.execute(sql, vals).as_simple_list().all()

    def max(self, where=None):
        """
        Retrieves the maximum value from the column.

        Args:
            where (str, optional): The WHERE clause to filter the rows. Defaults to None.

        Returns:
            int: The maximum value from the column.
        
        Raises:
            DbTableMissingError: If the table does not exist in the database.
            DbColumnMissingError: If the column does not exist in the database.
        """
        try:
            sql, vals = self.sql.select(columns="max({})".format(self.name), table=self.table.name, where=where)
            return self.tx.execute(sql, vals).scalar()
        except (exceptions.DbTableMissingError,exceptions.DbColumnMissingError):
            return 0
