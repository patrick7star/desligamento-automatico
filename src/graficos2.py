"""
   O código que cuida da interface do programa, usando 'curses', que foi
 escrito aqui está muito confuso: ele, a versão debug, os testes. Tentarei
 reescrever o código de maneira simples.
"""
from curses import (
 window as Window, start_color, use_default_colors, curs_set, nocbreak,
 initscr, endwin, napms, color_pair, start_color, init_color, init_pair,
 COLOR_GREEN, COLOR_WHITE, COLOR_BLUE, COLOR_MAGENTA, COLOR_YELLOW,
 COLOR_RED, COLOR_BLACK, error as CursesError
)
import curses
from time import (time)
from datetime import (timedelta, datetime)
from enum import (Flag, auto)
# Próprio projeto:
from lib.utilitarios.tela import (Ponto)
from lib.utilitarios.legivel import (tempo as tempo_legivel)
from .tempo_ligado import (tempos_importantes)
from lib.utilitarios.texto import (constroi_str as ConstroiString)


def definicoes_de_todas_cores() -> None:
   "Inicia todas cores que serão usadas na janela."
   # Definindo novas cores...
   init_color(18, 0, 255, 17)
   VERDE_ESCURO = 18 # Bom!

   # Paletas de cores.
   init_pair(95, COLOR_BLUE, -1)
   init_pair(96, VERDE_ESCURO, -1)
   init_pair(97, COLOR_RED, -1)
   init_pair(98, COLOR_YELLOW, -1)
   init_pair(99, COLOR_GREEN, -1)

   # Papéis de parede com fonte negra:
   init_pair(80, COLOR_BLACK, COLOR_YELLOW)
   init_pair(81, COLOR_BLACK, COLOR_RED)
   init_pair(82, COLOR_BLACK, COLOR_BLUE)
   init_pair(83, COLOR_BLACK, COLOR_MAGENTA)
   init_pair(84, COLOR_BLACK, COLOR_GREEN)

   # Papéis de parede com fonte branca:
   init_pair(70, COLOR_WHITE, COLOR_YELLOW)
   init_pair(71, COLOR_WHITE, COLOR_RED)
   init_pair(72, COLOR_WHITE, COLOR_BLUE)
   init_pair(73, COLOR_WHITE, COLOR_MAGENTA)
   init_pair(74, COLOR_WHITE, COLOR_GREEN)
   init_pair(55, COLOR_BLACK, COLOR_YELLOW)
   init_pair(56, COLOR_BLACK, VERDE_ESCURO)

def cria_janela_e_a_configura() -> Window:
   "Cria janela geral de desenho, configura-a e retorna para o chamador."
   janela = initscr()

   # sua configuração:
   start_color()
   use_default_colors()
   curs_set(0)
   # adicionado captura de tecla.
   nocbreak()
   janela.nodelay(True)
   definicoes_de_todas_cores()

   return janela

def espacador(In: str) -> str:
   "Adiciona margens a uma atual string."
   return ' ' + In + ' '

class Desenho():
   "Classe abstrata para todos tipos de desenhos feitos."
   def desenha(self, tela: Window) -> None:
      raise NotImplementedError("Sempre reescreve tal método")

   def desenha(self, tela: Window, ponto: Ponto) -> None:
      "Faz o desenho do objeto na 'tela', à partir do respectivo 'ponto'."
      raise NotImplementedError("O mesmo que o anterior, mas com posição")

   def dimensao(self) -> (int, int):
      "O retorno é o valor é sua altura, e a largura, respectivamente."
      raise NotImplementedError("A dimensão do desenho em linhas e colunas.")

# === === === === === === === === === === === === === === === === === === ===
#                          Barras de Status e 
#                             seus minis Widgets
# === === === === === === === === === === === === === === === === === === ===
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

class TipoDeExecucao(Desenho):
   def __init__(self) -> None:
      self.msg = ""

   def desenha(self, tela: Window, ponto: Ponto) -> None:
      assert (isinstance(tela, Window))
      assert (isinstance(ponto, Ponto))

      (y, x) = tuple(ponto)
      if __debug__:
         (self.msg, cor) = ("modo-debug", 71)
      else:
         (self.msg, cor) = ("Normal", 72)

      # Adiciona margem ao texto.
      self.msg = espacador(self.msg)
      tela.addstr(y, x, self.msg, color_pair(cor))

   def dimensao(self) -> (int, int):
      return (1, len(self.msg))

