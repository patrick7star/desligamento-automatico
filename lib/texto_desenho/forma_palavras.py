# meus módulos:
if __name__ == "__main__":
   from biblioteca.utilitarios import (
      mescla_matrizes, 
      letra_desenho, 
      numero_desenho
   )
   from biblioteca.moldura_str import imprime
else:
   if __debug__:
      print("\nfile: '%s'\n" % __file__)
   try:
      from .biblioteca.utilitarios import (
         mescla_matrizes, 
         letra_desenho, 
         numero_desenho
      )
      from .biblioteca.moldura_str import imprime
   except ImportError:
      from biblioteca.utilitarios import (
         mescla_matrizes, 
         letra_desenho, 
         numero_desenho
      )
      from biblioteca.moldura_str import imprime
   ...
...
      
   
# biblioteca do Python:
import os, math, copy


# o que pode ser importado.
__all__ = [
   "forma_palavras", "forma_texto",
   "PalavraNaoCabeErro", "forma_string",
   "CENTRO","DIREITA", "ESQUERDA"
]

# váriaveis de alinhamento.
(ESQUERDA, CENTRO, DIREITA) = (1, 2, 3)

# exceções do programa.
class PalavraNaoCabeErro(Exception):
   """ a palavra é grande demais para a atual
   dimensão(largura do terminal). Pega a
   palavra e mostra qual/quais não cabem, e
   o quão falta de tela no terminal para ser
   possível produzir. """
   def __init__(self,largura_term, palavra):
      self.L_TERM = largura_term
      self.acrescimo_ideal = abs(len(palavra[0])-largura_term)+1
      ...
   def __str__(self):
      return ("\npalavra não pode ser impressa, ou ajustada\n"+
             "de acordo com a atual LARGURA do terminal\n"+
             "é preciso redimensionar %i colunas para caber"
             %self.acrescimo_ideal)


def ajusta_string(string):
   """ transforma frase da string numa 
   versão desacentuado; o retorno é está
   versão e, também maiúscula. """
   # converte para minúsculo e, separa
   # cada letra da string.
   letras = list(string.lower())

   # troca vogais acentuadas, e algumas 
   # consoantes por algo não acentuado.
   for (indice, l) in enumerate(letras):
      l = ord(l)
      # letra A:
      if  0xe0 <= l <= 0xe6: 
         letras[indice] = 'a'
      elif 0xe8 <= l <= 0xeb:
         letras[indice] = 'e'
      elif 0xec <= l <= 0xef:
         letras[indice] = 'i'
      elif 0xf2 <= l <= 0xf6:
         letras[indice] = 'o'
      elif 0xf9 <= l <= 0xfc:
         letras[indice] = 'u'
      else:
         if 0xe0 <= l <= 0xff:
            if l == 0xf1:
               letras[indice] = 'n'
            elif l == 0xe7:
               letras[indice] = 'c'
            else:
               raise Exception("letra incompátivel!")
 
   # forma string novamente.
   _str = ""
   for l in letras: _str += l
   # retorna a versão maiúscula, porém
   # agora desacentuada.
   return _str.upper()

def filtra_palavras(string):
   """ dada uma string, contendo tudo tipo
   de coisa que pode haver, a função retorna
   uma lista contendo apenas palavras que 
   forma tal string. """
   # parte primeiramente baseado nos espaços
   # em branco.
   palavras = string.split(' ')

   # verifica se alguma palavra termina com
   # quebra de linha, e a remove.
   for I,p in enumerate(palavras):
      if p.endswith('\n') or p.startswith('\n'):
         palavras[I]=palavras[I].replace('\n','')

   # verifica se há espaços em brancos incompátiveis.
   while palavras.count('') > 0:
      palavras.remove('')
   return palavras

def forma_string(string):
   """ pega uma string "junta", quero dizer:
   mostra apenas uma palavra, não espaços no 
   meio; e expressa-a inteiramente na forma de 
   desenho de caractéres. Claro, ela precisa 
   ser alfonumérica(ascii), ou seja, ter valores 
   ascii e números. Não são aceitos ainda outros 
   caractéres especiais. Um modo também de
   terceirizar um pouco do código deste tipo de 
   função que cuida de várias palavras, e não 
   apenas uma. """
   # string apenas maiúsculo, pois 
   # o programa só aceita este tipo
   # de caractére, também desacentua
   # cada letra assim, na frase.
   string = ajusta_string(string)

   # lista com letras a formar baseado no desenho
   # de caractéres que a representa, e, concatena-las.
   lista_letras = []
   for char in string:
      if char.isascii() and char.isalpha():
         lista_letras.append(letra_desenho(char))
      elif char.isdigit():
         lista_letras.append(numero_desenho(int(char)))
      else: pass 

   # mescla palavra, nova função, está leva
   # em consideração números também.
   return mescla_matrizes(*lista_letras)

