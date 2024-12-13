
"""
  Configurações definidas manualmente, como o intervalo de segundos para
acionamentos não especificados, interface padrão do programa no momento,
como de texto ou "semi-gráfica".
  Também cuidara do arquivo de histórico sobre todos comandos acionados,
o tempo de cada comando, a média, o "modo gráfico" mais utilizados.
"""

# o que será exportado?
__all__ = ["grava_historico", "Visualizacao", "carrega_modo"]

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
# template para criação de JSON inicial.
MODELO_VAZIO = """{
   \r"modo_de_visualização": "Visualizacao.NCURSES",
   \r
   \r"histórico":[]
}"""
# nome das variáveis dentro do JSON.
CHAVE_VISUALIZACAO = "modo_de_visualização"
CHAVE_HISTORICO = "histórico"

def carrega_historico() -> Historico:
   try:
      with open(CAMINHO_HISTORICO, "rt") as arquivo:
         history = load(arquivo)
         if __debug__: print("history =", history)
         return history[CHAVE_HISTORICO]
      ...
   except FileNotFoundError:
      if __debug__:
         print("como o arquivo não existe, está sendo criado um...")
      # colocando uma lista vázia...
      with open(CAMINHO_HISTORICO, "wt") as arquivo:
         arquivo.write(MODELO_VAZIO)

      import sys
      print(
         "BD dos histórico de comandos ainda não existe!",
         file= sys.stderr
      )
      exit()
   ...
...

from enum import (Enum, auto)

class Visualizacao(Enum):
   """
   fiz um enum para os tipos, pois futuramente também haverá uma versão
   gráfica do 'desligamento'.
   """
   MODO_TEXTO = auto()
   NCURSES = auto()

   @staticmethod
   def parse(texto: str):
      (enumerador, variedade) = texto.split('.')
      if enumerador.lower() == "visualizacao":
         if variedade == "ncurses":
            return Visualizacao.NCURSES
         elif variedade.lower() == "modo_texto":
            return Visualizacao.MODO_TEXTO
         else:
            raise AttributeError("não existe tal tipo de 'membro'.")
      ...
      raise ValueError("a string passada não é do tipo 'Visualizacao'")
   ...
...

def carrega_modo() -> Visualizacao:
   "apenas carrega o tipo de visualização do programa atualmente."
   try:
      with open(CAMINHO_HISTORICO, "rt") as arquivo:
         dicio = load(arquivo)
         if chave in dicio:
            return dicio[CHAVE_VISUALIZACAO]
         else:
            return None
      ...
   except FileNotFoundError:
      if __debug__:
         print("como o arquivo não existe, está sendo criado um...")
      # colocando uma lista vázia...
      with open(CAMINHO_HISTORICO, "wt") as arquivo:
         arquivo.write(MODELO_VAZIO)

      import sys
      print(
         "BD dos histórico de comandos ainda não existe!",
         file= sys.stderr
      )
      exit()
   ...
...

def extrai_modo(comando: str) -> Visualizacao:
   """
   pega o comando, e vê se ele demando a visualização em texto ou
   semi-gráfica(usando o ncurses)
   """
   if "--modo-texto" in comando:
      return Visualizacao.MODO_TEXTO
   else:
      return Visualizacao.NCURSES
...

def grava_historico(novos: Sequence[str]) -> bool:
   # não grava valores inválidos ou listas vázias.
   if (novos is None) or (len(novos) == 0):
      return False

   # carrega para incrementar.
   antigo_conteudo = carrega_historico()

   if __debug__:
      print("conteúdo carregado =", antigo_conteudo)

   comando = novos[0]
   novos.extend(antigo_conteudo)
   estrutura = {
      "modo_de_visualização": str(extrai_modo(comando)),
      "histórico": novos
   }

   with open(CAMINHO_HISTORICO, "wt") as arquivo:
      dump(estrutura, arquivo, ensure_ascii=False, indent=True)
      return True
   ...
   return False
...

from correcao import conserta_comandos
from unittest import (TestCase, main, skip)

class Teste(TestCase):
   def visualizacao_do_enum(self):
      for x in Visualizacao: print(x)

   @skip("foi inicialmente feito apenas para visualiza um input inicial.")
   def carrega_modo_inicialmente(self):
      resultado = carrega_modo()
      print(resultado)
      self.assertTrue(resultado is None)
   ...

   def extrai_modo_de_visualizacao(self):
      for registro in carrega_historico():
         tipo_de_enum = extrai_modo(registro)
         print("'%s'\n\t\t==>%s\n" % (registro, tipo_de_enum))
      ...
   ...

   def ajeitando_antigos_comandos_passados(self):
      todos = carrega_historico()
      conserta_comandos(todos)
   ...
...