class Cronometro(Desenho):
   """
   Marca o tempo de demonstração da interface. Na verdade, o ínicio é desde
   a instância foi criada. Então, cuidado nisso.
   """
   def __init__(self) -> None:
      self.inicio = time()

   def decorrido(self) -> timedelta:
      final = time()
      diferenca = final - self.inicio
      return timedelta(seconds=diferenca)

   def desenha(self, tela: Window, posicao: Ponto) -> None:
      (y, x) = tuple(posicao)
      passado = self.decorrido()
      fmt = "%s" % tempo_legivel(passado, True, True)
      fmt = espacador(fmt)

      tela.addstr(y, x, fmt, color_pair(73))

   def dimensao(self) -> (int, int):
      return (1, 7)

class Horario(Desenho):
   "Horário atual do sistema."
   def __init__(self) -> None:
      self.comprimento = 7

   def desenha(self, tela: Window, posicao: Ponto) -> None:
      agora = datetime.today()
      (y, x) = list(posicao)
      formatacao = agora.strftime("%2H:%2M")
      formatacao = espacador(formatacao)

      self.comprimento = len(formatacao)
      tela.addstr(y, x, formatacao, color_pair(74))

   def dimensao(self) -> (int, int):
      return (1, self.comprimento)

class ComputadorAtivo(Desenho):
   def __init__(self) -> None:
      self.fmt = ""

   def desenha(self, tela: Window, posicao: Ponto) -> None:
      (y, x) = list(posicao)
      (tempo_ativo, _)= tempos_importantes()
      formatacao = tempo_legivel(tempo_ativo)
      formatacao = espacador(formatacao)
      self.fmt = formatacao

      tela.addstr(y, x, formatacao, color_pair(55))

   def dimensao(self) -> (int, int):
      if self.fmt == "":
         return (1, 8)
      else:
         return (1, len(self.fmt))
 
class BarraStatus(Desenho):
   def __init__(self, *componentes: list[Desenho]) -> None:
      self.componentes = componentes
      self.pilha = []

      for item in self.componentes:
         self.pilha.append(item)

   def desenha(self, tela: Window) -> None:
      (H_MAX, L_MAX) = tela.getmaxyx()
      preenchido = 2

      for item in self.componentes:
         (_, largura) = item.dimensao()

         if (preenchido + largura) > L_MAX:
            raise IndexError("Transbordou a tela")

         X = preenchido
         posicao = Ponto(H_MAX - 2, X)
         item.desenha(tela, posicao)
         preenchido += largura


# === === === === === === === === === === === === === === === === === === ===
#                             Janela Principal
# === === === === === === === === === === === === === === === === === === ===
class Janela():
   """
     Desenho da janela gráfica(no terminal, usando ncurses). Ela renderiza
   todos elementros nela adicionado. 
     Não é um caso geral, más, está sendo feito o máximo possível nísso, 
   assim, futuramente, pode ser copiada de forma simples. Poderia ser bem 
   mais genérica, mas tal situação iria criar um 'boilerplate code' pra atual
   aplicação que está sendo feita. Isso seria horrível, pois este código 
   está sendo feito justamente por este erro cometido no outro.
      """
   # A taxa que a tela atualiza em milisegundos.
   FALHOU = -1
   QUADROS_POR_SEG = 600

   def __init__(self, *componentes) -> None:
      self.janela = cria_janela_e_a_configura()
      # Tipo de execução no momento.
      self.status = BarraStatus(
         TipoDeExecucao(), 
         Cronometro(),
         Horario(),
         ComputadorAtivo()
      )
      for item in componentes:
         if isinstance(item, Percentual):
            self.barra = BarraProgresso(percentual=item)
            break
      else:
         self.barra = BarraProgresso()

      self.texto = Info("1003")

   def renderiza(self) -> None:
      J = self.janela

      self.janela.erase()
      self.status.desenha(J)
      self.texto.desenha(J, Ponto(1,1))
      # Ajustando barra ...
      self.barra.centraliza(J)
      self.barra.desloca(J, Direcao.CIMA, 2)
      self.barra.desenha(J)
      self.janela.refresh()
      napms(Janela.QUADROS_POR_SEG)

   def __del__(self):
      ESPERA = Janela.QUADROS_POR_SEG * 3;
      napms(ESPERA)
      endwin()

