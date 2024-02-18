import numpy as np

def saludar():
    print("Hola, te saludo desde saludos.saludar()")


class Saludo:
    def __init__(self):
        print("Hola, te saludo desde: __init__")

def generar_array(numeros):
    return np.arange(numeros)

def prueba():
    print("Esto es una nueva prueba de la nueva versión 7.0.")

print(__name__)
if __name__ == "__main__":
    saludar()
    print("me estoy ejecutando")
    print(generar_array(5))