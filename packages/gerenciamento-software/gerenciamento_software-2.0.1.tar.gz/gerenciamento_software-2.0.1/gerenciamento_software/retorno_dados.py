from .conexao import *


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