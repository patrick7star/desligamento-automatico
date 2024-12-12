#!/usr/bin/python3 -BO

"""
 Execução em sí do programa. Lê do terminal o tempo -- ou sortea ele,
então traduz em segundos para o temporizador que dispara o desligamento
no fim.
"""

# meus módulos:
from graficos import inicia_grafico
from utilitarios.src.tempo import Temporizador
from historico import grava_historico
from menu import *
from notificacao import *
from modo_texto import inicia_modo_texto

# biblioteca do Python:
from threading import Thread
from sys import argv
from os import system, chmod, chdir, getcwd, getenv
from random import randint
from stat import S_IRWXU, S_IXGRP, S_IXOTH
from pathlib import PosixPath

# biblioteca externa:
from print_color import print as PrintColorido

# Em qualquer tipo de execução do script, dando-o permissões que
# facilitarão suas execuções futuras.
try:
   chmod("setup.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   raiz_codigos = PosixPath(getenv("PYTHON_CODES"))
   caminho = raiz_codigos.joinpath("desligamento-automatico", "setup.py")
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...


# o filtro e organização dos argumentos do programa acontem aqui:
args_processados = MENU.parse_args()
# grava o comando passado, depois de uma interpletação para o antigo
# formato:
comando_formado = converte_para_padrao(args_processados)
grava_historico([comando_formado])

# Agora com o processamento de argumentos próprio, podemos obter os três
# mais importantes abaixo de maneira extramente simples. Eles são a ação
# a sí tomar, o modo de visuazliação e o tempo necessário(forma em string
# sem ainda conversão em segundos).
MODO_SUSPENSAO = (args_processados.acao == "suspende")
MODO_TEXTO = False if (args_processados.modo != "modo-texto") else True
TEMPO_DEMANDADO = args_processados.TEMPO

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

# pós conversão, converte o argumento sem arredondar?
segundos = stringtime_to_seg(TEMPO_DEMANDADO)
# criando temporizador.
contador = Temporizador(segundos)

def mensagemDeInterrupcao(porcentual):
   "entrega uma formatação de acordo com a cor da barra."
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

try:
   # inicia também thread onde dispara notificações espaçada baseado no
   # tempo total, para informar a hora.
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
      # para acionar este mostrador de horário, o valor mínimo tem que ser
      # mais de 7min.
      if contador.agendado().total_seconds() > 7 * 60:
         info_constante.start()
      else:
         print("info horário apenas com mais de 3min.")
   ...

   if (not MODO_TEXTO):
      # inicialização do modo gráfico ...
      if MODO_SUSPENSAO:
         inicia_grafico(contador, mensagem_final="suspendendo")
      else:
         inicia_grafico(contador)
   else:
      # inicialização do modo de texto.
      if MODO_SUSPENSAO:
         inicia_modo_texto(contador, "suspensão")
      else:
         inicia_modo_texto(contador, "desligamento")
except KeyboardInterrupt:
   # limpa tela em caso da interface ncurses ter quebrado a tela do 
   # emulador de terminal.
   system("stty sane")

   # informação colorida, para ficar mais informativo.
   mensagemDeInterrupcao(contador.percentual())

   # saindo em sí do programa.
   exit()
...

# execuntando o comando ...
if __debug__:
   import logging
   if MODO_SUSPENSAO:
      print("suspensão acionada.")
      logging.info("o sistema foi suspendido com sucesso.")
   else:
      print("desligamento acionado.")
      logging.info("o sistema foi desligado com sucesso.")
else:
   if MODO_SUSPENSAO:
      system("systemctl suspend")
   else:
      system("shutdown now")
...
