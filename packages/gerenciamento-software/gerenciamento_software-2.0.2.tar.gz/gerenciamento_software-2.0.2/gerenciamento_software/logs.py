from .infos import *
from colorama import init, Fore, Back
import os



init()
gerar_logs = False
estado_console_log = False


def configurar_log(criar_logs:bool=False,exibir_logs_em_console:bool=False):
    global gerar_logs
    global estado_console_log
    gerar_logs = criar_logs
    estado_console_log = exibir_logs_em_console


def verificar_status_log():
    global gerar_logs
    return gerar_logs

    
def gerar_log(tipo:str,conteudo:str):
    if gerar_logs == True:
        data_atual = retornar_data_atual("%d-%m-%Y")
        hora_atual = retornar_hora_atual()

        tipo = tipo.upper()

        conteudo = f'{tipo}: {conteudo} || DATA: {data_atual} || HORA: {hora_atual}\n'
        with open('log.txt', 'a') as arquivo:
            arquivo.write(conteudo)

        if estado_console_log == True:
            os.system("cls")
            print(Fore.RED + conteudo)

        return True
    else:
        print(Fore.RED + "ERRO: Gerar Log está desativado! Para ativar use a função 'configLog()'")