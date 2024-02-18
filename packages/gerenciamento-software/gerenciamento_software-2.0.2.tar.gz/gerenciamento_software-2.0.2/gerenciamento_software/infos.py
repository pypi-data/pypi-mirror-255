from datetime import datetime

def retornar_hora_atual():
    hora_atual = datetime.now()
    hora_atual = hora_atual.time()
    hora_atual = str(hora_atual)

    return hora_atual[0:8]


def retornar_data_atual(formato):
    data_atual = datetime.now()
    data_atual = data_atual.date()
    data_atual = data_atual.strftime(formato)

    return data_atual
