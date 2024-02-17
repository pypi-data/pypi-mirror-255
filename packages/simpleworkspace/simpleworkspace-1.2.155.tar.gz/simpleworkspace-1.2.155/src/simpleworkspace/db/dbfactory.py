class DBFactory:
    @classmethod
    def SQLite3_Memory(cls):
        import sqlite3
        return sqlite3.connect(':memory:')
    
    @classmethod
    def SQLite3_File(cls, databasePath:str):
        '''creates a new sqlite3 file db, or reuses if already existing at specified path'''
        import sqlite3
        return sqlite3.connect(databasePath)
    
    @classmethod
    def MSSQL_LocalDB(cls, database:str="tempdb", instanceName='MSSQLLocalDB'):
        '''when database is not specified an temporary one will be created, and deleted at end of python script'''
        return cls.MSSQL(server=f"(localdb)\\{instanceName}", database=database, UseWindowsAuthentication=True)
    
    @classmethod
    def MSSQL(cls, server:str, database:str=None, driver=None, UseWindowsAuthentication=False):
        '''
        :driver: when set to None, it automatically finds a suitable driver(if there is any)
        Example:
            server='SQLExpress',
            database='master',
        '''
        import pyodbc
        from simpleworkspace.utility.linq import LINQ

        if(driver is None):
            msSqlDrivers = LINQ(pyodbc.drivers()) \
                .Where(lambda driverName: driverName.endswith('SQL Server')) \
                .ToList()
            
            if not(msSqlDrivers):
                raise Exception("No suitable MS SQL Server drivers found for pyodbc")
            
            #preffered driver
            driver = LINQ(msSqlDrivers) \
                .Where(lambda driverName: driverName.startswith('ODBC Driver')) \
                .FirstOrDefault()

            if(driver is None):
                driver = msSqlDrivers[0] #then just pick whatever is available

            driver = '{' + driver + '}'

        connString = f"Driver={driver};Server={server};Database={database};"
        if(UseWindowsAuthentication):
            connString += "Trusted_Connection=yes;"

        return pyodbc.connect(connString)