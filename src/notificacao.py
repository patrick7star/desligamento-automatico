

"""
 Dispara notificações do sistema Linux(Ubuntu).
 Usa o próprio programa do sistema para fazer isso,
 tudo via linha de comando, disparado pelo Python.
"""

from enum import (Enum, auto)
from subprocess import Popen

# re-exportar:
__all__ = ["Urgencia","alerta_horario", "lanca_notificacao"]

class Urgencia(Enum):
   BAIXO = auto()
   NORMAL = auto()
   ALTO = auto()

   def traduz(self) -> str:
      if self is Urgencia.BAIXO:
         return "low"
      elif self is Urgencia.NORMAL:
         return "normal"
      else:
         return "critical"
   ...
...

import logging
from pathlib import (Path, PurePosixPath)
from os import getenv

# caminho ligado ao diretório onde está o script deste programa.
caminho_do_log = PurePosixPath(
   getenv("PYTHON_CODES") + 
   "/desligamento-automatico" +
   "/data/notificacao.log"
)
# assert Path(caminho_do_log).exists()

logging.basicConfig(
   filename=caminho_do_log,
   # uma escrita por execução ...
   filemode="a",
   level=logging.DEBUG
)

def lanca_notificacao(nome_do_programa: str, mensagem: str,
importancia: Urgencia = Urgencia.NORMAL, segundos: int = None,
icone: str = None):
   """
     Mostra uma notificação no sistema Linux. Os parâmetros
    são bem simples de serem decodificados apenas pelos 
    seus nomes. Algumas resalvas são os com valores padrões,
    apenas os nomes não dizem tudo. Os que são atribuídos 
    'None' indicam que tais podem ser omitídos, ou sejam,
    o programa não para de funciona porque não estão alí,
    a opção só deixa de funcionar(é desligada), ou disparam
    a interna da caixa petra que dispara tais.
   """
   if len(nome_do_programa) > 30:
      mensagem_erro = (
         "O nome do programa deve ter menos "
         + "que 30 caractéres."
      )
      raise ValueError(mensagem_erro)
   elif len(mensagem.split()) > 20:
      raise ValueError("O texto não pode passar de 20 palavras.")
   elif segundos is not None:
      if segundos > 120 or segundos < 1:
         raise ValueError("o tempo máximo é só 2min, o mínimo 1seg.")
      else:
         tempo = ("-t", str(segundos * 1000))
   ...
   if __debug__:
      if segundos is None:
         # print("tempo é o padrão.")
         logging.info("tempo é o padrão.")
      if icone is None:
         # print("um ícone não foi selecionado")
         loggin.info("um ícone não foi selecionado")
   ...
   argumentos = [
      "notify-send", 
      "-a", nome_do_programa,
      "-u", Urgencia.traduz(importancia),
      # enfim a mensagem ...
      mensagem
   ]

   # inserção tardia baseado nos argumentos:
   if segundos is not None:
      argumentos.insert(1, tempo[1])
      argumentos.insert(1, tempo[0])
   if (icone is not None):
      argumentos.insert(1, icone)
      argumentos.insert(1, "-i")

   with Popen(argumentos) as execucao:
      if __debug__:
         logging.debug(execucao)
   ...
...


import unittest
from time import (sleep, strftime, time, localtime, gmtime)

TOTAL_DE_DISPAROS = 8

def alerta_horario(total_segundos: int, nome_do_programa: str):
   fracao_comum = total_segundos // TOTAL_DE_DISPAROS
   # pausa inicial para que não dispara imediamente.
   sleep(fracao_comum // 2)

   # divide os disparos constantes em oito partes do
   # tempo total.
   for k in range(TOTAL_DE_DISPAROS - 1):
      horario_formatado = strftime("%H:%M:%S", localtime(time()))
      if __debug__:
         logging.debug(
            "{}ª disparo de {} ..."
            .format(k + 1, TOTAL_DE_DISPAROS)
         )
         '''
         print(
            "{}ª disparo de {} ..."
            .format(k + 1, TOTAL_DE_DISPAROS)
         )'''
         horario_formatado += "{:>10d}/{}".format(
            (k + 1), 
            TOTAL_DE_DISPAROS - 1
         )
      else:
         percentual = (k / TOTAL_DE_DISPAROS) * 100
         horario_formatado += " {:>15.0f}%".format(percentual)
      ...
      try:
         lanca_notificacao(
            nome_do_programa, 
            horario_formatado, 
            importancia = Urgencia.ALTO,
            segundos = 6,
            icone="clock"
         )
      except:
         mensagem_erro = (
            "um erro ao chmar 'lanca_notifica'," 
            + " ocorreu"
         )
         logging.debug(mensagem_erro, file=sys.stderr)
      ...

      # só volta a executar a instrução acima depois de um
      # oitavo do tempo total decorrido.
      sleep(fracao_comum)
   ...
...

NOME_APP_GENERICO = "App Horário"

class Funcoes(unittest.TestCase):
   def lancaNotificacaoExemploSimples(self):
      lanca_notificacao(
         NOME_APP_GENERICO, 
         "uma nova mensagem!", 
         importancia=Urgencia.ALTO, segundos=1
      )
      lanca_notificacao(
         "ContadorAutomatico",
         "a contagem está completa!",
         segundos = 5
      )
      lanca_notificacao("Minha Confirmação App", "Okay!")
      # uma avaliação manual.
      self.assertTrue(True)
   ...
   def lancamentoComParametroIcone(self):
      horario_str = strftime("%H:%M:%S", gmtime(time()))
      lanca_notificacao(
         NOME_APP_GENERICO, horario_str,
         importancia=Urgencia.ALTO,
         icone="clock"
      )
      # uma avaliação manual.
      self.assertTrue(True)
   ...
   def testaComandoPopen(self):
      Popen(["notify-send", "um pequeno teste"])

   def constantesDisparos(self):
      alerta_horario(40, NOME_APP_GENERICO)

   def funcionamentoTemposMaiores(self):
      alerta_horario(int(3.5 * 60), NOME_APP_GENERICO)
      # no mínimo tem que terminar, a avaliação do output
      # será avaliada manualmente.
      self.assertTrue(True)
   ...
...

if __name__ == "__main__":
   unittest.main(verbose=2)
