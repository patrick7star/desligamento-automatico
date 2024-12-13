
__all__ = {"conserta_comandos"}

from enum import Enum

class Parte(Enum):
   TEMPO = 9
   PROGRAMA = 9999
   ACAO = 999
   MODO_VIEW = 99

   def __lt__(self, outro) -> bool:
      "toda a hierarquia: tempo < modo < ação < programa"
      assert isinstance(outro, Parte)
      instancia = self
      return self.value < outro.value
   ...

   def __gt__(self, outro) -> bool:
      "toda a hierarquia: tempo < modo < ação < programa"
      assert isinstance(outro, Parte)
      return self.value > outro.value
...

def string_comeca_com_numeros(string: str) -> bool:
   contagem = 0
   for char in string:
      if char.isdigit() or char == '.':
         contagem += 1
      else:
         break
   ...
   return contagem > 0 and string[0] != '.'
...

def identifica_parte(s: str) -> Parte:
   # proposições:
   contem_peso = ( "min" in s or "seg" in s or "h" in s)
   tem_alguns_dos_modos = (lambda S:
      (
         ("modo-texto" in S) or
         ("ncurses" in S)
      )
   )
   tem_indicador_de_opcao = s.startswith("--")
   # função anômima que computa se ambos tem um comprimento próximo.
   comprimento_similiar = lambda s, l: abs(len(s) - len(l)) <= 2
   # tem uma 'ação' desejada.
   alguma_acao_mencionada = (
      (("desliga" in s) and comprimento_similiar(s, "desliga"))
                              or
      (("suspende" in s) and comprimento_similiar(s, "suspende"))
   )

   if contem_peso and string_comeca_com_numeros(s):
      return Parte.TEMPO
   elif tem_indicador_de_opcao and tem_alguns_dos_modos(s):
      return Parte.MODO_VIEW
   elif tem_alguns_dos_modos and alguma_acao_mencionada:
      return Parte.ACAO
   else:
      # qualquer outra deve ser considerada o nome do programa.
      return Parte.PROGRAMA
...

from pprint import pprint
from random import randint
from collections.abc import (Sequence)

# cada parte do retorno da função abaixo, com nomes mais amigáveis:
#Componente = tuple[str, Parte]
class Componente:
   def __init__(self, string: str, tipo: Parte) -> None:
      self.dado = string
      self.tipo_de_dado = tipo
   ...

   def __getitem__(self, indice: int):
      assert isinstance(indice, int)
      if indice == 0:
         return self.dado
      elif indice == 1:
         return self.tipo_de_dado
      else:
         raise IndexError("é uma 'tupla' com dois valores apenas!")
   ...

   def __iter__(self):
      self.contador = 0
      return self

   def __next__(self):
      if self.contador > 1:
         self.contador = 0
         raise StopIteration()
      ...
      novo_item = self[self.contador]
      self.contador += 1
      return novo_item
   ...

   def __repr__(self) -> str:
      string_tipo = str(self.tipo_de_dado).strip("Parte.")
      return ( "({}, {})".format(self.dado, string_tipo))
   ...
   def __str__(self) -> str:
      return "componente: " + str(self)

   def __lt__(self, outro) -> bool:
      assert isinstance(outro, Componente)
      return self.tipo_de_dado < outro.tipo_de_dado

   def __gt__(self, outro) -> bool:
      assert isinstance(outro, Componente)
      return self.tipo_de_dado > outro.tipo_de_dado

   @staticmethod
   def cria(string: str):
      if __debug__:
         print("feito via método estático!!!")
      return Componente(string, identifica_parte(string))
...

TodasPartes = Sequence[Componente]

def complementa(partes: Sequence[Componente]) -> TodasPartes:
   # tem que ter no mínimo uma parte(o programa).
   assert len(partes) >= 1

   # colocando os já mandados na array...
   completo = [p for p in partes]
   total = len(partes)
   um_minuto_aleatorio= lambda: str(randint(15, 59)) + "seg"
   # todas tuplas com as partes faltante, é impossível, e sucetível a 
   # erro se aparecer algo como 'PROGRAMA', por isso está de fora.
   ACAO_PADRAO = Componente("--desliga", Parte.ACAO)
   MODO_PADRAO = Componente("--ncurses", Parte.MODO_VIEW)
   TEMPO_PADRAO = Componente(um_minuto_aleatorio(), Parte.TEMPO)

   if __debug__:
      print("antes:", completo)

   # se houve apenas um comando é o script/ou o caminho até ele, logo os
   # demais devem ser adicionados(TEMPO, ACAO, MODO_VIEW): O 'ação' é 
   # o mais simples já que por toda execução deste programa sempre foi 
   # sobre 'desligar'. O 'modo' também é fácil, tal programa foi feito 
   # na base do ncurses, o "output de texto" foi adicionado posterior,
   # logo o original é o padrão. Já o 'tempo', o que não é especificado
   # é selecionado aleatóriamente, portanto, aqui também será; estamos
   # falando qualquer valor entre 10seg à 1min.
   possui = set(P[1] for P in partes)
   todos = set(Parte)
   restantes = todos - possui

   for tipo_de_parte in restantes:
      match tipo_de_parte:
         case Parte.ACAO:
            completo.append(ACAO_PADRAO)
         case Parte.MODO_VIEW:
            completo.append(MODO_PADRAO)
         case Parte.TEMPO:
            completo.append(TEMPO_PADRAO)
         case _:
            raise ValueError("não deve ter 'PROGRAMA', algum erro!!")
      ...
   ...

   if __debug__:
      print("depois:", completo)
   # tem que chegar aqui com tudo completo.
   # assert len(completo) == 4
   return sorted(completo, reverse=True)
