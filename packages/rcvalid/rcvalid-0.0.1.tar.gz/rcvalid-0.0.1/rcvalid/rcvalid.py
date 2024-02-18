#!/usr/bin/env python3
import re

# Ussage: validamail(correo) -> True/False

def validamail(correo):
        # patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(patron, correo):
            return True
        else:
            return False

# Ussage validaip(dirip) -> True/False

def validaip(dirip):
        patron = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(patron, dirip):
            return True
        else:
            return False


# Ussage likenumber(numero, decimales) -> numero_mask

def likenumber(numero, decimales):
    numero_mask = "{:.,}".format(round(numero, decimales))
    return numero_mask



'''
numerito = float(input("Introduce un número: "))
print(likenumber(numerito, 3))

while True:
    correo = input("Introduce un correo electrónico válido: ")
    if validamail(correo):
        print(f"\n El correo electrónico {correo} es válido")
        break
    else:
        print(f"\n El correo electrónico {correo } es un pufo")

print("Paso con correo electrónico válido")

while True:
    dirip = input("Introduce una dirección IP válida: ")
    if validaip(dirip):
        print(f"\n La dirección IP {dirip} es válida")
        break
    else:
        print(f"\n La dirección IP {dirip } es un pufo")

print("Paso con IP válida")
'''
