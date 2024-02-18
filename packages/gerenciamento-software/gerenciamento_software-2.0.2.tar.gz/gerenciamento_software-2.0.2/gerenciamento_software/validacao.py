from .uteis import quebrar_frase

parametros_bloqueados = []
comandos_sql_bloquados = ['WHERE','FROM','SELECT','CREATE',';','=',"'",'"','`','AND','OR','ALTER','TABLE','GROUP BY','NOT','!','--']



def verificar_strings_vazias(*strings):
    for item in strings:
        if (len(item)) <=0:
            return False
        else:
            contador = 0
            for letra in range(len(item)):
                if item[letra] == ' ':
                    contador += 1
            
            if contador >= len(item):
                return True
            else:
                return False
            

def bloquear_parametro(parametro)->bool:
    parametros_bloqueados.append(parametro)
    return True


def verificar_validade_parametro(parametro)->bool:
    parametros = quebrar_frase(parametro)

    for item in parametros:
        if item in parametros_bloqueados:
            return False
    else:
        return True
    

