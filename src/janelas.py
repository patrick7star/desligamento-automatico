
# o que será importado.
__all__ = ["JanelaDebug", "Janela"]

from threading import Thread
from curses import (
   init_pair, init_color, napms, endwin,
   use_default_colors, start_color, 
   initscr, curs_set, COLOR_RED, COLOR_YELLOW,
   COLOR_GREEN, A_BLINK, A_ITALIC, cbreak
)
# criando uma janela à partir da versão
# 'debug', deveria ter sido o inverso, mas 
# enfim. Está contém threading, portanto
# executas buscas, impressões e etc,
# indepedente se foi chamada para fazer tal.
class Janela(Thread):
   " para série de testes "

   # taxa padrão para atualização de 'quadros'
   TAXA_PADRAO = 800 #milisegundos.

   def __init__(self, segundos, taxa_atualizacao, 
   automatico=False, rotulo=None) -> None:
      # construindo uma 'daemon thread'.
      Thread.__init__(self, daemon=True) 
      # confirmação para executar tal objeto como 'thread'.
      self._atualizacao = automatico 
      # taxa de atualização dos quadros da janela.
      if taxa_atualizacao is None:
         self._taxa = Janela.TAXA_PADRAO / 1000
         # só inicia se for exigido.
      else:
         self._taxa = taxa_atualizacao
      if segundos > 20 or segundos < 0.5:
         # para pegar as codificações antigas.
         raise OverflowError(
            "mais de 20seg não é permitido"
            +", ou menos que meio segundo"
         )
      ...
      # converte o tempo passado em segundso
      # para miliseg.
      self._tempo_limite = int(segundos * 1_000)
      self._janela = initscr()
      # sua configuração:
      start_color()
      use_default_colors()
      curs_set(0)
      # adicionado captura de tecla.
      cbreak()
      self._janela.nodelay(True)

      # novas cores.
      init_color(18, 0, 255, 17)
      VERDE_ESCURO = 18 # Bom!
      # paletas de cores.
      init_pair(99, COLOR_GREEN, -1)
      init_pair(98, COLOR_YELLOW, -1)
      init_pair(97, COLOR_RED, -1)
      init_pair(96, VERDE_ESCURO, -1)

      # põe um rótulo, seja a primeira vez, ou
      # com execuções continuas, por demanda.
      if rotulo is None:
         self._marca_dagua_ativada = False
      else:
         self._marca_dagua_ativada = True
         self._rotulo = rotulo
         # primeira gravura de marca d'água.
         self._marca_dagua(self._rotulo)
      ...
   ...

   # encerra programa semi-gráfico.
   def encerra(self):
      napms(self._tempo_limite)
      endwin()
   ...

   def referencia(self):
      return self._janela
   ref = property(referencia, None, None, None)

   # método formal de limpesa da 'tela'.
   def limpa(self):
      if hasattr(self, "_ciclos"):
         # contabiliza upgrades de tela.
         self._ciclos += 1
      else:
         self._ciclos = 0
      self._janela.erase()
      if self._marca_dagua_ativada:
         self._marca_dagua(self._rotulo)
   ...

   # congela limpa de janela por algum tempo.
   def congela(self, segundos):
      # não permitido mais de 3segs e menos de 1/5seg.
      if segundos >= 3 or segundos < 0.2:
         # para pegar as codificações antigas.
         raise OverflowError(
            "mais de 3seg não é permitido"
            +", ou menos que 1/5 de segundo"
         )
      ...
      # conversão em segundos.
      t = int(segundos * 1000)
      napms(t)
   ...

   # mostrando que está no modo debug.
   def _marca_dagua(self, mensagem):
      # ciclos do loop infinito.
      (y, x) = self._janela.getmaxyx()
      X = x - len(mensagem) - 2
      Y = y - 2
      self._janela.addstr(
         Y, X, mensagem,
         A_BLINK | A_ITALIC
      )
   ...

   def dimensao(self):
      return self._janela.getmaxyx()

   def run(self): 
      # sai disso, se não tiver dado
      # permissão para tal.
      while self._atualizacao:
         self._janela.refresh()
         self.congela(self._taxa)
         self.limpa()
      ...
   ...
   def __del__(self):
      self.encerra()
   '''
   def __getattribute__(self, atributo):
      print("atributo:", atributo)
      if atributo in ("addch", "addstr"):
         object.__getattribute__(self._janela, atributo)
      else:
         object.__getattribute__(self, atributo)
   ...'''
...

class JanelaDebug(Janela):
   """
   Janela especial para debug, com várias
   configurações limitadas.
   """
   def __init__(self) -> None:
      Janela.__init__(self, 3.5, 0.8, rotulo="modo debug")
      # comprimento do rótulo
      self._comprimento = len(self._rotulo)
      self._rotulo += "(%0.1fseg)" % (self._tempo_limite/1000)
   ...
   def aumenta_tempo_limite(self, novo: float):
      if novo <= 14:
         self._tempo_limite += int(novo * 1000)
         self._rotulo = (
            "%s(%0.1fseg)" % (
            self._rotulo[0:self._comprimento],
            self._tempo_limite/1000)
         )
   ...
