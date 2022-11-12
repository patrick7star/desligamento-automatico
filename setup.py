#!/usr/bin/python3 -BO

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
from os import system, chmod, chdir, getcwd, getenv
from random import randint
from stat import S_IRWXU, S_IXGRP, S_IXOTH
from os.path import join

# biblioteca externa:
from print_color import print as PrintColorido

# colocando permisões:
try:
   chmod("setup.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   caminho = join(
      getenv("PYTHON_CODES"),
      "desligamento-automatico", 
      "setup.py"
   )
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...

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
   # pós conversão, converte o argumento sem arredondar?
   if __debug__:
      print("tempo real(em seg):", segundos)
else:
   segundos = tempo_demandado

# criando temporizador.
contador = Temporizador(segundos)

# entrega uma formatação de acordo
# com a cor da barra.
def mensagemDeInterrupcao(porcentual):
   # quebra-de-linha normal.
   print("\n\n")

   # percentual em várias formas.
   complemento = 1.0 - porcentual 
   percentual = complemento * 100
   p = complemento
   # tipo de coloração.
   cor_do_progresso = "magenta"

   if p <= 1.0 and p >= 0.70:
      cor_do_progresso = "blue"
   elif p < 0.70 and p >= 0.50:
      cor_do_progresso = "green"
      intensidade = "bold"
   elif p < 0.50 and p >= 0.20:
      intensidade = "bold"
      cor_do_progresso = "yellow"
   else:
      intensidade = "bold"
      cor_do_progresso = "red"
   ...
   PrintColorido(
      "parou em {:0.1f}%\n"
      .format(percentual), 
      tag = "interrupção",
      tag_color = cor_do_progresso,
      color = "white",
      format = "bold" 
   )
...

# parte gráfica ...
try:
   inicia_grafico(contador)
except KeyboardInterrupt:
   system("stty sane")

   # informação colorida, para ficar 
   # mais informativo.
   mensagemDeInterrupcao(contador.percentual())

   # saindo em sí do programa.
   exit()
...

# execuntando o comando ...
if __debug__:
   system("echo desligamento acionado.")
else:
   system("shutdown now")
