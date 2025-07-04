#!/usr/bin/python3

"""
 Execução em sí do programa. Lê do terminal o tempo -- ou sortea ele,
então traduz em segundos para o temporizador que dispara o desligamento
no fim.
"""

# Meus módulos:
from graficos import inicia_grafico
from janelas import (Acao, )
from historico import grava_historico
from menu import *
from notificacao import *
from modo_texto import (inicia_modo_texto, formatacao_do_tempo_ligado)
from linque import (caminho_do_script, cria_linque_do_script)
from tempo_ligado import (tempos_importantes)
# Biblioteca do Python:
from threading import Thread
from sys import argv
from os import (system, chmod, chdir, getcwd, getenv, popen)
from random import randint
from stat import S_IRWXU, S_IXGRP, S_IXOTH
from pathlib import PosixPath
from datetime import (timedelta)
# Minhas Bibliotecas externas:
try:
   from externo import (Temporizador, COLORACAO_ATIVADO, PrintColorido)
   # Nota: A ordem da importação e os possíveis crashs importam. A variável
   # e a função, podem quebrar, por isso o 'Temporizador' é importado 
   # primeiro, se fossem o contrário, o lançamento de uma exceção pararia
   # de importa-lô.
except NameError:
   pass
except ImportError:
   if __debug__:
      print("Provavelmente não há uma biblioteca 'print_color'.")
finally:
   pass
# Importação aplicada apenas no modo debug:
if __debug__:
   import logging


def muda_o_nivel_de_permisao_do_script():
   " Muda a permissão do script que executa este programa."
   nivel_de_permissao = S_IRWXU | S_IXGRP | S_IXOTH
   caminho = caminho_do_script()
   chmod(caminho, nivel_de_permissao)

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

def mensagemDeInterrupcao(porcentual):
   "Entrega uma formatação de acordo com a cor da barra."
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

   if COLORACAO_ATIVADO:
      PrintColorido(
         "Parado em {:0.1f}%.\n"
         .format(percentual),
         tag = "interrupção",
         tag_color = cor_do_progresso,
         color = "white",
         format = "bold"
      )
   else:
      print("Parado em {:3.0f}%.".format(percentual))

def avalia_opcoes_passadas_no_terminal():
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
            acao = Acao.Suspende
            inicia_grafico(contador, mensagem_final="suspendendo", acao=acao)
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
      exit(0)
   ...

def aplica_o_processo_de_desligamento():
   # execuntando o comando ...
   if __debug__:
      if MODO_SUSPENSAO:
         print("Suspensão acionada.")
         logging.info("o sistema foi suspendido com sucesso.")
      else:
         print("desligamento acionado.")
         logging.info("O sistema foi desligado com sucesso.")
   else:
      if MODO_SUSPENSAO:
         comando = "systemctl suspend"
      else:
         comando = "shutdown now"

      stream = popen(comando)
      code = stream.close()

      if code is not None:
         print(
            "[erro(%d)] houve um erro ao executar o comando '%s'." 
            % (code, comando)
         )


# o filtro e organização dos argumentos do programa acontem aqui:
args_processados = MENU.parse_args()

# Agora com o processamento de argumentos próprio, podemos obter os três
# mais importantes abaixo de maneira extramente simples. Eles são a ação
# a sí tomar, o modo de visuazliação e o tempo necessário(forma em string
# sem ainda conversão em segundos).
MODO_SUSPENSAO = (args_processados.acao == "suspende")
MODO_TEXTO = False if (args_processados.modo != "modo-texto") else True
TEMPO_DEMANDADO = args_processados.TEMPO
APENAS_TEMPO_LIGADO = args_processados.ligado

cria_linque_do_script()
muda_o_nivel_de_permisao_do_script()

if APENAS_TEMPO_LIGADO:
   (t, _) = tempos_importantes()
   formatacao_do_tempo_ligado(t)

else:
   # Grava o comando passado, depois de uma interpletação para o antigo
   # formato:
   comando_formado = converte_para_padrao(args_processados)
   grava_historico([comando_formado])
   # Pós conversão, converte o argumento sem arredondar?
   segundos = stringtime_to_seg(TEMPO_DEMANDADO)
   contador = Temporizador(segundos)

   avalia_opcoes_passadas_no_terminal()
   aplica_o_processo_de_desligamento()

