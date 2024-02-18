from hashlib import sha256
import random
import string



def criptografar_SHA256(arg:str):
    hash = sha256(arg.encode())
    resultado = hash.hexdigest()
    return resultado


def criptografar_SALT():
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(32))


def criptografar_SHA256_SALT(arg:str):
    salt = criptografar_SALT()
    hashFinal = arg+salt
    hashFinal = criptografar_SHA256(hashFinal)

    return {'salt':salt,'hashFinal':hashFinal}