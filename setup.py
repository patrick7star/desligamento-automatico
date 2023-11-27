#!/usr/bin/python3 -BO

"""
 Execução em sí do programa. Lê do terminal
o tempo -- ou sortea ele, então traduz em 
segundos para o temporizador que dispara
o desligamento no fim.
"""


# meus módulos:
from graficos import inicia_grafico
from utilitarios.src.tempo import Temporizador

# biblioteca do Python:
from sys import argv
from os import system, chmod, chdir, getcwd, getenv
from random import randint
from stat import S_IRWXU, S_IXGRP, S_IXOTH

# biblioteca externa:
from print_color import print as PrintColorido

from pathlib import PosixPath
# Em qualquer tipo de execução do script, dando-o permissões que
# facilitarão suas execuções futuras.
try:
   chmod("setup.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   raiz_codigos = PosixPath(getenv("PYTHON_CODES"))
   caminho = raiz_codigos.joinpath(
      "desligamento-automatico", 
      "setup.py"
   )
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...

# outras possíveis opções que podem ser acionadas.
from historico_e_configuracao import grava_historico
comando_formado = " ".join(argv)
if __debug__:
   print("comando =",comando_formado)
grava_historico([comando_formado])

# alterna para suspensão ao invés do desligamento.
modo_suspensao = False
if "--suspende" in argv:
   if __debug__:
      print("argumentos agora:", argv)
   argv.remove("--suspende")
   modo_suspensao = (not modo_suspensao) 
...

# alterna modo gráfico para modo de texto, este bem mais claro sobre
# como está o comando, do contrário era só digitar o comando no
# terminal mesmo.
MODO_TEXTO = False
if "--modo-texto" in argv:
   argv.remove("--modo-texto")
   MODO_TEXTO = (not MODO_TEXTO) 
...

# formando argumento ...
if len(argv) > 1:
   tempo_demandado = " ".join(argv[1:])
else:
   tempo_demandado = randint(30, 60)
...

if __debug__:
   print("formação do argumento: \"%s\"" % tempo_demandado)

def stringtime_to_seg(string: str) -> float:
   caracteres = []
   # remove todos espaços brancos.
   for char in string:
      if not char.isspace():
         caracteres.append(char)
   ...
   # acha divisor entre peso e parte numérica.
   marco = None
   for (i, char) in enumerate(caracteres):
      if char.isalpha():
         marco = i
         break
      ...
   ...
   # transformando em respectivos objetos.
   digitos = float(''.join(caracteres[0:marco]))
   peso = ''.join(caracteres[marco:])

   if marco == None:
      raise Exception("argumento mal formado: %s" % string)

   if peso.startswith("min") or peso == "m":
      return digitos * 60
   elif peso.startswith("seg") or peso == "s":
      return digitos
   elif peso.startswith("hora") or peso == "h":
      return digitos * 3600
   elif peso.startswith("dia") or peso == "d":
      return digitos * 3600 * 24
   else:
      raise Exception("não implementado para tal")
...
if type(tempo_demandado) == str:
   segundos = stringtime_to_seg(tempo_demandado)
   # pós conversão, converte o argumento sem arredondar?
   if __debug__:
      print("tempo real(em seg):", segundos)
else:
   segundos = tempo_demandado

# criando temporizador.
contador = Temporizador(segundos)

# entrega uma formatação de acordo com a cor da barra.
def mensagemDeInterrupcao(porcentual):
   # quebra-de-linha normal.
   print('\n')

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

from notificacao import *
from threading import Thread
from modo_texto import inicia_modo_texto

# parte gráfica ...
try:
   # inicia também thread onde dispara notificações
   # espaçada baseado no tempo total, para informar
   # a hora.
   info_constante = Thread(
      target=alerta_horario, 
      args=(
         # tem que ser um inteiro, pois por qualquer motivo
         # bem difícil de responder, quebra com valores decimais.
         int(contador.agendado().total_seconds()),
         "Desligamento Automático"
      ),
      daemon=True,
      # para encontrar thread no gerenciador de 
      # tarefas do sistema.
      name="alerta-de-horarioDA"
   )
   if __debug__:
      # no modo debug sempre dispara.
      print(contador.agendado())
      info_constante.start()
   else:
      # para acionar este mostrador de horário, o valor mínimo
      # tem que ser mais de 7min.
      if contador.agendado().total_seconds() > 7 * 60:
         info_constante.start()
      else:
         print("info horário apenas com mais de 3min.")
   ...

   if (not MODO_TEXTO):
      # inicialização do modo gráfico ...
      if modo_suspensao:
         inicia_grafico(contador, mensagem_final="suspendendo")
      else:
         inicia_grafico(contador)
   else:
      if modo_suspensao:
         inicia_modo_texto(contador, "suspensão")
      else:
         inicia_modo_texto(contador, "desligamento")
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
   import logging
   if modo_suspensao:
      print("suspensão acionada.")
      logging.info("o sistema foi suspendido com sucesso.")
   else:
      print("desligamento acionado.")
      logging.info("o sistema foi desligado com sucesso.")
else:
   if modo_suspensao:
      system("systemctl suspend")
   else:
      system("shutdown now")
