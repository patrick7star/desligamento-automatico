"""
   O menu do programa usando a ferramenta já da linguagem. Quando o 
 o programa estiver mais maduro e fechado, a hora certa digo de acroplar 
 este 'menu' já configurado no programa como o todo.
"""

#o que será exportado?
__all__ = ["converte_para_padrao", "MENU"]

from argparse import (ArgumentParser, Namespace, SUPPRESS)
from sys import argv
from unittest import (TestCase)

MENU = ArgumentParser(
   prog="Desligamento",
   usage="%(prog)s [opções] <tempo>",
   description="""
   Programa com um contador que agenda em alguns segundos, minutos ou 
   horas o desligamento/ou suspensão do computador. Existe alternativos 
   modos de se fazer isso como também a ação em sí, onde pode se desligar 
   ou suspender, você escolhe.
   """
)

MENU.add_argument(
   "--visualizacao", type=str, choices=("ncurses", "modo-texto"),
   default="ncurses", dest="modo",
   help = """
   como se dará o progresso até o fim do tempo delimitado. Há duas opções,
   uma mais gráfica(usando a biblioteca ncurses) ,e a outra mais textual, 
   porém ainda com coloração se assim for permitido no terminal. 
   """
)

MENU.add_argument(
   "--acao",  choices=("desliga", "suspende"), default="desliga",
   help="""
   Só existe apenas dois motos de este programa executar o que ele foi 
   feito no final: a suspensão do computador, ou o desligamento. Você então
   pode selecionar duas opções, mas o desligamento é padrão em caso de 
   ausência
   """,
)

MENU.add_argument(
   "TEMPO", type=str, default="1min", metavar="XY.Z(h|min|seg)",
   help="""
   o tempo até a 'ação' ser executada. Se não colocado, o valor
   padrão limita-se entre 10seg à 1min. Alguns exemplos de input são algo
   do tipo: 53s, 3h, 15min, 5.4h, 36.2min, 17seg"
   """
)

MENU.add_argument(
   "--ligado", '-l', required=False, action="store_true",
   help="""
   Informa quanto este computador está ligado. A versão de visualização do
   'ncurses' já informa isso, quando tal é acionado, porém não existia,
   até agora, uma opção para ver o tempo que o computador está operando sem
   necessariamente acionar o desligamento/ou a suspensão.
   """
)


def converte_para_padrao(argumento: Namespace) -> str:
   """
   Como existe uma parte da rotina principal que registra o comando dado,
   e este menu altera a formatação, é preciso ter um conversão entre os 
   tipos, assim o comando pode ser convertido para a antiga versão sem
   causar problemas com os demais módulos do programa que usam ela como
   base para demais 'features'.
   """
   nome_do_programa = argv[0]
   acao = "--" + argumento.acao
   modo = "--" + argumento.modo
   tempostr = argumento.TEMPO
   return " ".join((nome_do_programa, acao, modo, tempostr))
...

class InfoDoParserBasico(TestCase):
   def setUp(self):
      import sys

      sys.argv.append("--acao=suspende")
      sys.argv.append("--visualizacao=modo-texto")

      print(sys.argv)

   def runTest(self):
      resultado = MENU.parse_args()
      comando_para_historico = converte_para_padrao(resultado)
      print(
         "\n\tação: '{}'\n\tmodo: '{}'\n\ttempo: {}"
         .format(
            resultado.acao, 
            resultado.modo, 
            resultado.TEMPO
         ),end="\n\n"
      )
      print (resultado)
      

      print(
         "conversão para o padrão: '{}'"
         .format(comando_para_historico)
      )
