
"""
   Aqui cuida-se especificamente da parte
gráfica do programa. Sera feita no 'ncurses'
do Python especificamente.
"""

import curses
from temporizador import (Temporizador, stringtime_to_segundos)
from texto_desenho.forma_palavras import forma_string 
from utilitarios.src.legivel import tempo as ul_tempo 


# constantes de personalização.
if __debug__:
   BARRA_V = '@'
else:
   BARRA_V = '#'
MARGEM_HORIZONTAL = 10
QTD_LINHAS = 5
PROGRESSO_ATOMO = ' '


def desenha_barra(janela):
   (_, largura) = janela.getmaxyx()
   comprimento = largura - (2 * MARGEM_HORIZONTAL)
   linha = computa_altura(janela)
   
   (y, x) = (linha - 1, MARGEM_HORIZONTAL)
   janela.vline(y, MARGEM_HORIZONTAL, BARRA_V, QTD_LINHAS + 1)
   x = MARGEM_HORIZONTAL + comprimento
   janela.vline(y, x, BARRA_V, QTD_LINHAS)
   x = MARGEM_HORIZONTAL + 1
   janela.hline(y, x, BARRA_V, comprimento)
   y = linha + QTD_LINHAS - 1
   janela.hline(y, x, BARRA_V, comprimento)
...

def inicia_grafico(timer):
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

   preenche_barra(janela, timer.percentual())
   janela.refresh()
   curses.napms(1500)

   # inclui contagem regressiva no minuto final.
   if __debug__:
      MEIA_HORA = 60 * 5 // 2
   else:
      MEIA_HORA = 3600 // 2
   barra_acionada = False
   outra_barra = timer > MEIA_HORA

   desenha_barra(janela)
   while timer():
      janela.clear()
      # texto piscante para dizer que nada no
      # sistema vai acontecer(desligamento).
      if __debug__:
         janela.addstr(2, 2, "debug mode", curses.A_BLINK)

      contagem = ul_tempo(
         timer.agendado(), 
         arredonda=True, 
         acronomo=True
      )
      info_de_tempo(janela, contagem)
      desenha_barra(janela)
      percentual = 1.0 - timer.percentual()
      preenche_barra(janela, percentual)

      # troca para o timer de 1min.
      # só se o timer foi marcado com mais de meia-hora.
      if outra_barra:
         if (timer < 60) and (not barra_acionada):
            restante = Temporizador(60)
            barra_acionada = True
         elif timer < 60 and barra_acionada:
            # barra complementar de um minito mais ou menos.
            desenha_barra_complementa(janela)
            # um percentual decrescente(%).
            percentual = 1.0 - restante.percentual()
            preenche_barra_complementar(janela, percentual)
         ...
      ...

      # atualização de tela em quase 1min.
      janela.refresh()
      curses.napms(800)
   else:
      # mensagem de fim.
      janela.clear()
      # dimensão do terminal
      (altura, largura) = janela.getmaxyx()
      # cria texto-desenhado.
      texto_matriz = forma_string("desligando")
      (l, h) = (len(texto_matriz[0]), len(texto_matriz))
      # computação CSE para desenhar o texto-desenhado.
      posicao = posicao_centralizada(janela, h, l)
      # desenha em sí o texto-desenhado.
      escreve_no_curses(janela, *posicao, texto_matriz)
      janela.refresh()
   ...

   curses.napms(1500)
   curses.endwin()
...

def preenche_barra(janela, percentual):
   (_, largura) = janela.getmaxyx()
   comprimento = largura - (2 * MARGEM_HORIZONTAL)
   linha = computa_altura(janela)
   # limite até onde será gerado.
   tarja = int(comprimento * percentual)

   # desenhando barra em si.
   janela.standout()
   for p in range(QTD_LINHAS-1):
      x = MARGEM_HORIZONTAL + 1
      y = p + linha
      if 0.70 < percentual <= 1.0:
         texto_cor = 96
      elif 0.450 < percentual <= 0.70:
         texto_cor = 99
      elif 0.20 < percentual <= 0.450:
         texto_cor = 98
      else:
         texto_cor = 97
      janela.attron(curses.color_pair(texto_cor))
      janela.hline(y, x, PROGRESSO_ATOMO, tarja)
      janela.attroff(curses.color_pair(texto_cor))
   ...
   janela.standend()
