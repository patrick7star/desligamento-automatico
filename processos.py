
"""
   Tarefa simples de contabilizar o total
 de threads que estão sendo utilizadas
 pelo sistema. Assim como aparace no
 gerenciador de tarefas do Windows.

   O código é literalmente a cópia do que
 foi feito em Rust, com alguns retoques,
 que são mais apropriados no Python.
"""

# biblioteca padrão do Python.
from enum import (Enum, auto)
import os.path
from pathlib import Path

class Estado(Enum):
   "Todos os casos que um processo pode assumir"
   RODANDO = auto()
   PARADO = auto()
   DORMINDO = auto()
   PRESTE_A_RODAR = auto()
   NA_MEMORIA_SWAP = auto()

   @staticmethod
   def converte(info: str):
      if "running" in info:
         return Estado.RODANDO
      elif "sleeping" in info:
         return Estado.DORMINDO
      elif "stopped" in info:
         return Estado.PARADO
      elif "idle" in info:
         return Estado.PRESTE_A_RODAR
      elif "disk sleep" in info:
         return Estado.NA_MEMORIA_SWAP
      else:
         raise Exception("[%s]caso não existe!" % info)
   ...
...

class Processo:
   """
    Pega um caminho de alguma pasta de processo
   no Linux, geralmente em '/proc', e lê os dados
   mais importantes(alguns selecionados pessoalmente
   neste contexto, podem aumentar ou diminuir)
   para a aplicação aqui codificada.
   """
   # função auxiliar para o método construtor.
   @staticmethod
   def limpando_conteudo_arquivo(caminho: Path) -> iter:
      caminho = os.path.join(caminho, "status")
      # tem que existir tal caminho.
      assert os.path.exists(caminho)
      # abre arquivo e lê todas linhas, apenas
      # descartando comentários, e tudo mais que
      # não têm ':', ou seja, não está ligado a
      # uma variável.
      with open(caminho, "rt") as arquivo:
         linhas = arquivo.readlines()
         if __debug__:
            print("qtd. de linhas:",len(linhas))
         assert len(linhas) > 0
         # este 'closure' toma uma string, e remove 
         # todos seus espaços-brancos.
         retira = (
            lambda string_entrada: "".join(
               filter(
                  lambda char: 
                  not char.isspace(), 
                  string_entrada
               )
            )
         )
         # de volta ao começo do arquivo.
         arquivo.seek(0)
         # faz todo um processamento dos dados,
         # filtragem e ajustes, usando iteradores
         # seus adaptadores e funções anônimas.
         return map(
            # retira espaços-em-branco.
            lambda l: retira(l),
            # torna tudo minúsculo.
            map(
               lambda s: s.lower(),
               # pega apenas linhas com um separador
               # de variável-valor(:).
               filter (
                  lambda l: ':' in l,
                  arquivo.readlines()
               )
            )
         )
      ...
   ...

   # separa a chave do valor, sendo que tal valor
   # ainda está em string, porém é necessário ser
   # retornado assim.
   @staticmethod
   def campos_importantes(conteudo: iter) -> {str: str}:
      dicio: dict(str=str) = {}
      for l in conteudo:
         (chave, dado) = l.split(':', maxsplit=1)
         dicio[chave] = dado
      ...
      return dicio
   ...

   def __init__(self, caminho: Path):
      """
      apenas pega o mapa, e anexa a seus devidos
      atributos, escolhidos específicamente para
      aplicação, portanto podem aumentar quando
      for copiado para outro código.
      """
      # limpando conteúdo do arquivo e separando em
      # linhas, assim como fazendo uma organização
      # no que foi despejado.
      extracao = Processo.limpando_conteudo_arquivo(caminho)
      # campos importantes.
      mapa = Processo.campos_importantes(extracao)

      # simples conversão ao respectivos tipos.
      self._nome = mapa["name"]
      self._pid = int(mapa["pid"])
      self._pai = int(mapa["ppid"])
      self._estado = Estado.converte(mapa["state"])
      self._qtd_threads = int(mapa["threads"])
   ...

   def info(id: int) -> object:
      """
      cria uma instância, dando apenas o PID.
      Se ele não existir 'None' será retornado,
      caso contrário, a instância do 'Processo'.
      """
      caminho = os.path("/proc", str(id))
      if not os.path.exists(caminho):
         return None
      else:
         return Processo(caminho)
   ...
   def __str__(self) -> str:
      "visualização de tais para 'debug'."
      return "{pid:>5d}{nome}".format(
         nome=self._nome,
         pid=self._pid
      )
   ...
   def __del__(self) -> None:
      "encerra o programa, como acaba com sua instância"
      #kill(self._pid, signal.SIGTERM)
      print("o programa '%s' foi encerrado" % self._nome)
   ...