class Interruptor():
   """
   Fazer parte da condição do loop em execução. Se em algum momento alternar
   pra desligado. Então interrompe-a.
   """
   def __init__(self, estado=False) -> None:
      self.ligado = estado

   def alterna(self) -> bool:
      valor_antigo = self.ligado
      self.ligado = (not self.ligado)

      return valor_antigo

   def __bool__(self) -> bool:
      return self.ligado


def console_da_aplicacao(app: Janela, chave: Interruptor) -> None:
   "Definição das teclas que o comando interpreta."
   pressionado = app.janela.getch()

   if pressionado != Janela.FALHOU:
      match chr(pressionado).lower():
         case 's':
            chave.alterna()
         case _:
            return None

# === === === === === === === === === === === === === === === === === === ===
#                          Barras de Progressos 
# === === === === === === === === === === === === === === === === === === ===
from numbers import (Rational)

class Percentual(Rational):
   """
     Objeto que representa e retorna um percentual. Usar no número puro, 
   evita que possa-se declarar-lo antes, assim reter uma referência, e 
   mandar ele com argumento. Assim, é possível modificar a instância externa,
   que a interna também se altera.
     Tente apenas o tipo 'Fraction', mas parece que ele não retorna um objeto
   que possa aplicar tal ação.
      """
   def __init__(self, n: float = 1.0) -> None:
      if n > 100:
         raise OverflowError("o valor tem que ser maior ou igual à 100")

      if n < 0:
         raise ValueError("não é possíveis números negativos")

      self.numerador = n

   # Não útil no momento, porém é preciso implementar.
   def __abs__(self): return self
   def __add__(self, esquerdo): pass
   def __ceil__(self, esquerdo): pass
   def __floor__(self, esquerdo): pass
   def __floordiv__(self, esquerdo): pass
   def __mod__(self, esquerdo): pass
   def __mul__(self, esquerdo): pass
   def __trunc__(self, esquerdo): pass
   def __round__(self, esquerdo): pass
   def __neg__(self, esquerdo): pass
   def __truediv__(self, esquerdo): pass
   def __pos__(self, esquerdo): pass
   def __pow__(self, esquerdo): pass
   def __rmul__(self, esquerdo): pass
   def __rpow__(self, esquerdo): pass
   def __rfloordiv__(self, esquerdo): pass
   def __radd__(self, esquerdo): pass
   def __rmod__(self, esquerdo): pass
   def __rtruediv__(self, esquerdo): pass

   def __eq__(self, esquerdo) -> bool: 
      return self.numerador == esquerdo.numerador

   def __le__(self, obj) -> bool: 
      return self.numerador <= obj.numerador

   def __lt__(self, obj) -> bool: 
      return self.numerador < obj.numerador

   @property
   def denominator(self):
      return 100.0

   @property
   def numerator(self): 
      return self.numerador

   @numerator.setter
   def numerator(self, novo: int):
      self.numerador = novo

   def __float__(self) -> float:
      return self.numerator / self.denominator

class Ponto(Ponto):
   """
     A classe abaixa funciona apenas com está operação. Não me lembro bem o
   porquê defini assim, más, é como funciona, então implemetando. Suponho que
   foi está a implementação do antigo 'Ponto'. Aqui uso o padrão da 
   biblioteca 'Utilitários'.
     Outras propriedades que tal 'Ponto' ainda não implementa foram
   adicioanadas, pelo o simples motivo de poder rodar o programa. Futuramente
   adicionarei tais funções essenciais no código dos 'Utilitários'.
   """
   def __add__(a: Ponto, b: Ponto) -> Ponto:
      (y_a, x_a) = tuple(a)
      (y_b, x_b) = tuple(b)

      return Ponto(y_a + y_b, x_a + x_b)

   def __sub__(a: Ponto, b: Ponto) -> Ponto:
      (y_a, x_a) = tuple(a)
      (y_b, x_b) = tuple(b)

      return Ponto(y_a - y_b, x_a - x_b)


   def __getitem__(self, indice: int):
      if not isinstance(indice, int):
         raise KeyError("Tem que ser do tipo inteiro")

      match indice:
         case 0:
            return self.lin
         case 1:
            return self.col
         case _:
            raise IndexError("Há apenas dois")

   def _getX(self) -> int:
      return self.col

   def _getY(self) -> int:
      return self.lin

   x = property(_getX, None, None, "Acesso ao valor")
   y = property(_getY, None, None, "Acesso ao valor")

