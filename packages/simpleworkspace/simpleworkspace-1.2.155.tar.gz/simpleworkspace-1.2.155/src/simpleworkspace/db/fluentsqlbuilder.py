from typing import Callable, List, Optional, Generator
from simpleworkspace.utility.time import StopWatch
from enum import Enum

try:
    from mysql.connector.connection import MySQLConnectionAbstract as MySQLConnection 
    from mysql.connector.cursor import CursorBase as MySQLCursor
except ImportError:
    pass

try:
    from pyodbc import Connection as MsSqlConnection
    from pyodbc import Cursor as MsSqlCursor
except ImportError:
    pass

try:
    from sqlite3 import Connection as Sqlite3Connection
    from sqlite3 import Cursor as Sqlite3Cursor
except ImportError:
    pass


class _FluentSqlBuilderExecuteResults:
    '''Represents the result of an executed SQL query using FluentSqlBuilder'''
    def __init__(self, executed_statement: 'Sqlite3Cursor|MsSqlCursor|MySQLCursor', execution_time_ms):
        self._executed_statement = executed_statement
        self.execution_time_ms = execution_time_ms
        self._FetchMode_Dictionary = True

    def _OnGetRow(self, row: tuple):
        '''row is by default cursors expected to be numeric index mode'''

        if not (self._FetchMode_Dictionary):
            return row
        
        row_dict = {}
        for i, value in enumerate(row):
            columnName = self._executed_statement.description[i][0]
            row_dict[columnName] = value
        return row_dict
    
    def FirstOrDefault(self) -> dict|tuple|None:
        '''Returns the first row or None if no result'''
        for row in self.Iterator():
            return row
        return None

    def ToArray(self) -> List[dict]|List[tuple]:
        '''Loads all resulting rows into memory and returns them as a list'''
        return list(self.Iterator())

    def Iterator(self) -> Generator[int, dict|tuple, None]:
        '''
        Loads one row at a time in a memory-efficient manner, useful for large result sets.
        
        Example:
        >>> for row in self.iterator():
        ...
        '''
        while True:
            row = self._executed_statement.fetchone()
            if row is None:
                break
            yield self._OnGetRow(row)

    def AffectedRowCount(self) -> int:
        '''Returns the number of rows affected by the query (for DELETE, INSERT, UPDATE queries)'''
        return self._executed_statement.rowcount

    def SetFetchMode_Dictionary(self):
        self._FetchMode_Dictionary = True
        return self
    
    def SetFetchMode_NumericIndex(self):
        '''
        Uses column indexes instead of column names when gathering results
        Example:
          result['columnName'] changes to result[0]...
        '''
        self._FetchMode_Dictionary = False
        return self

    def __del__(self):
        '''when garbage collecting the result, closes the cursor'''
        self._executed_statement.close()


class DBTypeEnum(Enum):
    MYSQL = 1
    MSSQLSRV = 2
    SQLITE = 3

    @classmethod
    def GetFromConnection(cls, connection):
        #if a module is missing, then we definitely do not have that type of connection
        try:
            if(isinstance(connection, MySQLConnection)):
                return cls.MYSQL
        except Exception:
            pass
        
        try:
            if(isinstance(connection, MsSqlConnection)):
                return cls.MSSQLSRV
        except Exception:
            pass
        
        return cls.SQLITE #wether or not it is, use sqlite as default type


class FluentSqlBuilderError(Exception):
    def __init__(self, operation: str, message: str):
        if operation:
            message = f"{operation}: {message}"
        super().__init__(message)

