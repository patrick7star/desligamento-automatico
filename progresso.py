

""" Tentando criar uma barra mais bonita."""

import curses, unittest
from graficos import PROGRESSO_ATOMO
#PROGRESSO_ATOMO = ' '

# verifica se argumentos passados cumprem
# com os limites das telas.
def valida(ponto, dimensao_obj, dimensao_janela) -> (bool, int):
   (Y, X) = dimensao_janela
   # altura(H) e largura(L)
   (H, L) = dimensao_obj
   (y, x) = (ponto.y, ponto.x)
   if (H + y) > Y:
      return (False, Y-(y+H))
   if (L + x) > X:
      return (False, X-(L+x))
   # se não dispará, e chegar até aqui,
   # então é válido.
   return (True, 0)
...

# outro nome para o mesmo objeto.
class Ponto:
   "representação do 'Ponto', posições (y, x)"
   def __init__(self, vertical, horizontal):
      self._y = vertical
      self._x = horizontal
   ...
   def __str__(self):
      return "({}, {})".format(self._y, self._x)
   def __add__(self, ponto):
      if not isinstance(ponto, Ponto):
         raise ValueError("'%s' não é do tipo 'Ponto'" % type(ponto))
      return Ponto(self._y + ponto.y, self._x + ponto.x)
   def __sub__(self, ponto):
      if not isinstance(ponto, Ponto):
         raise ValueError("'%s' não é do tipo 'Ponto'" % type(ponto))
      return Ponto(self._y - ponto.y, self._x - ponto.x)
   ...
   # só delega as funções acimas que já fazem
   # quase todo o trabalho.
   def __iadd__(self, ponto):
      return self + ponto
   def __isub__(self, ponto):
      return self - ponto
   # encapsulamento ...
   def valor_x(self):
      return self._x
   def valor_y(self):
      return self._y
   x = property(valor_x, doc="coordenada X(horizontal)")
   y = property(valor_y, doc="coordenada Y(vertical)")
...