...

def cria_componente(string: str) -> Componente:
   return Componente(string, identifica_parte(string))

def divide_em_componentes(string: str) -> Sequence[Componente]:
   return list(map(lambda s: Componente.cria(s), string.split()))


def decodifica_cmd(comando_str: str) -> str:
   """
   faz a seguinte quebra todas partes(os espaços) então cocatena o que 
   tem, e o que não tem na seguinte ordem: nome do programa, tipo de 
   interface, qual ação tomar.

   NOTA: admite que o comando passado é válido.
   """
   # realiza processamento inicial.
   produto = divide_em_componentes(comando_str)

   # se já estiver arrumado, apenas retorna-lô.
   if verifica_necessidade(produto):
      if __debug__: 
         print ("já está completo o comando '%s'" % comando_str)
      return comando_str

   # novo processamento de complementação do que falta e ordenação.
   novo_produto = complementa(produto)

   if __debug__:
      print("produto final:", novo_produto)

   return ' '.join(c[0] for c in novo_produto)
...

def conserta_comandos(todos_cmd: Sequence[str]) -> Sequence[str]:
   for comando in todos_cmd:
      novo_comando = decodifica_cmd(comando)
      print(
         "comando anterior: '{}'\ncomando reprocessado: '{}'\n"
         .format(comando, novo_comando)
      )
   ...
   return None
...

def verifica_necessidade(cmd: Sequence[Componente]) ->  bool:
   # tem que ter todos os quartro componentes.
   tem_todos_componentes = (len(cmd) == 4)
   if (not tem_todos_componentes): return False

   # todos tem que seguir está ordem, sem mais: ação, modo e o tempo.
   e_uma_acao = cmd[1].tipo_de_dado is Parte.ACAO
   eo_modo = cmd[2].tipo_de_dado is Parte.MODO_VIEW
   eo_tempo = cmd[3].tipo_de_dado is Parte.TEMPO

   return (eo_modo and e_uma_acao and eo_tempo)
...

from unittest import TestCase

class Teste(TestCase):
   def comparacao_do_enum(self):
      e1 = Parte.PROGRAMA
      e2 = Parte.TEMPO
      self.assertTrue(e1 > e2)
      self.assertTrue(Parte.ACAO > Parte.MODO_VIEW)
      self.assertTrue(not (Parte.TEMPO > Parte.MODO_VIEW))

      print(sorted(list(Parte), reverse=True))
   ...

   def novo_tipo_componente(self):
      c = Componente("main.py", Parte.PROGRAMA)
      print(c[0], c[1])
      print(list(c))
      try:
         print(c[2], c[3])
      except IndexError:
         print("pego o erro!")
         self.assertTrue(True)
      ...
   ...

   def comparacao_do_componente(self):
      lista = [
         Componente("3min", Parte.TEMPO),
         Componente("/usr/bin/desligamento", Parte.PROGRAMA),
         Componente("--desliga", Parte.ACAO)
      ]
      print(lista)
      print("ordenando ...")
      nova_lista = sorted(lista, reverse=True)
      print(nova_lista)
   ...

   def repara_comando_ja_completo(self):
      comando = "desligador --desliga --modo-texto 13min"
      print("atual comando: '%s'" % comando)
      print("comando consertado: '%s'" % decodifica_cmd(comando))
   ...

   def verificando_necessidade_de_correcao(self):
      from historico import carrega_historico
      historico = carrega_historico()

      for cmd in historico:
         componentes = divide_em_componentes(cmd)
         resultado = verifica_necessidade(componentes)
         print ("[{:^8s}] {}".format(str(resultado).lower(), cmd))
      ...
   ...
...