class BarraProgresso(Desenho):
   """
      Desenho da barra de progresso, onde foi demandado, como também na
   medida desejada. É claro que têm que respeitar o limite da 'janela',
   esta, que tem quer ser passada por referência.
   """
   PROGRESSO_ATOMO = ' '

   @staticmethod
   def valida(ponto, dimensao_obj, dimensao_janela) -> (bool, int):
      "Verifica se argumentos passados cumprem com os limites das telas."
      (Y, X) = dimensao_janela
      (H, L) = dimensao_obj
      (y, x) = (ponto.y, ponto.x)

      if (H + y) > Y:
         return (False, Y - (y+H))
      if (L + x) > X:
         return (False, X - (L+x))

      # se não dispará, e chegar até aqui,
      # então é válido.
      return (True, 0)

   def _ajusta_coordenadas(self) -> None:
      "Atualiza coordenadas baseado no canto-superior-esquerdo passado:"
      # precisa ter sido criado o atibuto principal, se se, o resto é 
      # aplicável; caso contrário lança um erro.
      if hasattr(self, "_cse"):
         P = self._cse
         # Acha as demais. Canto-superior-direito:
         self._csd = P + Ponto(0, self._largura)
         self._cid = P + Ponto(self._altura, self._largura)
         self._cie = P + Ponto(self._altura, 0)
         # atualizando referência do ponto-genêrico.
         self._ponto = self._cse
      else:
         raise Exception("coordenada principal não existe!")

   def __init__(self, percentual: Percentual = Percentual(), altura = 4,
     largura = 50, posicao=Ponto(2, 2), mais_cores=False) -> None:
      # Dimensões passadas têm que ter algum limite:
      if altura < 2 or largura < 20:
         raise CursesError(
            "um tamanho assim, simplesmente não"
            + " carrega/descarrega a barra"
         )

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
      # Atual percentual do progresso que está sendo demonstrado:
      self.percentual = percentual

   def _desenha_borda_do_progresso(self, janela: Window) -> None:
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
         (y, x) = tuple(ponto)
         janela.move(y, x)
         janela.addch(simbolo)

      # Desenhas barras simultaneamente. Barras superior e inferior:
      x = (self._cse[1] + 1)
      (y, Y) = (self._cse[0], self._cie[0])

      for k in range(self._largura-1):
         # superior:
         janela.move(y, x + k)
         janela.addch(curses.ACS_HLINE)
         # inferior:
         janela.move(Y, x + k)
         janela.addch(curses.ACS_HLINE)

      # barras esquerda e direita:
      y = (self._cse.y + 1)
      (x, X) = (self._cse.x, self._csd.x)

      for k in range(self._altura-1):
         # lateral esquerda:
         janela.move(y+k, x)
         janela.addch(curses.ACS_VLINE)
         # lateral direita:
         janela.move(y+k, X)
         janela.addch(curses.ACS_VLINE)

   def desenha(self, J: Window) -> None:
      "Escreve figura da barra de progresso na tela do ncurses."
      self._desenha_borda_do_progresso(J)
      self._realiza_preenchimento(J)

   def _seleciona_uma_cor(self) -> None:
      percentual = float(self.percentual)

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

   def _realiza_preenchimento(self, janela: Window) -> None:
      percentual = float(self.percentual)

      if percentual > 1.0:
         raise OverflowError(
            "tem que ser um valor maior ou igual a 1, também, positivo."
         )

      (_, largura) = janela.getmaxyx()
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
      janela.standout()
      for p in range(self._altura - 1):
         x = (self._ponto.x + MARGEM_X)
         y = (p + linha)
         texto_cor = self._seleciona_uma_cor()
         janela.attron(color_pair(texto_cor))
         janela.hline(y, x, BarraProgresso.PROGRESSO_ATOMO, tarja)
         janela.attroff(color_pair(texto_cor))

      janela.standend()

