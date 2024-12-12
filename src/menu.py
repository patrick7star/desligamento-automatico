

"""
   O menu do programa usando a ferramenta já da linguagem. Quando o 
 o programa estiver mais maduro e fechado, a hora certa digo de acroplar 
 este 'menu' já configurado no programa como o todo.
"""

#o que será exportado?
__all__ = ["converte_para_padrao", "MENU"]

from argparse import (ArgumentParser, Namespace)

MENU = ArgumentParser(
   prog="Desligamento",
   usage="%(prog)s [opções] <TEMPO>",
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
   "TEMPO", type=str, default="1min",
   help="""
   o tempo até a 'ação' ser executada. Se não colocado, o valor
   padrão limita-se entre 10seg à 1min."
   """
)

from sys import argv

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

if __debug__:
   resultado = MENU.parse_args()
   print(
      "\n\tação: '{}'\n\tmodo: '{}'\n\ttempo: {}"
      .format(
         resultado.acao, 
         resultado.modo, 
         resultado.TEMPO
      ),end="\n\n"
   )
   print (resultado)
   comando_para_historico = converte_para_padrao(resultado)
   print(
      "conversão para o padrão: '{}'"
      .format(comando_para_historico)
   )
...
