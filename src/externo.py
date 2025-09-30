"""
   Concentrar a importação de pacotes externos bem aqui. Assim, o processo
 pode ser feito apenas uma vez, então todos os demais módulos que contam
 com tal, podem importar daqui. Se houver algum problema no futuro ao tentar
 importa-lôs, também cairia aqui.
"""

from linque import (caminho_do_projeto_do_programa)
import sys, pprint

# Apenas executa testes em debug quando executado deste próprio script aqui.
FALHOU = -1
NO_PROPRIO_MODULO = (__file__.find(__name__) == FALHOU)

if __debug__ and NO_PROPRIO_MODULO:
    print(
        """
        \rInformção de todos:
        \r    - name: {}
        \r    - file: '{}'
        \r    - package: '{}'
        \r    - loader: {}
        \r    - doc: '''{}'''
        \r    - cached: '{}'
        \r    - spec: '{}'
        """.format(
            __name__, __file__, __package__, __loader__, __doc__,
            __cached__, __spec__
        )
    )

if __debug__ and NO_PROPRIO_MODULO:
    print("\nTodas bibliotecas de busca(antes da adição):")
    pprint.pp(sys.path, indent=4, width=90)
    sys.path.sort()

PROJETO_DIR =caminho_do_projeto_do_programa()
CAMINHO_LIB = PROJETO_DIR.joinpath("lib")
sys.path.append(str(CAMINHO_LIB))

if __debug__ and NO_PROPRIO_MODULO:
    print("\nTodas bibliotecas de busca:")
    sys.path.sort()
    pprint.pp(sys.path, indent=4, width=90)

# Agora, tentando importa para re-exporta tais módulos...
#from legivel import *
from utilitarios.legivel import *
from utilitarios.texto import (constroi_str as forma_string)
from utilitarios.tempo import *

if __debug__ and NO_PROPRIO_MODULO:
    pprint.pp(dir(), indent=7, compact=True)

# Biblioteca externa:
try:
   from print_color import (print as PrintColorido)
   COLORACAO_ATIVADO = True
except ModuleNotFoundError:
   COLORACAO_ATIVADO = False
finally:
   if (not COLORACAO_ATIVADO) and __debug__:
      print("A coloração está desativada no momento.")
