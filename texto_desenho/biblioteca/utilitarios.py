# módulos da biblioteca padrão Python:
from os.path import dirname, join as Join
from os import listdir
from copy import deepcopy, copy
import string
# minha biblioteca:
from .moldura_str import matriciar, imprime


# Um dicionário que contém todos as letras 
# e números na memória, para que não precise 
# ler em disco em cada chamada para uma nova 
# letra/número, pois tal consulta é lenta.
algs_e_mais = {} # vázia inicialmente.
alfabeto = {} # vázia inicialmente.
# o caminho para o diretório contendo 
# números, acrônimos e outros símbolos 
# desenhados com caractéres.
def ajusta_path(caminho):
   arquivo_path = __file__
   while not arquivo_path.endswith("texto_desenho"):
      arquivo_path = dirname(arquivo_path)
   return Join(arquivo_path, caminho)
...
caminho_numeros = ajusta_path(r'símbolos/números')
caminhos_acron = ajusta_path(r'símbolos/acronimos')
caminho_outros = ajusta_path(r'símbolos/')
caminho_letras = ajusta_path(r'símbolos/alfabeto/')

# exceções para erros específicos:
class CaractereNaoExisteErro(Exception):
   """
   alerta que o caractére, ou símbolo passado
   não tem nenhum desenho para sua representação
   ainda, ou permanentemente.
   """
   def __init__(self, C): 
      self.caractere = C
   def __str__(self):
      string = (
        "\no caractére \"%s\" não tem desenho específico\n"+
        "para sua representação, então remova,\n"+
        "ou implemente-o."
      )
      return string%self.caractere
   ...
...


def numero_desenho(numero):
   """
   retorna uma matriz contendo a representação 
   em texto do algarismos passado.
   """
   # se for a primeira vez de acesso, então
   # obter dados do disco, e gravar também 
   # na memória.
   global algs_e_mais
   if numero not in algs_e_mais:
      # proposições:
      if type(numero) == int and (numero >= 0 and numero <= 9):
         if numero == 0:
            numero_str = 'zero.txt'
         elif numero == 1:
            numero_str = 'um.txt'
         elif numero == 2:
            numero_str = 'dois.txt'
         elif numero == 3:
            numero_str = 'três.txt'
         elif numero == 4:
            numero_str = 'quatro.txt'
         elif numero == 5:
            numero_str = 'cinco.txt'
         elif numero == 6:
            numero_str = 'seis.txt'
         elif numero == 7:
            numero_str = 'sete.txt'
         elif numero == 8:
            numero_str = 'oito.txt'
         else:
            numero_str = 'nove.txt'

         caminho = Join(caminho_numeros, numero_str)
         with open(caminho, 'rt') as arq:
            dados = matriciar(arq.read())
            algs_e_mais[numero] = dados
            return dados
         ...
      ...
   else:
      return algs_e_mais[numero]
...

def letra_desenho(letra):
   """
   retorna uma matriz contendo a representação
   em texto da letra passada.
   """
   # carrega letra na memória apenas se requisitida.
   if letra in string.ascii_uppercase:
      nome_arq = letra+'.txt'
      novo_caminho = Join(caminho_letras,nome_arq)
      with open(novo_caminho,'rt') as arquivo:
         alfabeto[letra] = matriciar(arquivo.read())
   ...

   if letra.isalpha():
      return alfabeto[letra]
   else:
      raise CaractereNaoExisteErro(letra)
...

def mescla_matrizes(*matrizes):
   """ 
   Pega matrizes representa uma figura, neste
   caso letras alfabéticas e, junta elas numa
   mesma matriz parecendo que no final todas estão
   numa mesma linha; o retorno é a matriz combinada.
   """
   # cópia de todas matrizes, porque serão alteradas.
   matrizes = deepcopy(matrizes)
   igualiza_matrizes(matrizes)
   # cópia de primeira.
   geral = deepcopy(matrizes[0]) 
   # cálcula da matriz "com maior altura", ou
   # seja, número de linhas, e também o "mais
   # largo"(com maior número de colunas).
   colunas = []
   for M in matrizes:
      colunas.append(max(len(linha) for linha in M))
   colunas = sum(colunas)+len(matrizes)

   # junta com as demais.
   for M in matrizes[1:]:
      for (i, linha) in enumerate(M):
         try:
            # dando espaço entre as letras.
            geral[i].extend([' '])
            geral[i].extend(linha)
         except IndexError:
            geral.append([' '] * colunas)
            continue
         ...
      ...
   ...

   # corrigindo lacunas nas colunas.
   for linha in geral:
      if len(linha) < colunas:
         d = abs(len(linha)-colunas)
         linha.extend([' '] * d)
      ...
   ...

   # retorno da matriz geral mesclada.
   return geral
...

def igualiza_matrizes(matrizes):
   """ iguala as matrizes em altura; matrizes
   com número de linhas diferenciado, serão
   modificadas para se igualarem nisso; onde
   as com menos linhas, serão preenchidas com
   linhas em branco para atingir a "altura" 
   da matriz com maior linha"""
   # a maior "altura" entre as matrizes.
   max_h = max(len(M) for M in matrizes)
   t = len(matrizes) # quantia de matrizes.
   # percorre cada matriz para ajustar sua "altura".
   while t > 0:
      M = matrizes[t-1] # referência da matriz.
      if len(M) < max_h:
         linha_vazia = [' ']*len(M[0]) # espaco vázio.
         for k in range(abs(len(M)-max_h)):
            M.insert(0, copy(linha_vazia))
      ...
      t -= 1 # descontando já revisto.
   ...
...


# execução para testes:
if __name__ == '__main__':
   letra_A = letra_desenho('A')
   for L in ('A','U','W','K','X'):
      imprime(letra_desenho(L))

   letras=list(map(letra_desenho,tuple('savio'.upper())))
   imprime(mescla_matrizes(*letras))

   print("tamanho na memória:%4i bytes"%alfabeto.__sizeof__())

   letras=list(map(letra_desenho,tuple('queijo'.upper())))
   imprime(mescla_matrizes(*letras))

   letras=list(map(letra_desenho,tuple('quotation'.upper())))
   imprime(mescla_matrizes(*letras))

   letras=list(map(letra_desenho,tuple('baleia'.upper())))
   imprime(mescla_matrizes(*letras))
   letras=list(map(letra_desenho,tuple('dado'.upper())))
   imprime(mescla_matrizes(*letras))

   print("tamanho na memória:%4i bytes"%alfabeto.__sizeof__())

   nums = list(map(numero_desenho, (1,2,3,3,9,5,4)))
   imprime(mescla_matrizes(*nums))
