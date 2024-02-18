import mysql.connector
from datetime import datetime 
from .criptografia import criptografar_SHA256_SALT          
from .infos import retornar_data_atual, retornar_hora_atual

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


def sql_criar_conta(tabela:str, coluna_nome:str, coluna_email:str, coluna_senha:str, nome:str, email:str, senha:str,coluna_salt:str,criptografar:bool=False):
    try: 
        if (sql_verificar_uso_email(tabela,email)):
            return [False, 'Email Utilizado']
        else:
            if (verificar_validade_email(email)):
                comando = f'INSERT INTO {tabela} ({coluna_nome},{coluna_email},{coluna_senha}) VALUES("{nome}","{email}","{senha}")'

                if (criptografar):
                    hash = criptografar_SHA256_SALT(senha)
                    salt = hash['salt']
                    senha = hash['hashFinal']
                    comando = f'INSERT INTO {tabela} ({coluna_nome},{coluna_email},{coluna_senha},{coluna_salt}) VALUES("{nome}","{email}","{senha}","{salt}")'
                
                cursor.execute(comando)
                conexao.commit()

                return True
            else:
                return [False, 'Insira um email válido']
    except:
        return [False, 'Erro ao tentar executar a função']
    finally:
        cursor.close()  
        conexao.close()
          

def sql_logar_conta(tabela:str, coluna_email:str, coluna_senha:str, email:str, senha:str, coluna_salt:str, criptografar:bool=False):
    try:
        conexao.commit()

        if (criptografar):
            pegando_salt = f'SELECT {coluna_salt} FROM {tabela} WHERE {coluna_email}="{email}"'
            cursor.execute(comando)
            salt = cursor.fetchall()

            if ((len(salt)) <=0):
                return [False, 'Conta nao encontrada']
            else:
                salt = salt[0]
                hash_consulta = senha+salt
                hashFinal = criptografar_SHA256_SALT(hash_consulta)
                senha = hashFinal['hashFinal']

        comando = f'SELECT * FROM {tabela} WHERE {coluna_email}="{email}" AND {coluna_senha}="{senha}"'
        cursor.execute(comando)
        resultado = cursor.fetchall()

        if ((len(resultado)) !=0):
            return True
        else:
            return [False, 'Conta não encontrada']
    except:
        return [False, 'Erro ao tentar executar a função']
    finally:
        cursor.close()  
        conexao.close()
              

def sql_alterar_conta(tabela:str,coluna:str,valor,condicao:str):
    try:
        conexao.commit()

        comando = f'UPDATE {tabela} SET {coluna}={valor} WHERE {condicao}'
        cursor.execute(comando)
        conexao.commit()

        return True
    except:
        return [False, 'Erro ao tentar executar a função']
    finally:
        cursor.close()  
        conexao.close()
              

def sql_excluir_conta(tabela:str,condicao:str):
    try:
        conexao.commit()
    
        comando = f'DELETE FROM {tabela} WHERE {condicao}'
        cursor.execute(comando)
        conexao.commit()

        return True
    except:
        return [False, 'Erro ao tentar executar a função']
    finally:
        cursor.close()  
        conexao.close()
        

def sql_registrar_log(tabela_log:str, tabela_usuario:str, coluna_id_log:str, coluna_motivo_log, coluna_data_log:str, coluna_hora_log:str, coluna_id_usuario:str, coluna_email:str, email:str, motivo_log:str):
    try:
        conexao.commit()

        data = retornar_data_atual("%Y-%m-%d")
        hora = retornar_hora_atual()
        id = sql_retornar_id_usuario(tabela_usuario,coluna_id_usuario,coluna_email,email)

        comando = f'INSERT INTO {tabela_log} ({coluna_id_log},{coluna_motivo_log},{coluna_data_log},{coluna_hora_log}) VALUES("{id}","{motivo_log}","{data}","{hora}")'
        cursor.execute(comando)
        conexao.commit()

        return True
    except:
        return [False, 'Erro ao executar a função']
    finally:
        cursor.close()  
        conexao.close()


def sql_verificar_uso_email(tabela:str, email:str):
    try:
        conexao.commit()

        comando = f'SELECT * FROM {tabela} WHERE email = "{email}"'
        cursor.execute(comando)
        resultado = cursor.fetchall()

        if ((len(resultado)) != 0):
            return True
        else:
            return False
    finally:
        cursor.close()  
        conexao.close()

    
def sql_retornar_id_usuario(tabela:str, coluna_id:str, coluna_email:str, email:str):
    try:
        conexao.commit()

        comando = f'SELECT {coluna_id} FROM {tabela} WHERE {coluna_email} = "{email}"'
        cursor.execute(comando)
        id_usuario = cursor.fetchall()
        id_usuario = id_usuario[0][0]

        return int(id_usuario)
    except:
        return [False, 'Erro ao tentar executar a função']
    finally:
        cursor.close()  
        conexao.close()
          
  
def verificar_validade_email(email:str):
  if '@' in email and '.' in email:
    return True
  else:
    return False