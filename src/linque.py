"""
  Quando executado qualquer vez, verifica se há um linque válido deste 
programa no repositório padrão de linques, se não houver algum cria, se 
houver um quebrado(lique a script errado), então conserta ele.
"""
# O que será exportado?
__all__ = [
   "cria_linque_do_script", 
   "caminho_do_projeto_do_programa",
   "caminho_do_script"
]

# Biblioteca padrão do Python:
from os import (symlink, getenv, abort)
from pathlib import (PosixPath, )
from sys import argv as Argumentos

# Tenta criar linque com nome do programa para o arquivo no "repositório"
# de linques de programas codificados:
DIR_LINQUES = PosixPath(getenv("HOME"), ".local/usr/bin")
MSG_ERROR = "Não é possível prosseguir com o teste"
NOME_DO_LINQUE = "desligamento"
# Computa o caminho do linque deste programa.
if DIR_LINQUES is None:
   print("O diretório de linques compartilhados $LINKS não existe.")
   sleep(4); abort()
else:
   CAMINHO_LINQUE = PosixPath(DIR_LINQUES, NOME_DO_LINQUE)


def caminho_do_projeto_do_programa() -> PosixPath:
   """
     Assumindo que, tal programa estará no subdiretório 'src', dentro de 
   um diretório 'my_project', esta função retornará o caminho até 
   'my_project'. 
   """
   caminho_str = Argumentos[0]
   caminho = PosixPath(caminho_str).resolve()

   return caminho.parent.parent

def caminho_do_script() -> PosixPath:
   """
     Entrega o caminho do arquivo de script de python que está sendo 
   executado no momento. Basicamente o algoritmo pega a primeira linha 
   dado ao interpletador, e resolve o caminho se for algum relativo.
   """
   dir_projeto = caminho_do_projeto_do_programa()
   return dir_projeto.joinpath("src","main.py")

def cria_linque_do_script() -> None:
   """ 
     O algoritmo consiste no seguinte: verifica se tal linque existe, se 
   não, então será criado um linque para determinado 'executável'; caso 
   não, então verifica se aponta para executável, se sim, o fluxograma de
   decições acaba aqui; caso não, então é preciso fazer o linque apontar 
   para ele.
   """
   if CAMINHO_LINQUE.exists():
      pass 
   else:
      script = caminho_do_script()
      linque = PosixPath(DIR_LINQUES, NOME_DO_LINQUE)

      try:
         symlink(script, linque)

      except FileExistsError:
         if not linque.exists():
            print("Não está lincando o 'script' certo, portanto...")
            linque.unlink()
            linque.symlink_to(script)

         else:
            print("O linque já existe em '%s'." % DIR_LINQUES)


