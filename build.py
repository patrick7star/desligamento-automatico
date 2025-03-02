#!/bin/python3 -OO
"""
  No momento, tal script serve apenas para gerar o manifesto de todos 
arquivos, excluindo o diretório de dados, e subdiretórios de cache que 
a própria linguagem gera; isso porque muitos arquivos descontinuados ficam
ainda pois o GitHub não é o ponto central de produção destas aplicações -- 
pelo contrário, raramente são subidas algumas modificações -- logo, se não 
for excluído lá, tais arquivos continuam sendo baixados e replicados. 

  Já no futuro, é bem provavelmente as capilaridades de tal script, com um
nome bem forte, serão aumentadas.
"""
from pathlib import (PosixPath)
from glob import (glob as Glob)
import unittest
from os import (getenv)
from subprocess import (Popen)


# === === === === === === === === === === === === === === === === === === =
#                Processo de Criação do Manifesto 
# === === === === === === === === === === === === === === === === === === = 
def todos_dirs_e_files_do_diretorio() -> set[PosixPath]:
   diretorio_do_programa = PosixPath.cwd()
   coletado = set([])
   tentativas_de_padroes = [
      "./*", "./*/*", "./*/*/*/", 
      "./*/*/*/*", "./*/*/*/*/*.txt"
   ]

   if __debug__:
      print("caminho:", diretorio_do_programa)

   for pattern in tentativas_de_padroes:
      L = {PosixPath(p) for p in Glob(pattern)}
      coletado = coletado.union(L)

   assert (isinstance(coletado, set))
   return coletado

def filtra_diretorios_de_dados_e_cache(bolsa: set) -> None:
   "Varre a lista e exclui seleção de diretórios e arquivos."
   exclusao = []

   for path in bolsa:
      componentes = path.parts

      if "data" in componentes:
         exclusao.append(path)
      elif "__pycache__" in componentes:
         exclusao.append(path)
   
   if __debug__:
      print("\nO que achamos?")
      for e in exclusao:
         print('\t\b\b\b\b- ', e)
      print('')

   for item in exclusao:
      bolsa.remove(item)

def cria_manifesto_em(diretorio: PosixPath) -> None:
   NOME = "MANIFESTO.txt"
   destino = diretorio.joinpath(NOME)

   conteudo = todos_dirs_e_files_do_diretorio()
   filtra_diretorios_de_dados_e_cache(conteudo)
   conteudo_ordenado = sorted(conteudo)

   arquivo = open(destino, "wt")
   for item in conteudo_ordenado:
      linha = str(item) + '\n'
      arquivo.write(linha)
   arquivo.close()

# === === === === === === === === === === === === === === === === === === =
#                 Instalação de Ambiente e Bibliotecas
# === === === === === === === === === === === === === === === === === === = 
def construcacao_de_biblioteca_virtual_pra_terceiros() -> None:
   PY_EXE   = "/usr/bin/python3"
   NOME_LIB = "alicepylibs"
   caminho  = PosixPath(getenv("PYTHON_CODES"), NOME_LIB)

   if not caminho.exists():
      comando = Popen([PY_EXE, "-m", "venv", caminho])
      if __debug__:
         print("Comando:", comando)
      saida = comando.wait()
      assert (saida == 0)
   else:
      print("Biblioteca já existe no repositório local!")

def instala_dependencias_requisitadas() -> None:
   RAIZ = getenv("PYTHON_CODES")
   LOCAL_LIB = getenv("PYTHON_LOCAL_LIB")
   EXECUTAVEL = "{}/bin/pip".format(LOCAL_LIB)
   DEPS_ARQ = "requirements.txt"

   with open(DEPS_ARQ, "rt", encoding="latin1") as streaming:
      for dependencia in streaming:
         partes = dependencia.split("==")
         programa = partes[0]
         comando = Popen([EXECUTAVEL, "install", programa])

         print("Comando a ser executado: '%s'" % str(comando))
         assert (comando.wait() == 0)

def processo_de_instacao_de_dependencias() -> None:
   construcacao_de_biblioteca_virtual_pra_terceiros()
   instala_dependencias_requisitadas()


# === === === === === === === === === === === === === === === === === === =
#              Execução do Proposito Geral do Script
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- - 
#   Aqui, todas as instruções criadas, e testadas no script, serão então
# executadas na ordem de codificação.
# === === === === === === === === === === === === === === === === === === = 
if __name__ == "__main__":
   caminho = PosixPath.cwd()
   mensagem = """Criando arquivo manifesto em '{:s}'. Espera-se que tenha
   \rsido removido antes todos códigos desnecessários, caso contrário eles
   \rserão gerados juntos. """

   print(mensagem.format(str(caminho)))
   cria_manifesto_em(caminho)
   print("\n\nInstalações de dependências do programa:")
   instala_dependencias_requisitadas()

# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- - 
#   Mesmo o script de 'buildup' tem que ter seus testes unitários durante
# seu desenvolvimento.
# === === === === === === === === === === === === === === === === === === = 
class Testes(unittest.TestCase):
   def varredura_sem_qualquer_filtro(self):
      output = todos_dirs_e_files_do_diretorio()

      for path in output:
         print('\b\b\b\b\t- ', path)
         print("Total de caminhos:", len(output))

   def aplicacao_do_primeiro_filtro(self):
      out = todos_dirs_e_files_do_diretorio()
      print("Total de caminhos:", len(out))
      filtra_diretorios_de_dados_e_cache(out)
      print("Total de caminhos:", len(out))

   def criando_manifesto_de_teste(self):
      cria_manifesto_em(PosixPath("data"))

   @unittest.skip("Modifica muita coisa importante")
   def instalacao_de_dependencias_no_requirements(self):
      instala_dependencias_requisitadas()

   @unittest.skip("Modifica muita coisa importante")
   def cria_ambiente_para_biblioteca(self):
      construcacao_de_biblioteca_virtual_pra_terceiros()
