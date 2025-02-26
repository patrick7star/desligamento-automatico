""" Tentando criar uma barra mais bonita."""

# o que será importado:
__all__ = ["BarraProgresso", "Ponto", "Direcao", "JanelaDebug"]

import curses, unittest
from time import (time, sleep)
from enum import (Flag, auto)
from os import get_terminal_size

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
      Desenho da barra de progresso, onde foi demandado, como também na 
   medida desejada. É claro que têm que respeitar o limite da 'janela', 
   esta, que tem quer ser passada por referência.
   """
   PROGRESSO_ATOMO = ' '

   # Atualiza coordenadas baseado no canto-superior-esquerdo passado:
   def _ajusta_coordenadas(self) -> None:
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

   def __init__(self, janela, altura = 4, largura = 50, posicao=Ponto(2, 2),
     mais_cores=False) -> None:
      # Dimensões passadas têm que ter algum limite:
      if altura < 2 or largura < 20:
         raise curses.error(
            "um tamanho assim, simplesmente não"
            + " carrega/descarrega a barra"
         )
      ...
      # Referência da janeal onde é desenhado a barra e os demais.
      self._janela = janela
      # Dimensão da barra.
      self._altura = altura
      self._largura = largura
      # Dimensão do canto-superior-esquerdo do objeto.
      self._cse = posicao
      self._ajusta_coordenadas()
      # Se quer adicionar o azul, ou demais cores baseado no percentual do 
      # progresso.
      self._maior_escalar_de_cor = mais_cores
      # Verificação do que foi passado acima.
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
      # Atual percentual do progresso que está sendo demonstrado:
      self.atual_percentual = 0.00

   def _desenha_borda_do_progresso(self) -> None:
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

      # Desenhas barras simultaneamente. Barras superior e inferior:
      x = (self._cse.x+1)
      (y, Y) = (self._cse.y, self._cie.y)

      for k in range(self._largura-1):
         # superior:
         self._janela.move(y, x + k)
         self._janela.addch(curses.ACS_HLINE)
         # inferior:
         self._janela.move(Y, x + k)
         self._janela.addch(curses.ACS_HLINE)

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

   def desenha(self) -> None:
      "Escreve figura da barra de progresso na tela do ncurses."
      self._desenha_borda_do_progresso()
      self._realiza_preenchimento()

   def _seleciona_uma_cor(self) -> None:
      percentual = self.atual_percentual

      # coloração depedendo do percentual.
      if self._maior_escalar_de_cor:
         if 0.80 < percentual <= 1.0:
            return 95
         elif 0.60 < percentual <= 0.80:
            return 96
         elif 0.40 < percentual <= 0.60:
            return 99
         elif 0.20 < percentual <= 0.40:
            return 98
         else:
            return 97
      else:
         if 0.70 < percentual <= 1.0:
            return 96
         elif 0.450 < percentual <= 0.70:
            return 99
         elif 0.20 < percentual <= 0.450:
            return 98
         else:
            return 97

   def _realiza_preenchimento(self) -> None:
      percentual = self.atual_percentual

      if percentual > 1.0:
         raise OverflowError(
            "tem que ser um valor maior ou igual a 1"
            + ", também, positivo."
         )

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

      # desenhando barra em si.
      self._janela.standout()
      for p in range(self._altura - 1):
         x = (self._ponto.x + MARGEM_X)
         y = (p + linha)
         texto_cor = self._seleciona_uma_cor()
         self._janela.attron(curses.color_pair(texto_cor))
         self._janela.hline(y, x, BarraProgresso.PROGRESSO_ATOMO, tarja)
         self._janela.attroff(curses.color_pair(texto_cor))
      ...
      self._janela.standend()

   def atualiza(self, valor: float) -> None:
      assert (valor >= 0.00 and valor <= 1.00)
      self.atual_percentual = valor
...

class JanelaDebug():
   " para série de testes "
   # taxa padrão para atualização de 'quadros'
   TAXA_PADRAO = 800 #milisegundos.
   def __init__(self, segundos):
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
      # primeira gravura de marca d'água.
      self._marca_dagua("modo de debug")
   ...
   # encerra programa semi-gráfico.
   def encerra(self):
      curses.napms(self._tempo_limite)
      curses.endwin()
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
      self._marca_dagua("modo debug")
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
      curses.napms(t)
   ...
   # mostrando que está no modo debug.
   def _marca_dagua(self, mensagem):
      # ciclos do loop infinito.
      (y, x) = self._janela.getmaxyx()
      self._janela.addstr(
         y-2, (x-(len(mensagem)+2)), mensagem,
         curses.A_BLINK | curses.A_ITALIC
      )
   ...
...

class Direcao(Flag):
   "Para direciona recuo demandado"
   CIMA = auto()
   BAIXO = auto()
   ESQUERDA = auto()
   DIREITA = auto()

   def oposta(self):
      "computa a direção oposta a esta"
      match self:
         case Direcao.CIMA:
            return Direcao.BAIXO
         case Direcao.BAIXO:
            return Direcao.CIMA
         case Direcao.ESQUERDA:
            return Direcao.DIREITA
         case Direcao.DIREITA:
            return Direcao.ESQUERDA
      ...
   ...
...

# continuação da implementação de 'BarraProgresso'.
class BarraProgresso(BarraProgresso):
   # criando um descriptor para sua dimensão.
   class Dimensao():
      def __get__(self, instancia, classe):
         return (instancia._altura, instancia._largura)
      def __set__(self, instancia, valor):
         raise AttributeError("ainda não é possível modifica-lá")
   ...
   dimensao = Dimensao()

   def centraliza(self) -> None:
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
   def desloca(self, direcao: Direcao, passo: int) -> None:
      "desloca o objeto na 'direção' dada, por 'n passos'"
      (max_altura, max_largura) = self._janela.getmaxyx()
      # renomeando ponto principal para
      # melhor codificação. Também dois pontos
      # utilizados que são usados repetidamente.
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
      # realinha as demais.
      self._ajusta_coordenadas()
   ...
   def mover(self, ponto: Ponto) -> bool:
      self._cse = ponto
      try:
         self._ajusta_coordenadas()
      except:
         return False
      finally:
         return True
   ...
   def anexa(self, direcao: Direcao, barra:BarraProgresso,
   margem:int=1) -> None:
      """
      Serão preciso o lado onde será anexado, que
      se usa também a 'direção', o espaço entre
      eles e, e a 'barra de progresso' a ser anexada;
      para ser honesto, por mais que seja nomeado como
      uma anexação, não existe qualquer captura do
      objeto, apenas o deslocamento dele baseado na
      instância, tal deslocamento que fica paracendo
      uma anexação.
      Obs.: a 'margem' dada não podem exceder grandes
      quantias, uma restrição auto imposta; já que
      "anexações" muitos espaçadas, não pareceriam,
      bem,... uma "anexação". O limite aqui será
      10 caractéres de distância no máximo.
      """
      if margem > 5:
         mensagem = (
            "excede o limite, portanto distorce "
            + "a \"anexação\""
         )
         raise OverflowError(mensagem)
      elif margem < 1:
         raise OverflowError(
            "não pode ser colocado colidindo "
            + "com o objeto da instância"
         )
      ...

      # move para a atual coordenada da instância.
      barra.mover(self._ponto)
      # dimensão do objeto barra.
      (altura, largura) = barra.dimensao

      match direcao:
         case Direcao.DIREITA | Direcao.ESQUERDA:
            barra.desloca(direcao, margem + largura)
            # verifica se distância(horizontal) é ampla?
            dx = abs(self._ponto.x-barra._ponto.x)
            if dx > (self._largura + margem):
               ajuste = dx - (self._largura + margem)
               barra.desloca(direcao.oposta(), ajuste)
            ...
         case Direcao.CIMA:
            barra.desloca(direcao, margem + altura)
         case Direcao.BAIXO:
            barra.desloca(direcao, margem + self._altura)
         case _:
            raise Exception("ainda não implementado")
      ...

class BarraMinuto(BarraProgresso):
   def __init__(self, janela, altura = 4, largura = 50, posicao=Ponto(2, 2)) -> None:
      super().__init__(janela, altura, largura, posicao, True)
      self.visibilidade = False
      self.inicio = None
      self.contagem_iniciada = False

   def aciona_visibilidade(self):
      self.visibilidade = True

   # Sobreescrevendo ....
   def desenha(self) -> None:
      hora_de_acionar_contagem = (
         self.visibilidade and
         (not self.contagem_iniciada) and
         (self.inicio is None)
      )

      # Começa a registra a contagem regressiva de um minuto.
      if hora_de_acionar_contagem:
         self.inicio = time()
         self.contagem_iniciada = True

      if self.contagem_iniciada and self.visibilidade:
         decorrido = time() - self.inicio
         percentual = 1.0 - decorrido / 60.0
         self._realiza_preenchimento(percentual)

      # Apenas mostra se tiver sido ativada.
      if self.visibilidade:
         super().desenha()

   def centraliza(self):
      super().centraliza()
      self.desloca(Direcao.BAIXO, 5)


class Classes(unittest.TestCase):
   "teste referentes as classe 'BarraProgresso'"
   def runTest(self):
      self.escalasDeCores()
   def desenhaBarra(self):
      janela = JanelaDebug(2.0)
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
      janela = JanelaDebug(2.5)
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
      janela = JanelaDebug(4.5)
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
      janela = JanelaDebug(5.0)
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
      janela = JanelaDebug(4.5)
      # instanciando e visualizando...
      barra = BarraProgresso(janela.ref)
      barra.preenche(0.15); barra();
      Barra = BarraProgresso(janela.ref, posicao=Ponto(17, 2))
      Barra.preenche(1.0); Barra()
      janela.encerra()
   ...
   def demonstracaoDescarregamento(self):
      janela = JanelaDebug(0.5)
      # instanciando e visualizando...
      percentual = 1.00
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(7, 15),
         largura=60, altura=6
      )
      while percentual > 0:
         janela.limpa()
         barra.preenche(percentual)
         # renderizando a animação ...
         barra()
         # diminuindo percentual e pausa.
         percentual -= 0.05; janela.congela(0.8)
      ...
      janela.encerra()
   ...
   def duasBarras(self):
      janela = JanelaDebug(0.5)
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
         janela.limpa()
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
         janela.limpa()
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
      janela = JanelaDebug(0.5)
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
         janela.limpa()
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
      janela = JanelaDebug(0.5)
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(4, 21),
         largura=45, altura=3
      ); barra()
      janela.congela(1.5)
      janela.limpa()
      barra.centraliza(); barra()
      janela.congela(1.500)
      janela.encerra()
   ...
   def deslocamentoBasico(self):
      # colocar tudo em um loop.
      entradas = [
         # direção, quantia de carácteres
         # à descolar; e o tempo para mostra
         # aquilo.
         (Direcao.DIREITA, 10, 1.5),
         (Direcao.ESQUERDA, 20, 1.5),
         (Direcao.CIMA, 4, 0.9),
         (Direcao.BAIXO, 10, 1.5)
      ]
      janela = JanelaDebug(0.500)
      barra = BarraProgresso(
         janela.ref, posicao=Ponto(4, 21),
         largura=45, altura=3
      ); barra()
      curses.napms(1500)
      # centraliza a instância criada.
      janela.limpa()
      barra.centraliza(); barra()
      curses.napms(1500)
      for (d, s, t) in entradas:
         barra.desloca(d, s)
         janela.limpa(); barra()
         janela.congela(t)
      ...
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
         janela.limpa()
         janela.congela(0.9)
      ...
      janela.encerra()
   ...
   @unittest.skipIf(
     get_terminal_size().columns < 151,
     "tela muito pequena para esboçar desenhos"
   )
   def anexacaoBarras(self):
      janela = JanelaDebug(4.0)
      # será anexada a direita.
      # próximo ao canto-superior-esquerdo.
      b1 = BarraProgresso(janela.ref)
      # próximo ao centro, um pouco à esquerda.
      b2 = BarraProgresso(janela.ref, altura=3, largura=40)
      b2.centraliza(); b2.desloca(Direcao.DIREITA, 14);
      b2.centraliza(); b2.desloca(Direcao.BAIXO, 2);
      b2.desloca(Direcao.ESQUERDA, 20)
      # próximo canto-inferior-direito.
      b3 = BarraProgresso(
         janela.ref, altura=8,
         largura=20,
         posicao=Ponto(23, 120)
      )
      b1(); b2(); b3();
      janela.congela(0.9)
      # primeira anexação...
      janela.limpa()
      b2.anexa(Direcao.CIMA, b3)
      b2.anexa(Direcao.DIREITA, b1)
      b1(); b2(); b3();
      janela.congela(0.9)
      # segunda anexação...
      b1.anexa(Direcao.BAIXO, b3)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # terceira anexação...
      b1.anexa(Direcao.CIMA, b2)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # quarta anexação...
      b2.anexa(Direcao.CIMA, b3)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # quinta anexação...
      b1.anexa(Direcao.ESQUERDA, b2)
      b2.anexa(Direcao.ESQUERDA, b3)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # sexta anexação...
      b3.anexa(Direcao.CIMA, b2)
      b3.anexa(Direcao.DIREITA, b1)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # sétima anexação...
      b2.anexa(Direcao.CIMA, b3)
      b2.anexa(Direcao.BAIXO, b1)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      # oito anexação...
      b3.anexa(Direcao.DIREITA, b1)
      b1.anexa(Direcao.BAIXO, b2)
      janela.limpa()
      b1(); b2(); b3();
      janela.congela(0.9)
      janela.encerra()
   ...
   @unittest.expectedFailure
   def anexacaoTransborda(self):
      j = JanelaDebug(4000)
      # será anexada a direita.
      # próximo ao canto-superior-esquerdo.
      b1 = BarraProgresso(j.ref)
      # próximo ao centro, um pouco à esquerda.
      b2 = BarraProgresso(j.ref, altura=3, largura=40)
      try:
         # o erro ocorre nesta chamada.
         b1.anexa(Direcao.CIMA, b2, margem=3)
         # está aqui, não chega a executar.
         b1(); b2();
      except OverflowError:
         # encerra a janela.
         j.encerra()
         import sys
         # relançando o erro.
         (excecao, info, _) = sys.exc_info()
         print("exceção que foi pega: '%s'" % info); del sys
         raise excecao
      finally:
         j.encerra()
   ...
...

class TesteBarraMinuto(unittest.TestCase):
   def verificacao_da_barra_minuto(self):
      janela = JanelaDebug(2.0)
      # instanciando e visualizando...
      bar = BarraMinuto(janela.ref)

      # renderizando ambas ...
      for k in range(1, 30):
         if int(k) == 15:
            bar.aciona_visibilidade()
         percentual = 1.0 - k / 30.0
         bar.preenche(percentual)
         bar()
         janela.congela(0.600)
         janela.limpa()
      janela.encerra()
   ...


if __name__ == "__main__":
   unittest.main(verbose=2)
