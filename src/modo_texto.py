"""
Processo "gráfico", mas textual, do desligamento ordenado. Cuida de colorir,
organizar e formatar a visualização da saída.
"""

# o que será exportado?
__all__ = {"inicia_modo_texto", "formatacao_do_tempo_ligado"}

# Biblioteca padrão do Python:
from time import sleep
from datetime import timedelta
# Biblioteca externa:
try:
   from externo import (COLORACAO_ATIVADO, PrintColorido)
except: 
   pass
finally: 
   pass
# Própria biblioteca:
# Minhas bibliotecas externas:
from externo import(
  tempo as tempo_legivel, TempoEsgotadoError, Temporizador,
  DIA, MES
)


def informacao_colorida(timer: Temporizador, o_que_e: str) -> None:
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
      restante_str = tempo_legivel(t - t*p, acronomo = True)
   except:
      restante_str = "nenhum"

   PrintColorido(
      "está em {:>5.1f}%, faltam".format(percentual),
      tag = o_que_e, tag_color = cor_do_progresso,
      color = "white", format = "bold", end=" "
   )
   PrintColorido("{:>9s}".format(restante_str), format="underline")
...

def informacao_sem_cor(timer: Temporizador, o_que_e: str) -> None:
   porcentual = timer.percentual()
   # Percentual em várias formas.
   complemento = 1.0 - porcentual 
   percentual = complemento * 100
   p = complemento

   # computando tempo restante...
   t = timer.agendado().total_seconds()
   p = timer.percentual()
   try:
      restante_str = tempo_legivel(t - t*p, acronomo = True)
   except:
      restante_str = "nenhum"

   print(
      "[{}] está em {:>5.1f}%, faltam {:>9s}"
      .format(o_que_e.center(16), percentual, restante_str)
   )

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


def inicia_modo_texto(contador: Temporizador, tipo: str) -> None:
   print("processo de \"%s\" iniciado." % tipo)

   try:
      while bool(contador):
         if COLORACAO_ATIVADO:
            informacao_colorida(contador, tipo)
         else:
            informacao_sem_cor(contador, tipo)
         sleep(contador.agendado().total_seconds() / 26)
      ...
   except TempoEsgotadoError:
      pass
...

def tempo_legivel_mais_detalhado(tempo: timedelta) -> str:
   segundos = tempo.total_seconds()
   UMA_SEMANA = 7 * DIA

   if (segundos >= UMA_SEMANA) and (segundos < MES):
      semanas = segundos / UMA_SEMANA
      return "%0.2f semanas" % semanas
   else:
      seg = tempo.total_seconds()
      traducao = tempo_legivel(seg)
      return traducao
      
def formatacao_do_tempo_ligado(tempo: timedelta):
   traducao = tempo_legivel_mais_detalhado(tempo)
   RECUO = "\t\b\b\b\b"

   if COLORACAO_ATIVADO:
      PrintColorido(
         "\n{}O computador já está ligado por".format(RECUO), 
         format='bold', color='yellow', end=" "
      )
      PrintColorido(traducao, format='underline', color='white', end=' ')
      PrintColorido("direto.\n", format='bold', color='yellow')
   else:
      print(
         "\n{}O computador já está ligado por {} diretamente."
         .format(RECUO, traducao), end='\n\n'
      )
