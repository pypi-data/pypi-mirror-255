from .conexao import *
from .infos import retornar_data_atual, retornar_hora_atual
from .retorno_dados import *

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