def forma_palavras(string):
   """ retorna uma lista contendo matrizes
   representando palavras construídas por 
   caractéres alfanuméricos. """
   # separa palavras.
   palavras = filtra_palavras(string)
   # caso haja apenas uma palavra apenas.
   if len(palavras) == 1:
      return mescla_matrizes(palavras[0])

   elif len(palavras) == 0:
      # levanta uma exceção, falando que 
      # a string provavelmente está vázia.
      raise Exception("nenhuma palavra foi adicionada!")

   else:
      # caso haja muitas palavras...
      # lista com todas palavras formadas.
      lista = []
      for p in palavras:
         lista.append(forma_string(p))
      # retorna a lista com as matrizes representando
      # cada palavras, sendo estas uma funsão de
      # letras-desenho.
      return tuple(lista)

def forma_texto(palavras, alinhamento=ESQUERDA):
   """ pega todas matrizes representando palavras,
   e mescla-as de forma inteligente respeitando
   as bordas do terminal. """
   # quantidade de caractéres que o terminal
   # está dimensionado.
   colunas_max = os.get_terminal_size().columns
   # matriz representando os espaços, será
   # mesclado para separar palavras. Tem 
   # três espaços de separação, e altura
   # de uma das palavras, mesmo sendo irrelevante
   # ressaltar tal, já que todas, porque as letras
   # são assim... têm a mesma altura.
   espaco = [[' ']*3]*len(palavras[0])
   linhas, indice = {}, 1

   # computa a quantia de colunas de uma matriz.
   def qtd_colunas(M): return len(M[0])

   # começa da primeira palavra.
   atual = palavras[0]
   for P in palavras[1:]:
      # verificando se palavra cabe no terminal.
      if len(P[0]) >= colunas_max:
         raise PalavraNaoCabeErro(colunas_max, P) 

      # P para quantidade total de colunas na
      # palavra; três é o números de colunas 
      # do espaço adicionado; atual é a qtd.
      # de todo o texto da linha.
      colunas_em_linha = qtd_colunas(P)+4+qtd_colunas(atual)
      if colunas_em_linha < colunas_max:
         atual = mescla_matrizes(atual, espaco, P)
      else:
         atual = P # engancha nesta, esquece a outra.
         indice += 1 # muda para à próxima linha.
      # copia para o dicionário, dado o índice
      # definido, ou seja, a linha.
      linhas[indice] = atual
      # para debug.
      #ativa_grade(linhas[indice])
   if alinhamento == DIREITA:
      return ajusta_a_direita(linhas)
   elif alinhamento == CENTRO:
      return centraliza_texto(linhas)
   elif alinhamento == ESQUERDA:
      return linhas
   else:
      aviso =("esta opção não existe, apenas:"+
              "\nDIREITA, CENTRO e ESQUERDA\n") 
      raise Exception(aviso)

def ativa_grade(P):
   altura, colunas = len(P), len(P[0])
   for i in range(altura):
      for j in range(colunas):
         if P[i][j].isspace(): P[i][j] = '¨'

def centraliza_texto(texto):
   """ pega o dicionário e, centraliza cada linha
   adicionando partes em brancos na linha até que
   o texto fico centralizado. """
   k = len(texto) # qtd. de linhas
   # quantidade de colunas da janela.
   maxX = os.get_terminal_size().columns
   # cópia do texto.
   TEXTO = copy.deepcopy(texto) 
   while k >= 1:
      # computa a quantia de colunas que precisará
      # ser preenchida para centralizar e tal.
      X = math.floor(abs(len(texto[k][0])-1 - maxX) / 2)
      #TEXTO[k] = copy.deepcopy(texto[k])
      linha = 0
      while linha < len(TEXTO[k]):
         # adiciona 'X' vezes espaço no começo.
         for q in range(X):
            TEXTO[k][linha].insert(0,' ')
         linha += 1
      k -= 1
   return TEXTO

def ajusta_a_direita(texto):
   k = len(texto) # qtd. de linhas
   # quantidade de colunas da janela.
   maxX = os.get_terminal_size().columns
   # cópia do texto.
   TEXTO = copy.deepcopy(texto) 
   while k >= 1:
      # computa a quantia de colunas que precisará
      # ser preenchida para colocar à direita.
      X = abs(len(texto[k][0]) - maxX)-1
      linha = 0
      while linha < len(TEXTO[k]):
         # adiciona 'X' vezes espaço no começo.
         for q in range(X):
            TEXTO[k][linha].insert(0,' ')
         linha += 1
      k -= 1
   return TEXTO


if __name__ == '__main__':
   from biblioteca.textos_para_teste import *
   
   def teste_de_forma_palavras():
      for frase in [nome, poemaI, poemaII]:
         for palavra in forma_palavras(frase):
            imprime(palavra)
      ...
   ...

   def teste_forma_texto():
      forma_texto(forma_palavras("o homem lobo"))
      
      palavras_repatidas = forma_palavras(poemaII)
      for X,Y in forma_texto(palavras_repatidas).items():
         imprime(Y)

      for linha in forma_texto(forma_palavras(texto)).values():
         imprime(linha)
   ...

   def teste_de_forma_string():
      imprime(forma_string("playoff"))
      imprime(forma_string("maçã"))
      imprime(forma_string("VOCÊ"))
      imprime(forma_string("código666"))
   ...
   
   teste_forma_texto()
   teste_de_forma_string()
   teste_de_forma_palavras()
...