...

# Computa o lado superior esquerdo, para que
# se possa desenhar a barra de progresso como
# todo. Levando-se em consideração a quantia 
# de linhas que formam a barra, assim com 
# seus limites.
def computa_altura(janela):
   (altura, _) = janela.getmaxyx()
   return (altura - (QTD_LINHAS + 2)//2) // 2
...

def info_de_tempo(janela, texto):
   matriz = forma_string(texto)
   altura = len(matriz)
   largura = len(matriz[0])
   # largura do terminal.
   (_, lt) = janela.getmaxyx()
   # canto superior esquerdo da barra
   # de progresso como todo.
   cse = computa_altura(janela)

   for lin in range(altura):
      y = lin + cse - (altura + 1)
      for col in range(largura):
         x = col + (lt-largura)//2
         janela.addch(y, x, matriz[lin][col])
      ...
   ...
...

def escreve_no_curses(janela, y, x, texto_matriz):
   M = texto_matriz
   (altura, largura) = (len(M),len(M[0]))

   for lin in range(altura):
      for col in range(largura):
         janela.addch(y + lin, x + col, M[lin][col])
      ...
   ...
...

# dado a dimensão do objeto de texto, cacula 
# o canto-superior-esquerdo para que seja 
# desenhado de forma centralizada.
def posicao_centralizada(janela, altura, largura):
   (at, lt) = janela.getmaxyx()
   altura = (at - altura) // 2
   largura = (lt - largura) // 2
   return (altura, largura)
...

# é uma altura menor que a superior.
NOVA_QL = QTD_LINHAS - 2
# comprimento da barra é menor.
NOVA_MARGEM_H = MARGEM_HORIZONTAL + 3
# barra complementar de um miniuto para 
# da dinâmismo gráfico.
def desenha_barra_complementa(janela):
   (_, largura) = janela.getmaxyx()
   comprimento = largura - (2 * NOVA_MARGEM_H)
   linha = computa_altura(janela)
   
   (y, x) = (
      linha - 1 + (QTD_LINHAS-NOVA_QL) + NOVA_QL + 2, 
      NOVA_MARGEM_H 
   )
   janela.vline(y, NOVA_MARGEM_H, BARRA_V, NOVA_QL + 1)
   x = NOVA_MARGEM_H + comprimento
   janela.vline(y, x, BARRA_V, NOVA_QL) 
   x = NOVA_MARGEM_H + 1
   janela.hline(y, x, BARRA_V, comprimento)
   y += NOVA_QL
   janela.hline(y, x, BARRA_V, comprimento)
...

def preenche_barra_complementar(janela, percentual):
   (_, largura) = janela.getmaxyx()
   comprimento = largura - (2 * NOVA_MARGEM_H)
   linha = computa_altura(janela)
   # limite até onde será gerado.
   tarja = int(comprimento * percentual)
   # nova paleta de cores.
   curses.init_pair(95, curses.COLOR_BLUE, -1)

   # desenhando barra em si.
   janela.standout()
   for p in range(NOVA_QL-1):
      x = NOVA_MARGEM_H + 1
      y = p + linha + (QTD_LINHAS + 2)
      if 0.80 < percentual <= 1.0:
         texto_cor = 95
      elif 0.60 < percentual <= 0.80:
         texto_cor = 96
      elif 0.40 < percentual <= 0.60:
         texto_cor = 99
      elif 0.20 < percentual <= 0.40:
         texto_cor = 98
      else:
         texto_cor = 97
      janela.attron(curses.color_pair(texto_cor))
      janela.hline(y, x, PROGRESSO_ATOMO, tarja)
      janela.attroff(curses.color_pair(texto_cor))
   ...
   janela.standend()
...


if __name__ == "__main__":
   from time import sleep
   segundos = stringtime_to_segundos("3.5min")
   timer = Temporizador(segundos)
   #inicia_grafico(timer)

   while timer():
      contagem = ul_tempo(
         timer.agendado(), 
         arredonda=True, 
         acronomo=True
      )
      print("tempo =:: {}".format(contagem))
      sleep(5)
...