class BarraProgresso:
   """
   Desenho da barra de progresso, onde foi
   demandado, como também na medida desejada. É
   claro que têm que respeitar o limite da
   'janela', esta, que tem quer ser passada por
   referência.
   """
   # atualiza coordenadas baseado no
   # canto-superior-esquerdo passado:
   def _ajusta_coordenadas(self):
      # precisa ter sido criado o atibuto
      # principal, se se, o resto é aplicável;
      # caso contrário lança um erro.
      if hasattr(self, "_cse"):
         P = self._cse
         # achando as demais:
         # canto-superior-direito.
         self._csd = P + Ponto(0, self._largura)
         self._cid = P + Ponto(self._altura, self._largura)
         self._cie = P + Ponto(self._altura, 0)
         # atualizando referência do ponto-genêrico.
         self._ponto = self._cse
      else:
         raise Exception("coordenada principal não existe!")
   ...
   # método construtor:
   def __init__(self, janela, altura = 4,
   largura = 50, posicao = Ponto(2, 2),
   mais_cores=False):
      # dimensões passadas têm que ter algum limite:
      if altura < 2 or largura < 20:
         raise curses.error(
            "um tamanho assim, simplesmente não"
            + " carrega/descarrega a barra"
         )
      ...
      # referência da janeal onde é desenhado
      # a barra e os demais.
      self._janela = janela
      # dimensão da barra.
      self._altura = altura
      self._largura = largura
      # dimensão do canto-superior-esquerdo do objeto.
      self._cse = posicao
      self._ajusta_coordenadas()
      # se quer adicionar o azul, ou demais cores
      # baseado no percentual do progresso.
      self._maior_escalar_de_cor = mais_cores
      # verificação do que foi passado acima.
      dimensao_objeto = (self._altura, self._largura)
      (argumentos_validos, diferenca) = valida(
         self._cse, dimensao_objeto,
         self._janela.getmaxyx()
      )
      if not argumentos_validos:
         raise curses.error(
            "excede a tela em %d caractéres"
            % diferenca
         )
      ...
   ...
   # desenha a barra.
   def _desenha_barra(self):
      # cuidando dos cantos primeiramente.
      pares = (
         # canto-superior-esquerdo.
         (self._cse, curses.ACS_ULCORNER),
         # canto-superior-direito.
         (self._csd, curses.ACS_URCORNER),
         # canto-inferior-direito.
         (self._cid, curses.ACS_LRCORNER),
         # canto-inferior-esquerdo.
         (self._cie, curses.ACS_LLCORNER)
      )
      for (ponto, simbolo) in pares:
         (y, x) = (ponto.y, ponto.x)
         self._janela.move(y, x)
         self._janela.addch(simbolo)
      ...
      # desenhas barras simultaneamente.
      # barras superior e inferior:
      x = (self._cse.x+1)
      (y, Y) = (self._cse.y, self._cie.y)
      for k in range(self._largura-1):
         # superior:
         self._janela.move(y, x + k)
         self._janela.addch(curses.ACS_HLINE)
         # inferior:
         self._janela.move(Y, x + k)
         self._janela.addch(curses.ACS_HLINE)
      ...
      # barras esquerda e direita:
      y = (self._cse.y + 1)
      (x, X) = (self._cse.x, self._csd.x)
      for k in range(self._altura-1):
         # lateral esquerda:
         self._janela.move(y+k, x)
         self._janela.addch(curses.ACS_VLINE)
         # lateral direita:
         self._janela.move(y+k, X)
         self._janela.addch(curses.ACS_VLINE)
      ...
   ...
   # toda chamada redenrizar tal.
   def __call__(self):
      "renderiza o que foi feito."
      self._desenha_barra()
      self._janela.refresh()
   ...
   def preenche(self, percentual:float):
      if percentual > 1.0:
         raise OverflowError(
            "tem que ser um valor maior ou igual a 1"
            + ", também, positivo."
         )
      ...
      (_, largura) = self._janela.getmaxyx()
      comprimento = (self._largura - 1)
      # são o mesmo, más para uso genérico 'ponto'
      # é um nome muito mais compreensível. Portanto,
      # se não há tal atributo, aqui será criado um.
      self._ponto = self._cse
      # ordenada à partir do canto-superior-esquerdo.
      linha = self._ponto.y + 1
      MARGEM_X = 2
      # limite até onde será gerado.
      tarja = int(comprimento * percentual) - MARGEM_X
      # nova paleta de cores.
      curses.init_pair(95, curses.COLOR_BLUE, -1)

      # desenhando barra em si.
      self._janela.standout()
      for p in range(self._altura):
         x = (self._ponto.x + MARGEM_X)
         y = (p + linha)
         # coloração depedendo do percentual.
         if self._maior_escalar_de_cor:
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
         else:
            if 0.70 < percentual <= 1.0:
               texto_cor = 96
            elif 0.450 < percentual <= 0.70:
               texto_cor = 99
            elif 0.20 < percentual <= 0.450:
               texto_cor = 98
            else:
               texto_cor = 97
         ...
         self._janela.attron(curses.color_pair(texto_cor))
         self._janela.hline(y, x, PROGRESSO_ATOMO, tarja)
         self._janela.attroff(curses.color_pair(texto_cor))
      ...
      self._janela.standend()
   ...
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

from enum import (Flag, auto)
class Direcao(Flag):
   "Para direciona recuo demandado"
   CIMA = auto()
   BAIXO = auto()
   ESQUERDA = auto()
   DIREITA = auto()
...

