"""
  Trabalha e coloca como extensão, o tempo que este computador esteve ligado
na parte "gráfica" deste programa. Ainda não sei como mudar a interface 
para caber bem no UX da interface de texto.
"""
__all__ = ["tempos_importantes"]

from datetime import (timedelta)
from sys import (path)
from unittest import (TestCase, main)


def valores_de_proc_uptime() -> tuple[timedelta, timedelta]:
   """
   O retorno é o tempo que tal system foi ligado, e o tempo de uso de cada
   CPU que ele possui. 
   """
   with open("/proc/uptime", "rb") as arquivo:
      conteudo = arquivo.readline()
      return tuple(
         timedelta(seconds=float(m)) 
         for m in conteudo.split()
      )

def tempos_importantes() -> tuple[timedelta, timedelta]:
   "Mesmo conteúdo acima, porém com nome mais palatável para exportar."
   return valores_de_proc_uptime()

# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- - 
#  Testes unitários de funções mesmo que sejam auxiliares; classes e seus 
# métodos acima; até mesmo utilitários da linguagem ou de alguma biblioteca.
# === === === === === === === === === === === === === === === === === === = 
class Unitarios(TestCase):
   def extracao_dos_valores(self):
      print("\nExtraindo do arquivo na ordem que estão lá:")
      output = valores_de_proc_uptime()
      print(output)

   def interpletando_tais_numeros(self):
      print("\nTipo de Importação '%s'" % __name__)
      path.append("./lib")

      from legivel import (tempo as Tempo)

      output = valores_de_proc_uptime()
      t1 = Tempo(output[0].total_seconds())
      t2 = Tempo(output[1].total_seconds())

      print("Computador ligado: %s" % t1)
      print("Tempo de uso do CPU: %s" % t2)

if __name__ == "__main__":
   main()
