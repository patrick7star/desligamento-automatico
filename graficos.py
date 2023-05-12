
"""
   Aqui cuida-se especificamente da parte
gráfica do programa. Sera feita no 'ncurses'
do Python especificamente.
"""

# biblioteca do Python:
import curses
# própria biblioteca:
from temporizador import (Temporizador, stringtime_to_segundos)
from texto_desenho.forma_palavras import forma_string
from utilitarios.src.legivel import tempo as ul_tempo


# constantes de personalização.
PROGRESSO_ATOMO = ' '

# o que será exportado:
__all__ = (
   "PROGRESSO_ATOMO",
   "inicia_grafico",
)


def inicia_grafico(timer):
   """ 
   a execução de todo o visual do programa,
   do seu arranjo de tela, até a animação 
   que ele toca.
   """ 
   janela = curses.initscr()
   # sua configuração:
   curses.start_color()
   curses.use_default_colors()
   curses.curs_set(0)

   # novas cores.
   curses.init_color(18, 0, 255, 17)
   VERDE_ESCURO = 18 # Bom!
   # paletas de cores.
   curses.init_pair(99, curses.COLOR_GREEN, -1)
   curses.init_pair(98, curses.COLOR_YELLOW, -1)
   curses.init_pair(97, curses.COLOR_RED, -1)
   curses.init_pair(96, VERDE_ESCURO, -1)

   #preenche_barra(janela, timer.percentual())
   janela.refresh()
   curses.napms(1500)

   # inclui contagem regressiva no minuto final.
   if __debug__:
      MEIA_HORA = 60 * 5 // 2
   else:
      MEIA_HORA = 3600 // 2
   barra_acionada = False
   outra_barra = timer > MEIA_HORA

   # importando aqui dentro, pois pode criar
   # algo circular, se feito na 'main thread'
   # do programa. Como tal função é chamada
   # apenas uma vez por execução, o custo 
   #computacional não será tão grande.
   from progresso import (Ponto, BarraProgresso, Direcao)
   global Ponto, BarraProgresso

   #desenha_barra(janela)
   (H, L) = janela.getmaxyx()
   largura_barra = int(L * 0.70)
   meio = Ponto((H-5)//2, (L-largura_barra)//2)
   barra = BarraProgresso(
      janela, posicao=meio,
      largura=largura_barra,
      altura=5
   )
   barraminuto = BarraProgresso(
      janela, altura=3,
      posicao=meio+Ponto(5, 0),
      largura = int(L * 0.70 * 0.70),
      mais_cores=True
   )
   # grava dimensão atual da janela.
   atual_dimensao = janela.getmaxyx()

   while timer():
      janela.clear()
      # texto piscante para dizer que nada no
      # sistema vai acontecer(desligamento).
      if __debug__:
         janela.addstr(2, 2, "debug mode", curses.A_BLINK)
         dimensao_str = "dimensão(H={} L={})".format(H, L)
         janela.addstr(
            2, L - len(dimensao_str) - 1,
            dimensao_str, curses.A_BLINK
         )
      ...

      # centraliza barra se necessário.
      if janela.getmaxyx() != atual_dimensao:
         barra.centraliza()
         # sem esquecer de uma possível outra barra.
         if outra_barra:
            barraminuto.centraliza()
            # retirando de cima da outra...
            barraminuto.desloca(Direcao.BAIXO, 5+1)
         ...
         # valor atual foi atualizado.
         atual_dimensao = janela.getmaxyx()
      ...

      contagem_str = ul_tempo(
         timer.agendado(),
         arredonda=True,
         acronomo=True
      )
      info_de_tempo(janela, contagem_str)
      percentual = 1.0 - timer.percentual()
      barra.preenche(percentual)
      barra()

      # troca para o timer de 1min.
      # só se o timer foi marcado com mais de meia-hora.
      if outra_barra:
         if (timer < 60) and (not barra_acionada):
            restante = Temporizador(60)
            barra_acionada = True
         elif timer < 60 and barra_acionada:
            # barra complementar de um minito mais ou menos.
            #desenha_barra_complementa(janela)
            # um percentual decrescente(%).
            percentual = 1.0 - restante.percentual()
            #preenche_barra_complementar(janela, percentual)
            barraminuto.preenche(percentual)
            barraminuto()
         ...
      ...

      # atualização de tela em quase 1min.
      janela.refresh()
      curses.napms(800)
   else:
      # mensagem de fim.
      janela.clear()
      # dimensão do terminal
      # cria texto-desenhado.
      texto_matriz = forma_string("desligando")
      (l, h) = (len(texto_matriz[0]), len(texto_matriz))
      # computação CSE para desenhar o texto-desenhado.
      posicao = posicao_centralizada(janela, h, l)
      # desenha em sí o texto-desenhado.
      escreve_no_curses(janela, posicao, texto_matriz)
      janela.refresh()
   ...

   curses.napms(1500)
   curses.endwin()
...

# Computa o lado superior esquerdo, para que
# se possa desenhar a barra de progresso como
# todo. Levando-se em consideração a quantia
# de linhas que formam a barra, assim com
# seus limites.
def computa_altura(janela, altura_objeto):
   h = altura_objeto
   (altura, _) = janela.getmaxyx()
   return (altura - (h+2) //2) // 2
...

def info_de_tempo(janela, texto):
   matriz = forma_string(texto)
   altura = len(matriz)
   largura = len(matriz[0])
   # largura do terminal.
   (_, lt) = janela.getmaxyx()
   # canto superior esquerdo da barra
   # de progresso como todo.
   cse = computa_altura(janela, altura)

   for lin in range(altura):
      y = lin + cse - (altura + 1)
      for col in range(largura):
         x = col + (lt-largura) // 2
         janela.addch(y, x, matriz[lin][col])
      ...
   ...
...

def escreve_no_curses(janela, ponto, texto_matriz):
   M = texto_matriz
   (altura, largura) = (len(M),len(M[0]))
   (y, x) = (ponto.y, ponto.x)

   for lin in range(altura):
      for col in range(largura):
         janela.addch(y+lin, x+col, M[lin][col])
   ...
...

# dado a dimensão do objeto de texto, cacula
# o canto-superior-esquerdo para que seja
# desenhado de forma centralizada.
def posicao_centralizada(janela, altura, largura):
   ((At, Lt), (a, l)) = (janela.getmaxyx(), (altura, largura))
   return Ponto(
      (At - a) // 2,
      (Lt - l) // 2
   )
...

class JanelaDebug():
   " para série de testes "
   def __init__(self, tempo):
      self._tempo_limite = tempo
      self._janela = curses.initscr()
      # sua configuração:
      curses.start_color()
      curses.use_default_colors()
      curses.curs_set(0)

      # novas cores.
      curses.init_color(18, 0, 255, 17)
      VERDE_ESCURO = 18 # Bom!
      # paletas de cores.
      curses.init_pair(99, curses.COLOR_GREEN, -1)
      curses.init_pair(98, curses.COLOR_YELLOW, -1)
      curses.init_pair(97, curses.COLOR_RED, -1)
      curses.init_pair(96, VERDE_ESCURO, -1)
   ...
   # encerra programa semi-gráfico.
   def encerra(self):
      curses.napms(self._tempo_limite)
      curses.endwin()
   ...
   def referencia(self):
      return self._janela
   ref = property(referencia, None, None, None)
...

from unittest import (TestCase, main, skip, skipIf)
from progresso import (BarraProgresso, Direcao, Ponto)
from os import get_terminal_size

class Funcoes(TestCase):
   def buscandoLayoutIdeal(self):
      janela = JanelaDebug(8500)
      info_de_tempo(janela.ref, "3.6h")
      (_, L) = janela.ref.getmaxyx()
      barra_geral = BarraProgresso(
         janela.ref, altura=6,
         largura=int(L * 0.70)
      )
      barra_minuto = BarraProgresso(
         janela.ref, altura=3,
         largura=int(L * (0.70**2)),
         mais_cores=True
      )
      barra_geral.centraliza()
      barra_minuto.centraliza()
      barra_minuto.desloca(Direcao.BAIXO, 6)
      barra_minuto.preenche(0.86)
      barra_geral.preenche(0.43)
      # renderização...
      barra_geral(); barra_minuto()
      janela.encerra()
   ...
   @skip("ainda não finalizado!")
   def barraPopupDinamismo(self):
      janela = JanelaDebug(8500)
      (_, L) = janela.ref.getmaxyx()
      barra_geral = BarraProgresso(
         janela.ref, largura=int(L * 0.70)
      )
      barra_minuto = BarraProgresso(
         janela.ref, altura=2,
         largura=int(L * (0.70**2)),
         mais_cores=True
      )
      percentual = 1.0
      texto = forma_string("3h")
      l = len(texto[0])
      L = (lambda j: j.getmaxyx()[1])

      while percentual > 0:
         ponto = Ponto(3, ((L(janela.ref)-l)//2))
         escreve_no_curses(janela.ref, ponto, texto)
         barra_geral.centraliza()
         barra_minuto.centraliza()
         barra_minuto.desloca(Direcao.BAIXO, 6)
         barra_minuto.preenche(percentual)
         barra_geral.preenche(percentual)
         # renderização...
         barra_geral(); barra_minuto()
         percentual -= 0.05
         curses.napms(1100)
         janela.ref.erase()
      ...
      janela.encerra()
   ...
   @skipIf(
     get_terminal_size().columns < 151,
     "tela muito pequena para esboçar desenhos"
   )
   def layoutParaTelaCheia(self):
      janela = JanelaDebug(8500)
      (H, L) = janela.ref.getmaxyx()
      percentual = 1.0
      texto = forma_string("37min")
      (l, h) = (len(texto[0]), len(texto))
      # só funciona para tela cheias, e que 
      # cabem o seguinte layout.
      bG = BarraProgresso(
         janela.ref, largura=int((L-l) * 0.70)
      )
      bM = BarraProgresso(
         janela.ref, altura=2,
         largura=int((L-l) * 0.70 * 0.93),
         mais_cores=True
      )

      while percentual > 0:
         ponto = Ponto((H-h)//2, (l//3))
         escreve_no_curses(janela.ref, ponto, texto)
         bG.centraliza()
         bM.centraliza()
         # ajeitando conforme a tela.
         bG.desloca(Direcao.DIREITA,16)
         bM.desloca(Direcao.DIREITA,16)
         bM.desloca(Direcao.BAIXO,2)
         bG.desloca(Direcao.CIMA, 3)
         bM.preenche(percentual)
         bG.preenche(percentual)
         # renderização...
         bG(); bM()
         percentual -= 0.05
         curses.napms(1100)
         janela.ref.erase()
      ...
      janela.encerra()
   ...
...

if __name__ == "__main__":
   main(verbose=1)
