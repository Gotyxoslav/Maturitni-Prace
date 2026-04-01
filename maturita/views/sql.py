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

def update_data(table, data, id):
    set_data = ", ".join([f"{key} = %s" for key in data.keys()]) # grabs each column name (name, password, etc) and adds "= %s" and finally adds ","
    column_data = tuple(data.values()) + (id,) # grabs all the inserted column data (123, John, etc) and also adds the id

    sql = f"UPDATE {table} SET {set_data} WHERE id = %s"
    mycursor.execute(sql, column_data)
    mydb.commit()

def get_joined_data(table1, table2, key1, key2, condition_column=None, condition_value=None):
    sql = f"SELECT * FROM {table1} JOIN {table2} ON {table1}.{key1} = {table2}.{key2}" # connects two tables

    if condition_column and condition_value: # condition_column = looks for a specific column (name, id, ...); condition_value = looks for specific values ("john", 123, ...)
        sql += f" WHERE {condition_column} = %s"
        mycursor.execute(sql, (condition_value,))
    else:
        mycursor.execute(sql)
        
    return mycursor.fetchall()

def update_specific_data(table, data, id_column, id_value):
    set_data = ", ".join([f"{key} = %s" for key in data.keys()])
    column_data = tuple(data.values()) + (id_value,)
    
    sql = f"UPDATE {table} SET {set_data} WHERE {id_column} = %s"
    
    mycursor.execute(sql, column_data)
    mydb.commit()