...

from os import listdir

def todos_processos() -> [Processo]:
   """
   Pega todos os 'processos' atuais no sistema,
   tenham permissão de manipular-lôs, ou não.
   Como os dados mais importantes sobre eles:
   n. de threads, pid, nome, estado e etc. Este,
   pode ser ampliado, na verdade eles são filtrados
   de, literalmente, uma dezenas de dados, estes
   que podem ser incorporados.
   """
   # verifica se os caminhos formados são
   # diretórios e existem.
   lista_de_diretorios = filter(
      lambda d: os.path.isdir(d) and os.path.exists(d),
      # pega conteúdo dentro do diretório
      # e concatena em algo provável de
      # ser um diretório.
      map(
         lambda e: os.path.join("/proc", e),
         # retira os diretórios que não
         # começam apenas com números.
         filter(
            lambda s: s.isnumeric(),
            listdir("/proc")
         )
      )
   )
   # cria instâncias, descarta os erros,
   # colocando tudo no fim numa lista.
   return list(
      filter(
         lambda r: r is not None,
         map(
            lambda pth: Processo(pth),
            lista_de_diretorios
         )
      )
   )
...

# série de testes para dá robustez ao programa.
# muitos já foram testados no código em Rust, porém
# como muda linguagem, e muda o modo de fazer-se
# algo, uma boa série de testes tem que ser
# refeitos, ou criados.
import unittest

class Funcoes(unittest.TestCase):
   def visualizacaoDaListagem(self):
      lista = todos_processos()
      if __debug__:
         print("elementos na lista:", len(lista))
      self.assertTrue(type(lista) == list)
      self.assertTrue(len(lista) > 0)
      for p in lista:
         print(p)
   ...
   def metodoLimpandoConteudoArquivo(self):
      caminho = "/proc/5271"
      extraido = Processo.limpando_conteudo_arquivo(caminho)
      for linha in extraido: print(linha)
   ...
   def visualizacaoDestruicao(self):
      lista = todos_processos()
...

class CodigosExperimentais(unittest.TestCase):
   def travessaDir(self):
      raiz = "/proc"
      Join = os.path.join
      iterador = map(
         lambda entrada: Join(raiz, entrada),
         listdir(raiz)
      )
      for pth in iterador:
         print(pth)
   ...
   def selecionaSoDirNumericos(self):
      raiz = "/proc"
      Join = os.path.join
      iterador = map(
         lambda entrada: Join(raiz, entrada),
         filter(
            lambda d: d.isnumeric(),
            listdir(raiz)
         )
      )
      for pth in iterador: print(pth)
   ...
   def combinacaoDoTodo(self):
      raiz = "/proc"
      Join = os.path.join
      Existe = os.path.exists
      UmDir = os.path.isdir
      iterador = filter(
         lambda d: Existe(d) and UmDir(d),
         map(
            lambda e: Join(raiz, e),
            filter(
               lambda s: s.isnumeric(),
               listdir(raiz)
            )
         )
      )
      for pth in iterador: print(pth)
   ...
   @unittest.skipIf(not os.path.exists("/proc/1/status"), 
   "o processo usado como exemplo tem que existir")
   def limpandoEspacosBrancos(self):
      retira = (
         lambda string_entrada: "".join(
            filter(
               lambda char: 
               not char.isspace(), 
               string_entrada
            )
         )
      )
      with open("/proc/1/status") as arquivo:
         # closure que retira espaços brancos.
         iterador = map(
            lambda l: retira(l),
            map(
               lambda s: s.lower(),
               filter(
                  lambda l: ':' in l,
                  arquivo.readlines()
               )
            )
         )
      for s in iterador: print(str(s))
   ...
...

if __name__ == "__main__":
   unittest.main()

# o que será importado.
__all__ = ("todos_processos", "Processo", "Estado")