# continuação da implementação de 'BarraProgresso'.
class BarraProgresso(BarraProgresso):
   def centraliza(self):
      "centralização do objeto no centro da tela."
      # dimensões da tela e do objeto.
      (H, L) = self._janela.getmaxyx()
      (h, l) = (self._altura, self._largura)
      # computa o meio, baseado na dimensão 
      # do objeto, e também levando a da 'tela'.
      self._cse = Ponto((H-h)//2, (L-l)//2)
      # acha os demais cantos e os atualiza.
      self._ajusta_coordenadas()
   ...
   def desloca(self, direcao: Direcao, passo: int):
      "desloca o objeto na 'direção' dada, por 'n passos'"
      (max_altura, max_largura) = self._janela.getmaxyx()
      # renomeando ponto principal para 
      # melhor codificação. Também dois pontos
      # utilizados que são usados repetidamente.
      from platform import python_version_tuple
      versao = python_version_tuple()[1]
      if versao >= 10:
         eval("""
         match direcao:
            case Direcao.DIREITA:
               # verificando também se tal ordem de movimento
               # não ultrapassa os limites da 'tela'. Se este
               # for o caso, um erro será lançado.
               if self._csd.x + passo >= max_largura:
                  raise OverflowError("passa limites da tela")
               self._cse += Ponto(0, passo)
            case Direcao.ESQUERDA:
               if self._cse.x - passo < 0:
                  raise OverflowError("passa limites da tela")
               self._cse -= Ponto(0, passo)
            case Direcao.CIMA:
               if self._cse.y - passo < 0:
                  raise OverflowError("passa limites da tela")
               self._cse -= Ponto(passo, 0)
            case Direcao.BAIXO:
               if self._csd.y + passo >= max_altura:
                  raise OverflowError("passa limites da tela")
               self._cse += Ponto(passo, 0)
         ...
         """)
      else:
         if direcao is Direcao.DIREITA:
            # verificando também se tal ordem de movimento
            # não ultrapassa os limites da 'tela'. Se este
            # for o caso, um erro será lançado.
            if self._csd.x + passo >= max_largura:
               raise OverflowError("passa limites da tela")
            self._cse += Ponto(0, passo)
         elif direcao is Direcao.ESQUERDA:
            if self._cse.x - passo < 0:
               raise OverflowError("passa limites da tela")
            self._cse -= Ponto(0, passo)
         elif direcao is Direcao.CIMA:
            if self._cse.y - passo < 0:
               raise OverflowError("passa limites da tela")
            self._cse -= Ponto(passo, 0)
         elif direcao is Direcao.BAIXO:
            if self._csd.y + passo >= max_altura:
               raise OverflowError("passa limites da tela")
            self._cse += Ponto(passo, 0)
         else:
            raise Exception("não implementado para tal!")
      ...
      # realinha as demais.
      self._ajusta_coordenadas()
   ...
...

class Classes(unittest.TestCase):
   "teste referentes as classe 'BarraProgresso'"
   def desenhaBarra(self):
      janela = JanelaDebug(2500)
      # instanciando e visualizando...
      b = BarraProgresso(janela.ref)
      b1 = BarraProgresso(
         janela.ref, altura=7, largura=30,
         posicao=Ponto(10, 45)
      )
      # renderizando ambas ...
      b(); b1()
      janela.encerra()
   ...
   @unittest.expectedFailure
   def quebraComArgumentosErrados(self):
      janela = JanelaDebug(2500)
      try:
         BarraProgresso(
            janela.ref, altura=7, largura=30,
            posicao=Ponto(100, 45)
         )
      except curses.error:
         import sys
         print("sim, houve um erro!", file=sys.stderr)
         janela.encerra()
         # relançando erro.
         raise curses.error()
   ...
   def metodoPreenche(self):
      janela = JanelaDebug(4500)
      # instanciando e visualizando...
      b = BarraProgresso(janela.ref)
      b.preenche(0.15); b();
      b1 = BarraProgresso(janela.ref, posicao=Ponto(7, 2))
      b1.preenche(0.25); b1()
      b2 = BarraProgresso(janela.ref, posicao=Ponto(12, 2))
      b2.preenche(0.55); b2()
      b3 = BarraProgresso(janela.ref, posicao=Ponto(17, 2))
      b3.preenche(0.95); b3()
      janela.encerra()
   ...
   @unittest.expectedFailure
   def overflowMetodoPreenche(self):
      janela = JanelaDebug(500)
      # instanciando e visualizando...
      b = BarraProgresso(janela.ref)
      b.preenche(0.15); b();
      b1 = BarraProgresso(janela.ref, posicao=Ponto(7, 2))
      b1.preenche(0.25); b1()
      b2 = BarraProgresso(janela.ref, posicao=Ponto(12, 2))
      try:
         b2.preenche(1.001)
      except OverflowError:
         janela.encerra()
         # relançando erro.
         raise OverflowError()
      ...
      b3 = BarraProgresso(janela.ref, posicao=Ponto(17, 2))
      b3.preenche(0.95); b3()
      janela.encerra()
   ...
   def retocandoPreenche(self):
      janela = JanelaDebug(4500)
      # instanciando e visualizando...
      barra = BarraProgresso(janela.ref)
      barra.preenche(0.15); barra();
      Barra = BarraProgresso(janela.ref, posicao=Ponto(17, 2))
      Barra.preenche(1.0); Barra()
      janela.encerra()
   ...
   def demonstracaoDescarregamento(self):
      janela = JanelaDebug(500)
      # instanciando e visualizando...
      percentual = 1.00
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(7, 15),
         largura=60, altura=6
      )
      while percentual > 0:
         janela.ref.erase()
         barra.preenche(percentual)
         # renderizando a animação ...
         barra()
         # diminuindo percentual e pausa.
         percentual -= 0.05; curses.napms(800)
      ...
      janela.encerra()
   ...
   def duasBarras(self):
      janela = JanelaDebug(500)
      # instanciando e visualizando...
      percentual_maior = 1.00
      percentual_menor = 1.0
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(7, 15),
         largura=60, altura=6
      )
      minibarra = BarraProgresso(
         janela.ref, posicao=Ponto(14, 21),
         largura=45, altura=2
      )
      # primeiro apenas a animação do maior.
      while percentual_maior > 0:
         janela.ref.erase()
         barra.preenche(percentual_maior)
         minibarra.preenche(percentual_menor)
         # renderizando a animação ...
         barra(); minibarra()
         # diminuindo percentual e pausa.
         percentual_maior -= 0.05
         curses.napms(800)
      ...
      # agora a mini barra de 1min.
      while percentual_menor > 0:
         janela.ref.erase()
         minibarra.preenche(percentual_menor)
         # renderizando a animação ...
         barra(); minibarra()
         # diminuindo percentual e pausa.
         percentual_menor -= 0.05
         curses.napms(800)
      ...
      janela.encerra()
   ...
   def escalasDeCores(self):
      janela = JanelaDebug(500)
      barra_i = BarraProgresso(
         janela.ref, posicao=Ponto(10, 21),
         largura=45, altura=3
      )
      barra_ii = BarraProgresso(
         janela.ref, posicao=Ponto(6, 21),
         largura=45, altura=3, mais_cores=True
      )
      percentual = 1.0
      # primeiro apenas a animação do maior.
      while percentual > 0:
         janela.ref.erase()
         barra_i.preenche(percentual)
         barra_ii.preenche(percentual)
         # renderizando a animação ...
         barra_i(); barra_ii()
         # diminuindo percentual e pausa.
         percentual -= 0.05
         curses.napms(800)
      ...
      janela.encerra()
   ...
   def centralizandoBarra(self):
      janela = JanelaDebug(500)
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(4, 21),
         largura=45, altura=3
      ); barra()
      curses.napms(1500)
      janela.ref.erase()
      barra.centraliza(); barra()
      curses.napms(1500)
      janela.encerra()
   ...
   def deslocamentoBasico(self):
      janela = JanelaDebug(500)
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(4, 21),
         largura=45, altura=3
      ); barra()
      curses.napms(1500)
      # centraliza a instância criada.
      janela.ref.erase()
      barra.centraliza(); barra()
      curses.napms(1500)
      # move ela 10 caractéres para direita.
      barra.desloca(Direcao.DIREITA, 10)
      janela.ref.erase(); barra()
      curses.napms(1500)
      # move ela 20 caractéres à esquerda.
      barra.desloca(Direcao.ESQUERDA, 20)
      janela.ref.erase(); barra()
      curses.napms(1500)
      # erge '7 caractéres' ela.
      barra.desloca(Direcao.CIMA, 4)
      janela.ref.erase(); barra()
      curses.napms(900)
      # então move '10 abaixo'.
      barra.desloca(Direcao.BAIXO, 10)
      janela.ref.erase(); barra()
      curses.napms(1_500)
      janela.encerra()
   ...
   @unittest.expectedFailure
   def transbordamentoDeTela(self):
      janela = JanelaDebug(3_500)
      barra = BarraProgresso(janela.ref)
      barra.centraliza(); barra()
      from random import choice 
      direcao = choice(
         (Direcao.CIMA, Direcao.DIREITA, 
         Direcao.ESQUERDA, Direcao.BAIXO)
      )
      while True:
         barra()
         try:
            barra.desloca(direcao, 2)
         except OverflowError:
            self.assertTrue(True)
            janela.encerra()
            # relançando erro.
            raise OverflowError()
         janela.ref.erase()
         curses.napms(900)
      ...
      janela.encerra()
   ...
...

if __name__ == "__main__":
   unittest.main(verbose=2)

# o que será importado:
__all__ = ("BarraProgresso", "Ponto", "Direcao")
...
