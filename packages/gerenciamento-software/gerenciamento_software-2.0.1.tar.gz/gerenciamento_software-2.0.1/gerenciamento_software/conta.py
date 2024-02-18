from datetime import datetime 
from .conexao import *
from .retorno_dados import *
from .criptografia import criptografar_SHA256_SALT          
  

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