...
   

from unittest import (TestCase, main, skip, skipIf)
from progresso import (BarraProgresso, Direcao, Ponto)
from os import get_terminal_size
from random import randint
from queue import SimpleQueue
from utilitarios.src.tempo import Temporizador

class JanelaComum(TestCase):
   def novaJanela(self):
      janela = Janela(1.5, rotulo="normal", taxa_atualizacao=0.5)
      janela.start()
      #info_de_tempo(janela.ref, "30seg")
      (_, L) = janela.dimensao()
      barra_geral = BarraProgresso(
         janela.ref, altura=6,
         largura=int(L * 0.70)
      )
      barra_minuto = BarraProgresso(
         janela.ref, altura=3,
         largura=int(L * (0.70**2)),
         mais_cores=True
      )

      # ajustando as barras.
      barra_geral.centraliza()
      barra_geral.desloca(Direcao.CIMA, 4)
      barra_geral.anexa(Direcao.BAIXO, barra_minuto)
      # temporizadores para cada barra.
      contador_reverso = Temporizador(30)
      contador_reversoI = Temporizador(10)

      while contador_reverso():
         # resetando o contador da barra-minuto.
         if not contador_reversoI():
            contador_reversoI = Temporizador(10)
         #info_de_tempo(janela.ref, "30seg")
         # preenchendo apenas para visualização.
         pBG = 1.0 - contador_reverso.percentual()
         pBM = 1.0 - contador_reversoI.percentual()
         barra_minuto.preenche(pBM)
         barra_geral.preenche(pBG)
         # renderização...
         barra_geral(); barra_minuto()
         janela.congela(0.6)
         # apagando tudo para reescreve novamente.
         janela.limpa()
      ...
      janela.encerra()
   ...
   class LoopContinuo:
      """
       pega várias instruções, está sendo tuplas
       com a quantidade de movimento para tal 
       direção, e a própria 'Direção' também.
       Executa-se tais instruções, na ordem dada
       que é esquerda para direita na lista,
       baseado na quantia demandada, e quando 
       terminar todas elas, recomeça a instruções
       novamente.
      """
      def __init__(self, instrucoes):
         # as instrunções têm que ser válidas
         # tipo, um inteiro e a direção que é
         # para fazer.
         os_argumentos_sao_validos = (
            # todos argumentos tem que ser 'legítimos'.
            all(
               map(lambda t:
                  # verifica se é uma tupla.
                  (type(t) is tuple)
                  # se a tupla tem apenas dois objetos nela.
                  and (len(t) == 2)
                  # se o primeiro é um 'inteiro'
                  and (type(t[0]) is int)
                  # e o segundo é uma 'Direção'.
                  and (type(t[1]) is Direcao),
               instrucoes)
            )
         )
         if (not os_argumentos_sao_validos):
            raise ValueError("revise os argumentos passados")
         # atual instrução.
         self.fila_de_instrucoes = SimpleQueue()
         for (n, d) in instrucoes:
            for _ in range(n):
               self.fila_de_instrucoes.put(d)
         ...
      ...
      def __call__(self) -> Direcao:
         if (not self.fila_de_instrucoes.empty()): 
            # pegando o primeiro elemento e,
            # jogando no final da fila novamente.
            remocao = self.fila_de_instrucoes.get()
            self.fila_de_instrucoes.put(remocao)
            return remocao
         ...
      ...
   ...

   def atualizacaoAutomatica(self):
      janela = Janela(
         0.8, automatico=True,taxa_atualizacao=0.5, 
         rotulo="ativando parametro 'automatico'"
      )
      janela.start()

      timer = Temporizador(58.6)
      (limite_vertical, limite_horizontal) = janela.dimensao()
      (x, y) = (0, 0)

      # repete tais instrunções continuamente.
      loop = JanelaComum.LoopContinuo([
         (limite_vertical-1, Direcao.BAIXO),
         (6, Direcao.DIREITA), 
         (limite_vertical-1, Direcao.CIMA),
         (9, Direcao.DIREITA), 
      ])

      while timer():
         match loop():
            case Direcao.CIMA:
               y -= 1
            case Direcao.BAIXO:
               y += 1
            case Direcao.DIREITA:
               x += 1
            case Direcao.ESQUERDA:
               x -= 1
         ...
         janela.ref.addch(y, x, '@')
         janela.ref.refresh()
         janela.congela(janela._taxa)
         janela.limpa()
      ...
      janela.encerra()
   ...
...

if __name__ == "__main__":
   main(verbose=1)
