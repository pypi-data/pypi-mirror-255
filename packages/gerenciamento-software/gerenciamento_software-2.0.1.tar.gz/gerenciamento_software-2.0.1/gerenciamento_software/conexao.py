import mysql.connector

host_name = ""
user_name = ""
password_name = ""
database_name = ""
conexao = ""
cursor = ""



def sql_conectar_db(host:str,user:str,password:str,database:str):
    global host_name
    global user_name
    global password_name
    global database_name
    global cursor
    global conexao

    host_name = host
    user_name = user
    password_name = password
    database_name = database

    conexao = mysql.connector.connect(
    host= host_name,    
    user= user_name,
    password= password_name,
    database= database_name
    )
    cursor = conexao.cursor()