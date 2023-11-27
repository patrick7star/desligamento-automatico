
"""
  Configurações definidas manualmente, como o intervalo de segundos para
acionamentos não especificados, interface padrão do programa no momento,
como de texto ou "semi-gráfica".
  Também cuidara do arquivo de histórico sobre todos comandos acionados, 
o tempo de cada comando, a média, o "modo gráfico" mais utilizados.
"""

# o que será exportado?
__all__ = ["grava_historico"]

from collections.abc import (Mapping, Sequence)
from json import (JSONDecoder, load, dump)
from pathlib import PosixPath
from os import getenv

Historico = Sequence[str]
RAIZ_DOS_CODIGOS = getenv("PYTHON_CODES")
CAMINHO_HISTORICO = PosixPath().joinpath(
   RAIZ_DOS_CODIGOS,
   "desligamento-automatico/data",
   PosixPath("historico.json")
)

def carrega_historico() -> Historico:
   try:
      with open(CAMINHO_HISTORICO, "rt") as arquivo:
         history = load(arquivo) 
         if __debug__: print("history =", history)
         return history["histórico"]
      ...
   except FileNotFoundError:
      if __debug__:
         print("como o arquivo não existe, está sendo criado um...")
      # colocando uma lista vázia...
      vazio = """{
      \r   "histórico":[]
      \r}
      """
      with open(CAMINHO_HISTORICO, "wt") as arquivo:
         arquivo.write(vazio)

      import sys
      print(
         "BD dos histórico de comandos ainda não existe!",
         file= sys.stderr
      )
      exit()
   ...
...

def grava_historico(novos: Sequence[str]) -> bool:
   # não grava valores inválidos ou listas vázias.
   if (novos is None) or (len(novos) == 0):
      return False

   # carrega para incrementar.
   antigo_conteudo = carrega_historico()
   if __debug__:
      print("conteúdo carregado =", antigo_conteudo)
   novos.extend(antigo_conteudo)
   estrutura = {"histórico": novos}

   with open(CAMINHO_HISTORICO, "wt") as arquivo:
      dump(estrutura, arquivo, ensure_ascii=False, indent=True)
      return True
   return False
...

Configuracao = Mapping[str:str]
