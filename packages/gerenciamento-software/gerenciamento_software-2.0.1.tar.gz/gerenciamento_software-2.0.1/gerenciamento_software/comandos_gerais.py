from .conexao import *



def sql_executar_comando(comando):
    try:
        conexao.commit()

        cursor.execute(comando)
        conexao.commit()

        return True
    except:
        return [False, 'Erro ao executar a função']
    finally:
        cursor.close()  
        conexao.close()

    
def sql_consultar_dado(comando):
    try:
        conexao.commit()
        cursor.execute(comando)
        resultado = cursor.fetchall()

        return resultado
    except:
        return [False, 'Erro ao executar a função']     
    finally:
        cursor.close()  
        conexao.close()