class BarraProgresso(BarraProgresso):
   # criando um descriptor para sua dimensão.
   class Dimensao():
      def __get__(self, instancia, classe):
         return (instancia._altura, instancia._largura)
      def __set__(self, instancia, valor):
         raise AttributeError("ainda não é possível modifica-lá")
   ...
   dimensao = Dimensao()

   def centraliza(self, janela: Window) -> None:
      "centralização do objeto no centro da tela."
      # dimensões da tela e do objeto.
      (H, L) = janela.getmaxyx()
      (h, l) = (self._altura, self._largura)
      # computa o meio, baseado na dimensão
      # do objeto, e também levando a da 'tela'.
      self._cse = Ponto((H - h) // 2, (L - l) // 2)
      # acha os demais cantos e os atualiza.
      self._ajusta_coordenadas()

   def desloca(self, janela: Window, direcao: Direcao, passo: int) -> None:
      "Desloca o objeto na 'direção' dada, por 'n passos'"
      (max_altura, max_largura) = janela.getmaxyx()

      # Renomeando ponto principal para melhor codificação. Também dois 
      # pontos utilizados que são usados repetidamente.
      match direcao:
         case Direcao.DIREITA:
            # Verificando também se tal ordem de movimento não ultrapassa 
            # os limites da 'tela'. Se este for o caso, um erro será lançado.
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
            #self._cse -= Ponto(passo, 0)
            self._cse = self._cse - Ponto(passo, 0)
         case Direcao.BAIXO:
            if self._csd.y + passo >= max_altura:
               raise OverflowError("passa limites da tela")
            self._cse += Ponto(passo, 0)

      # realinha as demais.
      self._ajusta_coordenadas()

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
        Serão preciso o lado onde será anexado, que se usa também a 
      'direção', o espaço entre eles e, e a 'barra de progresso' a ser 
      anexada; para ser honesto, por mais que seja nomeado como uma anexação,      não existe qualquer captura do objeto, apenas o deslocamento dele 
      baseado na instância, tal deslocamento que fica paracendo uma anexação.

      Obs.: a 'margem' dada não podem exceder grandes quantias, uma restrição
         auto imposta; já que "anexações" muitos espaçadas, não pareceriam, 
         bem,... uma "anexação". O limite aqui será 10 caractéres de 
         distância no máximo.
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

# === === === === === === === === === === === === === === === === === === ===
#                       Texto de Informação do Programa 
# === === === === === === === === === === === === === === === === === === ===
class Info(Desenho):
   def __init__(self, texto: str) -> None:
      self.texto = texto
      self.feito = False

   def desenha(self, J: Window, P: Ponto) -> None:
      # Garante que será processado apenas uma vez.
      if (not self.feito):
         self.esboco = ConstroiString(self.texto)
         # Muda estado.
         self.feito = (not self.feito)

      matriz = self.esboco
      (altura, largura) = matriz.dimensao()
      (y, x) = P

      for lin in range(altura):
         for col in range(largura):
            pixel = matriz[lin][col]
            Y = y + lin
            X = x + col
            J.addch(Y, X, pixel)

   def dimensao(self) -> (int, int):
      pass
# === === === === === === === === === === === === === === === === === === ===
#                           Testes Unitários
# === === === === === === === === === === === === === === === === === === ===
from unittest import (TestCase)
from random import (randint)

class Exemplo(TestCase):
   class Percentual(Percentual):
      def varia_aleatoriamente(self) -> float:
         sorteio = randint(2, 99)
         self.numerator = sorteio

         return float(self)

   def runTest(self):
      taxa = Exemplo.Percentual(100)
      instancia = Janela(taxa)
      inicio = time()
      chave = Interruptor(True)
      LIMITE = 15
 
      while ((time() - inicio) < LIMITE) and chave:
         instancia.renderiza()
         console_da_aplicacao(instancia, chave)
         taxa.varia_aleatoriamente()

      del instancia

class DesenhoStringFunciona(TestCase):
   def setUp(self):
      self.entrada_a = ConstroiString("porta")
      self.entrada_b = ConstroiString("02468")
      self.entrada_c = ConstroiString("#-+(!)")

   def runTest(self):
      print(self.entrada_a)
      print(self.entrada_b)
      print(self.entrada_c)
