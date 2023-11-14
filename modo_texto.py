

"""
Processo "gráfico", mas textual, do desligamento ordenado.
"""

# biblioteca externa:
from print_color import print as PrintColorido
# própria biblioteca:
from utilitarios.src.legivel import tempo
from utilitarios.src.tempo import (TempoEsgotadoError, Temporizador)

# o que será exportado?
__all__ = {"inicia_modo_texto"}


def informacao(timer: Temporizador, o_que_e: str):
   porcentual = timer.percentual()
   # percentual em várias formas.
   complemento = 1.0 - porcentual 
   percentual = complemento * 100
   p = complemento
   cor_do_progresso = define_cor(p)

   # computando tempo restante...
   t = timer.agendado().total_seconds()
   p = timer.percentual()
   try:
      restante_str = tempo(t - t*p, acronomo = True)
   except:
      restante_str = "nenhum"

   PrintColorido(
      "está em {:02.1f}%, faltam".format(percentual),
      tag = o_que_e, tag_color = cor_do_progresso,
      color = "white", format = "bold", end=" "
   )
   PrintColorido("{}".format(restante_str), format="underline")
...

def define_cor(p: float) -> str:
   # tipo de coloração.
   cor_do_progresso = "magenta"

   if p <= 1.0 and p >= 0.70:
      cor_do_progresso = "blue"
   elif p < 0.70 and p >= 0.45:
      cor_do_progresso = "green"
      intensidade = "bold"
   elif p < 0.45 and p >= 0.23:
      intensidade = "bold"
      cor_do_progresso = "yellow"
   else:
      intensidade = "bold"
      cor_do_progresso = "red"
   ...

   return cor_do_progresso
...

def informacao_dinamica(timer: Temporizador, o_que_e: str) -> None:
   porcentual = timer.percentual()
   # percentual em várias formas.
   complemento = 1.0 - porcentual
   percentual = complemento * 100
   p = complemento

   # computando tempo restante...
   t = timer.agendado().total_seconds()
   p = timer.percentual()
   try:
      restante_str = tempo(t - t*p, acronomo = True)
   except:
      restante_str = "nenhum"

   PrintColorido("\ro tempo restante é",end=" ")
   PrintColorido(
      restante_str,
      color = define_cor(1.0 - p),
      format = "bold", end="."
   )

   if (not bool(timer)):
      print("\niniciando %s..." % o_que_e)
...

from time import sleep
from datetime import timedelta

def inicia_modo_texto(contador: Temporizador, tipo: str) -> None:
   print("processo de \"%s\" iniciado." % tipo)

   try:
      while bool(contador):
         if contador.agendado() >= timedelta(minutes=1):
            informacao(contador, tipo)
            sleep(contador.agendado().total_seconds() / 26)
         else:
            informacao_dinamica(contador, tipo)
            sleep(0.8)
         ...
      ...
   except TempoEsgotadoError:
      pass
...
