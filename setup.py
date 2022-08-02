#!/usr/local/bin/python3.10 -BO

"""
 Execução em sí do programa. Lê do terminal
o tempo -- ou sortea ele, então traduz em 
segundos para o temporizador que dispara
o desligamento no fim.
"""


# meus módulos:
from interface_grafica import inicia_grafico
from temporizador import stringtime_to_segundos, Temporizador

# biblioteca do Python:
from sys import argv
from os import system
from random import randint


# formando argumento ...
if len(argv) > 1:
   tempo_demandado = " ".join(argv[1:])
else:
   tempo_demandado = randint(30, 60)
...

if __debug__:
   print("formação do argumento: \"%s\"" % tempo_demandado)

if type(tempo_demandado) == str:
   segundos = stringtime_to_segundos(tempo_demandado)
else:
   segundos = tempo_demandado

# criando temporizador.
contador = Temporizador(segundos)
# parte gráfica ...
inicia_grafico(contador)

# execuntando o comando ...
if __debug__:
   system("echo desligamento acionado.")
else:
   system("shutdown now")
