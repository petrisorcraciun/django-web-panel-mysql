from django.shortcuts import render
import mysql.connector
import array as arr
import socket 

def connectionDB(databaseName):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database= databaseName
    )
    return mydb

def connection():
    mydb = mysql.connector.connect(
         host="localhost",
         user="root",
         passwd=""
    )
    return mydb

def listDBMethod():
    
    conn = connection()
    listDatabases = conn.cursor()
    listDatabases.execute("SHOW DATABASES")
    result = listDatabases.fetchall()
    return result

def index(request):
  
    listDB = listDBMethod()

    host_name = socket.gethostname() 
    host_ip = socket.gethostbyname(host_name) 

    conn = connection()

    listDatabases = conn.cursor()
    listDatabases.execute("SHOW DATABASES")
    result = listDatabases.fetchall()

    nrDatabases = listDatabases.rowcount

    return render(request, 'index.html',
    {
        'listDB': listDB,
        'nrDatabases': nrDatabases,
        'host_ip': host_ip,
        'host_name': host_name
    })


def listTablesMethod(dbSelected):
    
    conn = connectionDB(dbSelected)

    mycursor2 = conn.cursor()
    mycursor2.execute("SHOW TABLES")
    listTables = mycursor2.fetchall()
    return listTables

def db_structure(request):
    
    dbSelected = request.GET['db']

    listTables = listTablesMethod(dbSelected)

    listDB = listDBMethod()


    return render(request, 'db_structure.html',
    {
       'listDB':  listDB,
       'listTables': listTables,
       'dbSelected': dbSelected
       
    })


def db_browse(request):
    tabelName = request.GET['table']
    databaseName = request.GET['db']
    try:
        conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database= databaseName)

        
        cursor = conn.cursor()
        cursor.execute("select * from " + tabelName)
        records = cursor.fetchall()
        nrRecords = cursor.rowcount

        columnsTable = conn.cursor()
        columnsTable.execute("SHOW COLUMNS FROM " + tabelName)

        columns = columnsTable.fetchall()

        nrColumns = columnsTable.rowcount

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if (conn.is_connected()):
            conn.close()
            cursor.close()
            print("MySQL connection is closed")

    listDB = listDBMethod()

    columns2 = [col[0] for col in columnsTable.description]
    records2 = [dict(zip(columns2, row)) for row in records]

    return render(request, 'db_browse.html',
    {
       'listDB':  listDB,
       'columns': columns,
       'records': records,
       'tabelName': tabelName,
       'nrColumns': nrColumns,
       'm': range(nrRecords),
       'n': range(nrColumns),
       'databaseName': databaseName
    })

def db_create(request):
    databaseName = request.GET['db']

    statusDB = checkIfDatabaseExists(databaseName)
    message = ""
    errMessage = ""

    if(statusDB):
        errMessage = "Database exists."
    else:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd=""
        )
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE " + databaseName)
        message = "The new database has been successfully added."

    listDB = listDBMethod()
    listTables = []

    return render(request, 'db_structure.html',
    {
       'listDB':  listDB,
       'listTables': listTables,
       'dbSelected': databaseName,
       'message': message,
       'errMessage': errMessage
       
    })


def empty_table(request):
    databaseName = request.GET['db']
    tableName = request.GET['table']
    message = ""
    errMessage = ""

    try:
        conn = connectionDB(databaseName)

        mycursor = conn.cursor()
        mycursor.execute("TRUNCATE TABLE " + tableName)
        message = "All records in the table have been deleted."
    except:
        errMessage = "Cannot truncate a table referenced in a foreign key constraint."

    listTables = listTablesMethod(databaseName)
    listDB = listDBMethod()

    return render(request, 'db_structure.html',
    {
       'listDB':  listDB,
       'listTables': listTables,
       'dbSelected': databaseName,
       'message': message,
       'errMessage': errMessage
       
    })


def checkIfTablesExists(databaseName, tableName):
    
    conn = connectionDB(databaseName)
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE " + tableName)
    result = cursor.fetchone()
    if result:
        return True
    return False

def checkIfDatabaseExists(databaseName):
    conn = connection()

    cursor = conn.cursor()
    cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME like '" + databaseName +"'")
    result = cursor.fetchone()
    if result:
        return True
   
    return False



def structure(request):
    databaseName = request.GET['db']
    tabelName = request.GET['table']

    conn = connectionDB(databaseName)
    mycursor = conn.cursor()
    mycursor.execute("DESC " + tabelName)

    conn2 = connectionDB(databaseName)
    indexesM = conn2.cursor()
    indexesM.execute("SHOW INDEXES FROM " + tabelName)

    indexes = indexesM.fetchall()
    records = mycursor.fetchall()

    conn3 = connection()
    data = conn3.cursor()
    data.execute("SELECT DISTINCT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS ORDER BY DATA_TYPE ASC")

    dataType = data.fetchall()
    
    listDB = listDBMethod()
    listTables = listTablesMethod(databaseName)

    return render(request, 'structure.html',
    {
       'listDB':  listDB,
       'listTables': listTables,
       'databaseName': databaseName,
       'records': records,
       'tabelName': tabelName,
       'indexes': indexes,
       'dataType': dataType
       
    })


def drop_table(request):
    databaseName = request.GET['db']
    tableName = request.GET['table']
    message = ""
    errMessage = ""

    try:
        conn = connectionDB(databaseName)

        mycursor = conn.cursor()
        mycursor.execute("DROP TABLE " + tableName)
        message = "The table " + tableName + " was successfully deleted."
    except:
        errMessage = "Cannot DROP a table referenced in a foreign key constraint."

    listTables = listTablesMethod(databaseName)
    listDB = listDBMethod()

    return render(request, 'db_structure.html',
    {
       'listDB':  listDB,
       'listTables': listTables,
       'dbSelected': databaseName,
       'message': message,
       'errMessage': errMessage
       
    })