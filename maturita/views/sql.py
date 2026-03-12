import mysql.connector

def get_connected():
    return mysql.connector.connect(
        host="dbs.spskladno.cz",
        user="student10",
        password="spsnet",
        database="vyuka10"
    )

mydb = get_connected() 
mydb.autocommit = True # to znamená že data budou furt aktualizovaný
mycursor = mydb.cursor(dictionary=True) # dictionary=True dělá že v html se to furt může udávat jako např {{ album.albumfile }}

def get_data(table):
    sql = f"SELECT * FROM {table}"
    mycursor.execute(sql)
    return mycursor.fetchall()

def add_data(table, data):
    columns = ", ".join(data.keys()) # grabs all the inserted column names (id, name, etc)
    column_inserts = ", ".join(["%s"] * len(data)) # creates all the insertables (%s) needed for the data
    column_data = tuple(data.values()) # grabs all the inserted column data (123, John, etc)

    sql = f"INSERT INTO {table} ({columns}) VALUES ({column_inserts})"

    mycursor.execute(sql, column_data)
    mydb.commit()

def del_data(table, data, logic="AND"):
    log = f" {logic} " # this is here just so it's " AND " or " OR "
    requirements = [f"{dat} = %s" for dat in data.keys()] # creates the requirements with column names ("X = %s", "Y = %s")
    statement = log.join(requirements) # makes the statement ("X = %s AND Y = %s")
    column_data = tuple(data.values()) # grabs all the inserted column data (123, John, etc)

    sql = f"DELETE FROM {table} WHERE {statement}"

    mycursor.execute(sql, column_data)
    mydb.commit()