class FluentSqlBuilder:
    '''FluentSqlBuilder provides a fluent interface for building and executing SQL queries'''
    def __init__(self, connection: 'MySQLConnection|MsSqlConnection|Sqlite3Connection' = None):
        self._segments = []
        self._params = []

        #the indexes are dictionaries and has format key=nestingLevel, value=array of segment indexes
        #this is used for cases when later methods overrides earlier segments
        self._nestingLevel = 0
        self._indexer_Select = _SegmentIndexer(self)
        self._indexer_Insert = _SegmentIndexer(self)
        self._indexer_Update = _SegmentIndexer(self)
        self._indexer_Delete = _SegmentIndexer(self)
        self._indexer_Where = _SegmentIndexer(self)

        if(connection is None):
            self._connection = None
            self._connection_type = DBTypeEnum.SQLITE #default syntax type
        else:
            self._connection = connection
            self._connection_type = DBTypeEnum.GetFromConnection(connection)


    def CreateTable(self, tableName: str, ignoreIfExists = False):
        """
        Creates a new table in the database.

        :param tableName: Name of the table.
        :param ignore_if_exists: Ignore error if the table already exists.
        
        Example:
        >>> FluentSqlBuilder(connection) 
        >>>     .CreateTable('users') 
        >>>     .Column('id', 'INT PRIMARY KEY') 
        >>>     .Column('name', 'VARCHAR(100)') 
        >>>     .Column('age', 'INT') 
        >>>     .Execute()
        ...
        """

        if not tableName:
            raise FluentSqlBuilderError("create_table", "No table name specified")

        if(self._connection_type == DBTypeEnum.MSSQLSRV):
            ignoreIfExists = False #mssql doesnt support this
        
        if(ignoreIfExists):
            self.Append(f"CREATE TABLE IF NOT EXISTS {tableName}")
        else:
            self.Append(f"CREATE TABLE {tableName}")
        return self

    def Column(self, columnName: str, attributes: str, foreignKeyReference: Optional[str] = None):
        '''
        Adds a column to the table.

        :param columnName: Name of the column.
        :param attributes: Any column attributes, e.g., "INT PRIMARY KEY".
        :param foreign_key_reference: Make the column a foreign key by specifying a reference like 'OtherTable(columnName)'.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .CreateTable('users')
        >>>     .Column('id', 'INT PRIMARY KEY')
        >>>     .Column('name', 'VARCHAR(100)')
        >>>     .Column('age', 'INT')
        >>>     .Execute()
        ...
        '''
        
        if not columnName or not attributes:
            raise FluentSqlBuilderError("column", "Empty column name or attributes")

        last_segment = self._GetLastSegment()
        if not isinstance(last_segment, _ChainableClause_Column):
            last_segment = _ChainableClause_Column()
            self._segments.append(last_segment)

        last_segment.Add(f"{columnName} {attributes}")
        if foreignKeyReference:
            last_segment.Add(f"FOREIGN KEY ({columnName}) REFERENCES {foreignKeyReference}")
        return self

    def Select(self, *columnNames: str):
        sql = "SELECT"
        if(columnNames):
            sql += ' ' + ', '.join(columnNames)
        self.Append(sql)
        self._indexer_Select.AddCurrentSegment()
        return self

    def From(self, table: str=None):
        sql = f"FROM"
        if(table):
            sql += ' ' + table
        self.Append(sql)
        return self

    def Insert(self, tableName: str, *keyValuePairs: dict):
        '''
        Adds an INSERT INTO clause to the query for inserting data into a table.

        :param table: The name of the table where data will be inserted.
        :param keyValuePairs: An dict of column names and their corresponding values.

        Example insert - single:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .Execute()
        ...

        Example insert - multiple:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users',
        >>>         {'name': 'John Doe', 'age': 30},
        >>>         {'name': 'Bob Lasso', 'age': 45}
        >>>     )
        >>>     .Execute()
        ...
        '''

        if not tableName or not keyValuePairs:
            raise FluentSqlBuilderError("insert", "Empty or invalid table/keyValuePairs")

        columnNames = list(keyValuePairs[0].keys())
        value_placeholder_template = "(" + self.GeneratePreparedPlaceholders(len(columnNames)) + ")"
        value_placeholders = []

        for row_mapping in keyValuePairs:
            self._params.extend(list(row_mapping.values()))
            value_placeholders.append(value_placeholder_template)

        columnNames = ', '.join(columnNames)
        value_placeholders = ', '.join(value_placeholders)

        self.Append(f"INSERT INTO {tableName} ({columnNames}) VALUES {value_placeholders}")
        self._indexer_Insert.AddCurrentSegment()
        return self

    def OnDuplicateKeyUpdate(self):
        '''
        Is used after an insert statement. When the insert fails due to a duplicate key,
        allows updating specific columns with new values.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .OnDuplicateKeyUpdate()
        >>>     .Set("age = VALUES(age)")
        >>>     .Set("name = ?", "newName")
        >>>     .Execute()
        ...
        '''

        if self._indexer_Insert.IsEmpty():
            raise FluentSqlBuilderError("OnDuplicateKeyUpdate", "Used in conjunction with insert statements only")

        self.Append("ON DUPLICATE KEY UPDATE")
        return self

    def OnDuplicateKeyIgnore(self):
        '''
        Is used after an insert statement. When the insert fails due to a duplicate key, errors are ignored
        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Insert('users', {'name': 'John Doe', 'age': 30})
        >>>     .OnDuplicateKeyIgnore()
        >>>     .Execute()
        ...
        '''

        if self._indexer_Insert.IsEmpty():
            raise FluentSqlBuilderError("OnDuplicateKeyIgnore", "Used in conjunction with insert statements only")

        replacement = "INSERT IGNORE"
        if(self._connection_type == DBTypeEnum.SQLITE):
            replacement = "INSERT OR IGNORE"

        self._indexer_Insert.ModifyLast(lambda segment: replacement + segment[6:])
        return self
    
    def Update(self, tableName: str):
        '''
        Adds an UPDATE clause to the query for updating values in a table.
        Requires a where condition before execute.

        :param table: The name of the table where the update operation will take place.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Update('users')
        >>>     .Set('name = ?', new_name)
        >>>     .Set('age = age + 1')
        >>>     .Where('id = ?', user_id)
        >>>     .Execute()
        ...
        '''
        if not tableName:
            raise FluentSqlBuilderError("update", "Empty table")

        self.Append(f"UPDATE {tableName} SET")
        self._indexer_Update.AddCurrentSegment()
        return self

    def Set(self, sql: str, *params):
        '''
        A chainable clause that simply makes comma-separated assignments, mainly used
        in conjunction with statements/clauses where you need to assign variables such as UPDATE or ONDUPLICATEKEYUPDATE.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Update('users')
        >>>     .Set('name = ?', new_name)
        >>>     .Set('age = age + 1')
        >>>     .Where('id = ?', user_id)
        >>>     .Execute()
        ...
        '''
        if not sql:
            raise FluentSqlBuilderError("set", "Empty assignment")

        last_segment = self._GetLastSegment()
        if not isinstance(last_segment, _ChainableClause_Set):
            last_segment = _ChainableClause_Set()
            self._segments.append(last_segment)

        last_segment.Add(sql)
        self._params.extend(params)
        return self

    def Delete(self):
        '''
        Adds a DELETE clause to the query for deleting rows in a table.
        Requires a where condition.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Delete()
        >>>     .From('users')
        >>>     .Where('name = ?', 'John Doe')
        >>>     .Execute()
        ...
        '''

        self.Append("DELETE")
        self._indexer_Delete.AddCurrentSegment()
        return self

    def Join(self, table: str=None, onCondition: str=None, alias:str=None):
        '''
        Adds a join clause to the query.

        Example style 1:
        >>> FluentSqlBuilder()
        >>>     .Select(*)
        >>>     .From('users')
        >>>     .Join('user_roles', onCondition='users.roleId = user_roles.id')
        >>>     .Execute()
        ...

        Example style 2:
        >>> FluentSqlBuilder()
        >>>     .Select(*)
        >>>     .From('users')
        >>>     .Join()
        >>>         .BeginParenthesis()
        >>>             .Select('*')
        >>>             .From('user_roles')
        >>>         .EndParenthesis()
        >>>         .As('user_roles')
        >>>         .On('users.role_id = user_roles.id')
        >>>     .Execute()
        '''
        
        sql = "JOIN"
        if(table is not None):
            sql += f" {table}"
            if(alias):
                sql += f' AS {alias}'
        if(onCondition is not None):
            sql += f' ON {onCondition}'
        self.Append(sql)
        return self
    
    def InnerJoin(self, table:str=None, onCondition:str=None, alias:str=None):
        self.Append("INNER")
        self.Join(table, onCondition, alias)
        return self

    def LeftJoin(self, table:str=None, onCondition:str=None, alias:str=None):
        self.Append("LEFT")
        self.Join(table, onCondition, alias)
        return self

    def RightJoin(self, table:str=None, onCondition:str=None, alias:str=None):
        self.Append("RIGHT")
        self.Join(table, onCondition, alias)
        return self
    
    def FullJoin(self, table:str=None, onCondition:str=None, alias:str=None):
        self.Append("FULL")
        self.Join(table, onCondition, alias)
        return self

    def CrossJoin(self, table:str, alias:str=None):
        sql = f"CROSS JOIN {table}"
        if(alias):
            sql += f' AS {alias}'

        self.Append(sql)
        return self

    def Where(self, condition: str, *params):
        '''
        Adds the starting WHERE clause and is a start point to create conditions.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Select('*')
        >>>     .From('users')
        >>>     .Where('name = ?', 'John Doe')
        >>>     .Execute()
        ...
        '''
        if not condition:
            raise FluentSqlBuilderError("where", "Empty condition")

        self.Append(f"WHERE {condition}", *params)
        self._indexer_Where.AddCurrentSegment()
        return self

    def WhereIn(self, columnName: str, params:tuple=None):
        '''
        Adds the starting WHERE IN clause and is a start point to create conditions.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Select('*')
        >>>     .From('users')
        >>>     .WhereIn('name', ['John Doe', 'Bob Dylan'])
        >>>     .Execute()
        ...
        '''
        self.GenericInClause("WHERE", columnName, params)
        self._indexer_Where.AddCurrentSegment()
        return self

    def WhereNotIn(self, columnName: str, params:tuple=None):
        self.GenericNotInClause("WHERE", columnName, params)
        self._indexer_Where.AddCurrentSegment()
        return self

    def And(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("And", "Empty condition")

        self.Append(f"AND {condition}", *params)
        return self

    def AndNot(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("AndNot", "Empty condition")

        self.Append(f"AND NOT {condition}", *params)
        return self

    def AndIn(self, columnName: str, params:tuple=None):
        self.GenericInClause("AND", columnName, params)
        return self

    def AndNotIn(self, columnName: str, params:tuple=None):
        self.GenericNotInClause("AND", columnName, params)
        return self

    def Or(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("Or", "Empty condition")

        self.Append(f"OR {condition}", *params)
        return self

    def OrNot(self, condition: str, *params):
        if not condition:
            raise FluentSqlBuilderError("OrNot", "Empty condition")

        self.Append(f"OR NOT {condition}", *params)
        return self

    def OrIn(self, columnName: str, params:tuple=None):
        self.GenericInClause("OR", columnName, params)
        return self

    def OrNotIn(self, columnName: str, params:tuple=None):
        self.GenericNotInClause("OR", columnName, params)
        return self

    def Append(self, sql: str, *params):
        '''
        This method allows you to freely add a parameterized/prepared SQL query.

        :param sql: The custom SQL to be added to the query.
        :param params: The parameters to be bound to the condition placeholders.

        Example:
        >>> FluentSqlBuilder(connection)
        >>>     .Append('SELECT *')
        >>>     .Append('FROM users')
        >>>     .Append('WHERE age > ?', 18)
        >>>     .Execute()
        ...
        '''
        if not sql:
            raise FluentSqlBuilderError("append", "Empty SQL")

        self._segments.append(sql)
        if params:
            self._params.extend(params)
        return self

    def OrderByAscending(self, columnName: str):
        '''
        Adds ORDER BY clause with ascending direction. This clause is chainable by following
        with more OrderBy* methods.
        '''
        return self._OrderBy(columnName, "ASC")

    def OrderByDescending(self, columnName: str):
        '''
        Adds ORDER BY clause with descending direction. This clause is chainable by following
        with more OrderBy* methods.
        '''
        return self._OrderBy(columnName, "DESC")

    def _OrderBy(self, columnName: str, direction: str):
        if not columnName or not direction:
            raise FluentSqlBuilderError("ORDERBY", "Empty column name or direction")

        last_segment = self._GetLastSegment()
        if not isinstance(last_segment, _ChainableClause_OrderBy):
            last_segment = _ChainableClause_OrderBy()
            self._segments.append(last_segment)

        last_segment.Add(columnName, direction)
        return self
    
    def GroupBy(self, *columnName: str):
        self.Append("GROUP BY " + ', '.join(columnName))
        return self

    def Limit(self, maxRowCount: int, offset:int=None):
        if self._indexer_Select.IsEmpty():
            raise FluentSqlBuilderError('LIMIT', 'Used in conjunction with SELECT statements only')
       
        if(self._connection_type == DBTypeEnum.MSSQLSRV): #only mssqlsrv needs to alter a previous segment
            if(offset is None):
                replacement = f"SELECT TOP {maxRowCount}"
                self._indexer_Select.ModifyLast(lambda segment: replacement + segment[6:])
            else:
                if not isinstance(self._GetLastSegment(), _ChainableClause_OrderBy):
                    raise FluentSqlBuilderError('LIMIT', 'MSSQLSERVER requires "ORDER BY" clause before using offset')
                self.Append(f"OFFSET {offset} ROWS FETCH NEXT {maxRowCount} ONLY")
            return self

        #the rest just appends at end
        sql = f"LIMIT {maxRowCount}"
        if(offset is not None):
            if(self._connection_type == DBTypeEnum.MYSQL):
                sql += f", {offset}"
            else:
                sql += f" OFFSET {offset}" #sqlite syntax as default
        self.Append(sql)
        return self
    
    def BeginParenthesis(self):
        self._nestingLevel += 1
        self.Append('(')
        return self
    
    def EndParenthesis(self):
        self._nestingLevel -= 1
        self.Append(')')
        return self
    
    def As(self, alias:str=None):
        '''Adds 'AS <alias>' to query'''
        sql = 'AS'
        if(alias):
            sql += f' {alias}'
        self.Append(sql)
        return self

    def On(self, onCondition:str, *params):
        '''Adds 'ON <condition>' to query'''
        if not (onCondition):
            raise FluentSqlBuilderError('On', 'empty ON condition')
        self.Append(f'ON {onCondition}', *params)
        return self
    
    def With(self, tableName:str, query:str=None, *params):
        """
        Adds a Common Table Expression (CTE) to the query,
        or in simple terms, a temporary table for the running query

        :param tableName: Name of the CTE.
        :param query: SQL query for the CTE.
        :param params: paramiterized params

        Example 1:
        >>> FluentSqlBuilder(connection)
        >>>     .With('CTEName', 'SELECT column1 FROM table1 WHERE condition')
        >>>     .Select('*')
        >>>     .From('CTEName')
        >>>     .Execute()
        ...
        Example 2
        >>> FluentSqlBuilder(connection)
        >>>     .With('cte_name').As().BeginParenthesis()
        >>>         .Select('column1')
        >>>         .From('table1')
        >>>         .Where('condition')
        >>>     .EndParenthesis()
        >>>     .Select('*')
        >>>     .From('CTEName')
        >>>     .Execute()
        """

        if not tableName:
            raise FluentSqlBuilderError("With", "Empty CTE name")

        sql = f'WITH {tableName}'
        if(query):
            sql += f' AS ({query})'
        self.Append(sql, *params)
        return self

    def Execute(self):
        if(self._connection is None):
            raise FluentSqlBuilderError('Execute', 'FluentSqlBuilder initialized without a connection, this functionality will not be available')

        sw = StopWatch()
        sw.Start()
        self._ValidateBuiltQuery()

        if(self._connection_type == DBTypeEnum.MYSQL):
            #only for mysql cursor, having prepared param behaves more like the rest, sql injections are safe either either way,
            #but small changes for example are that datatypes such as blob columns are retrieved properly.
            cursor = self._connection.cursor(prepared=True) 
        else:
            cursor = self._connection.cursor()

        cursor.execute(str(self), self._params)

        if(self._indexer_Delete.HasAny() or self._indexer_Insert.HasAny() or self._indexer_Update.HasAny()):
            self._connection.commit() #persist changes to database when needed, for free hand queries the caller must do it afterwards

        sw.Stop()
        return _FluentSqlBuilderExecuteResults(cursor, sw.GetElapsedMilliseconds())

    def __str__(self):
        '''Returns the built SQL query string with placeholders (e.g., ?)'''
        return " ".join(str(segment) for segment in self._segments)

    def _ValidateBuiltQuery(self):
        if not self._segments:
            raise FluentSqlBuilderError("Execute", "No query")

        if self._indexer_Update.HasAny() or self._indexer_Delete.HasAny():
            if self._indexer_Where.IsEmpty():
                raise FluentSqlBuilderError("Execute", "Safety check error, Update/Delete queries must have a where condition, otherwise all rows in the table would be altered")

    def GenericInClause(self, prefix: str, columnName: str, params:tuple=None, operator="IN"):
        if not columnName:
            raise FluentSqlBuilderError("generic_in_clause", "No columnName specified")

        sql = f"{prefix} {columnName} {operator}"
        if not params:
            self.Append(sql)
            return self


        placeholders = self.GeneratePreparedPlaceholders(len(params))
        sql += f' ({placeholders})'
        self.Append(sql, *params)
        return self

    def GenericNotInClause(self, prefix: str, columnName: str, params:tuple=None):
        self.GenericInClause(prefix, columnName, params, operator='NOT IN')

    @staticmethod
    def GeneratePreparedPlaceholders(placeholder_count: int) -> str:
        if placeholder_count <= 0:
            return ""
        return ', '.join(['?'] * placeholder_count)

    def GetSegmentCount(self):
        return len(self._segments)

    def _GetLastSegment(self):
        '''Retrieves the last segment or None if no segments exist'''
        if not self._segments:
            return None
        return self._segments[-1]
    



class _SegmentIndexer:
    def __init__(self, builder: FluentSqlBuilder):
        self._builder = builder
        self.indexer = {} #type:dict[int, list[int]]

    def IsEmpty(self, checkAllLevels = False):
        return not self.HasAny(checkAllLevels)
    
    def HasAny(self, checkAllLevels = False):
        '''
        checks if current indexer has any segment on current nesting level
        when checkAllLevels is true, checks all segments for this type of segment 
        '''
        if(checkAllLevels):
            return len(self.indexer) > 0
        return self._builder._nestingLevel in self.indexer
    
    def AddCurrentSegment(self):
        '''adds latest added segment index from the builder'''
        nestingLevel = self._builder._nestingLevel
        currentSegmentIndex = len(self._builder._segments) - 1
        if(nestingLevel not in self.indexer):
            self.indexer[nestingLevel] = []
        self.indexer[nestingLevel].append(currentSegmentIndex)

    def ModifyLast(self, filter: Callable[[str], str]):
        '''modifies last segment in current nesting level'''

        nestingLevel = self._builder._nestingLevel
        segments = self._builder._segments

        lastIndex = self.indexer[nestingLevel][-1]
        lastSegmentData = segments[lastIndex]
        if not(isinstance(lastSegmentData, str)):
            raise TypeError('Last segment in the indexer was not of type str, cannot be modified')
        segments[lastIndex] = filter(lastSegmentData)

class _ChainableClause_Column:
    def __init__(self):
        self._segments = []

    def Add(self, sql: str):
        self._segments.append(sql)

    def __str__(self):
        return '(' + ', '.join(self._segments) + ')'


class _ChainableClause_Set:
    def __init__(self):
        self._segments = []

    def Add(self, sql: str):
        self._segments.append(sql)

    def __str__(self):
        return ', '.join(self._segments)


class _ChainableClause_OrderBy:
    def __init__(self):
        self._segments = []

    def Add(self, columnName: str, direction: str):
        self._segments.append(f"{columnName} {direction}")

    def __str__(self):
        return "ORDER BY " + ', '.join(self._segments)



