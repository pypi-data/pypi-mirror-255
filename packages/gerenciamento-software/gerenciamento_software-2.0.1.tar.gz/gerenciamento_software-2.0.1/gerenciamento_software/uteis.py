import smtplib
import email.message
from datetime import datetime


def quebrar_frase(frase):
    pass


def enviar_verificacao_email(email_remetente,senha_remetente,nome_destinatario,email_destinatario,codigo_verificacao,corpo_do_email=False):
    if corpo_do_email == False:
        corpo_email = f"""
        <p>Olá {nome_destinatario}! Este é o código de verificação:</p>
        <a style='text-decoration:none;text-align:center;cursor: pointer;' target='_blank' href=''><input style='text-align:center;cursor: pointer;border:0;padding:5px;width:100px;height:45px;background-color:black;color:white;' type='button' value='{codigo_verificacao}'></a>
        """

    msg = email.message.Message()
    msg['Subject'] = "Verifique Sua Conta"
    msg['From'] = f'{email_remetente}'
    msg['To'] = f'{email_destinatario}'
    password = f'{senha_remetente}'

    msg.add_header('Content-Type','text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()

    s.login(msg['From'],password)
    s.sendmail(msg['From'],[msg['To']], msg.as_string().encode('utf-8'))
    
    return True   