
# o que será importado.
__all__ = ["Janela", "Acao", "PapeisP", "PapeisB", "Cores"]

from curses import *
from time import (time as mede_tempo, strftime, gmtime, localtime)
from enum import (auto, IntEnum, Enum)
from datetime import (datetime as DT, timedelta)
from utilitarios.legivel import (tempo as Tempo)
from tempo_ligado import *

class Cores(IntEnum):
   VerdeEscuro = 96
   Vermelho     = auto()
   Amarelo      = auto()
   Verde        = auto()

class PapeisP(IntEnum):
   # Papeis de paredes.
   Amarelo      = 80
   Vermelho     = auto()
   Azul         = auto()
   Violeta      = auto()
   Verde        = auto()

class PapeisB(IntEnum):
   # Papeis de paredes.
   Amarelo      = 70
   Vermelho     = auto()
   Azul         = auto()
   Violeta      = auto()
   Verde        = auto()

class Acao(Enum):
   Suspende = auto()
   Desliga = auto()

   def __str__(self) -> str:
      match self:
         case Acao.Suspende:
            return "Suspensão"
         case Acao.Desliga:
            return "Desligamento"
         case _ :
            raise Exception("Não implementado para tal")

class Horario:
   def __init__(self) -> None:
      self.formatacao = ""
      pass

   def desenha(self, tela: window, Y: int, X: int):
      horario = localtime()
      self.formatacao = strftime(" %2H:%2M ", horario)

      tela.attron(A_UNDERLINE)
      tela.addstr(Y, X, self.formatacao, color_pair(PapeisP.Violeta))
      tela.attroff(A_UNDERLINE)

   def __len__(self) -> int:
      return len(self.formatacao)

class AtualAcao:
   BRANCO = ord(' ')
   SIMBOLO = ord('.')
   LIMITE = 0.9
   MAX = 5

   def __init__(self, texto):
      assert isinstance(texto, str)

      # Cronometragem de tempo.
      self.inicio = mede_tempo()
      self.contagem = 0
      self.mensagem = texto
      self.impressao = bytearray(texto, encoding="latin1")
      self.limite = AtualAcao.MAX

      for _ in range(self.limite):
         char = AtualAcao.BRANCO
         self.impressao.append(char)

      # Acochoa o ínicio para não ficar grudados com outros externos.
      # É obrigatório contabilizar tal inserção nos índices e cálculos
      # de comprimentos abaixo.
      char = AtualAcao.BRANCO
      self.impressao.insert(0, char)

   def desenha(self, tela: window, Y: int, X: int):
      assert isinstance(tela, window)
      assert isinstance(Y, int)
      assert isinstance(X, int)

      # Computa tempo decorrido desde o íncio da última cronometração.
      decorrido = mede_tempo() - self.inicio

      if decorrido >= AtualAcao.LIMITE:
         code = AtualAcao.SIMBOLO
         t = len(self.mensagem)
         # Computa índice do próximo caractére preenchido na string.
         M = AtualAcao.MAX
         c = self.contagem
         self.impressao[t + 1 + (c % M)] = code
         self.contagem += 1
         # Reseta recontagem de tempo.
         self.inicio = mede_tempo()

      # Limpa parte pontinhada novamente, se atingiu o limite.
      if self.contagem % AtualAcao.MAX == 0:
         for p in range(AtualAcao.MAX):
            t = len(self.mensagem)
            char = AtualAcao.BRANCO
            self.impressao[t + 1 + p] = char

      msg = self.impressao.decode(encoding="latin1")
      cor = color_pair(PapeisP.Amarelo)

      tela.attron(A_BOLD)
      tela.addstr(Y, X, msg, cor)
      tela.attroff(A_BOLD)

   def __len__(self) -> int:
      return len(self.mensagem) + 1 + AtualAcao.MAX

class Debug:
   def __init__(self):
      if __debug__:
         self.msg = " modo debug "
      else:
         self.msg = " Normal "

   def desenha(self, tela: window, Y: int, X: int):
      assert isinstance(tela, window)
      assert isinstance(Y, int)
      assert isinstance(X, int)

      if __debug__:
         cor = int(PapeisP.Vermelho)
         tela.attron(A_BOLD)
         tela.addstr(Y, X, self.msg, color_pair(cor))
         tela.attroff(A_BOLD)
      else:
         cor = int(PapeisB.Azul)
         tela.attron(A_BOLD)
         tela.addstr(Y, X, self.msg, color_pair(cor))
         tela.attroff(A_BOLD)


   def __len__(self):
      return len(self.msg)

class BarraStatus:
   def __init__(self, janela, lista: list):
      assert isinstance(lista, list)
      assert isinstance(janela, window)

      self.tela = janela
      self.objetos = lista
      m = 0
      lengths = map(lambda o: len(o) + m, lista)
      self.X = 1 + sum(lengths)

   def desenha(self) -> None:
      (y, x) = self.tela.getmaxyx()
      tela = self.tela
      Y = y - 2; X = 1

      for obj in self.objetos:
         obj.desenha(tela, Y, X)
         X += len(obj)

class Percentual:
   def __init__(self, timer) -> None:
      self.inicial = 1.0
      # Referência do temporizador, para calcular o percentual.
      self.contador = timer
      p = self.contador.percentual() * 100.0
      self.formatacao = " {:3.0f}% ".format(p)

   def atualiza(self):
      p = self.contador.percentual() * 100.0
      self.formatacao = " {:3.0f}% ".format(p)

   def desenha(self, tela: window, Y: int, X: int):
      self.atualiza()
      tela.attron(A_DIM)
      tela.addstr(Y, X, self.formatacao, color_pair(PapeisP.Vermelho))
      tela.attroff(A_DIM)

   def __len__(self) -> int:
      return len(self.formatacao)

def definicoes_de_todas_cores() -> None:
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

class SistemaLigado:
   "LED que informa quanto tempo este computador já está ligado."
   def __init__(self) -> None:
      (self.segundos, _) = tempos_importantes()
      self.contador = DT.today()
      vl = self.segundos.total_seconds()
      self.fmt = (lambda X: " Ligado: %s " % Tempo(X))
      self.formatacao = self.fmt(vl)

   def atualiza(self):
      """
        Obtém o novo valor do tempo ligado(em segundos), baseado no quanto
      está ligado. Isso porque não faz sentido algo que já avançou horas,
      ficar verificando novos valores a cada quantia de segundos, não
      mudaria nada numa visualização humana no LED.
      """
      decorrido = DT.today() - self.contador
      MARCOS = (
         timedelta(minutes=2),
         timedelta(minutes=5),
         timedelta(hours=1)
      )

      """
        Caso esteja no estágio de minutos, inicial(mais que dois minutos),
      então atualiza a cada 30 segundos, já o estágio médio atualização de
      um em um minuto; no caso avançado, então é ritmo é 5min. Em horas,
      ou maior que isso, aí fica eterno a atualização de 32min.
      """
      # 2min à 5min:
      primeira_faixa = (decorrido >= MARCOS[0] and decorrido < MARCOS[1])
      # 5min à 1h:
      segunda_faixa = (decorrido >= MARCOS[1] and decorrido < MARCOS[2])
      # 1h ao infinito:
      terceira_faixa = (decorrido >= MARCOS[1])

      if primeira_faixa:
         LIMITE = timedelta(seconds=30)
      elif segunda_faixa:
         LIMITE = timedelta(minutes=1)
      elif terceira_faixa:
         LIMITE = timedelta(minutes=32)
      else:
         # Para valore abaixo de 2min, atualiza com o frame do ncurses.
         LIMITE = timedelta(seconds=0)
         pass

      if decorrido < LIMITE :
         segs = self.segundos.total_seconds()
         self.formatacao = self.fmt(segs)
         (a, _) = tempos_importantes()
         self.segundos = a
         # Atualiza o contador ...
         self.contador = DT.today()

   def desenha(self, tela: window, Y: int, X: int):
      cor = PapeisB.Verde

      self.atualiza()
      tela.attron(A_DIM)
      tela.addstr(Y, X, self.formatacao, color_pair(cor))
      tela.attroff(A_DIM)

   def __len__(self) -> int:
      return len(self.formatacao)

def cria_janela_e_a_configura() -> window:
   "Cria janela geral de desenho, configura-a e retorna para o chamador."
   janela = initscr()

   # sua configuração:
   start_color()
   use_default_colors()
   curs_set(0)
   # adicionado captura de tecla.
   nocbreak()
   janela.nodelay(True)

   return janela

class Janela():
   """
      Criando uma janela à partir da versão 'debug', deveria ter sido o 
   inverso, mas enfim. Está contém threading, portanto executas buscas, 
   impressões e etc, indepedente se foi chamada para fazer tal.
   """
   # Taxa padrão para atualização de 'quadros' em milisegundos.
   TAXA_PADRAO = 800

   def __init__(self, segundos, taxa_atualizacao, automatico=False,
     rotulo=None, acao=Acao.Desliga, timer=None) -> None:
      self._atualizacao = automatico
      # taxa de atualização dos quadros da janela.
      if taxa_atualizacao is None:
         self._taxa = Janela.TAXA_PADRAO / 1000
         # só inicia se for exigido.
      else:
         self._taxa = taxa_atualizacao
      if segundos > 20 or segundos < 0.5:
         # para pegar as codificações antigas.
         erro = "mais de 20seg não é permitido, ou menos que meio segundo"
         raise OverflowError(erro)

      # Converte o tempo passado em segundos para miliseg.
      self._tempo_limite = int(segundos * 1_000)
      self._acao = acao
      self._janela = cria_janela_e_a_configura()
      # Iniciando pares de cores que se pode usar na construção.
      definicoes_de_todas_cores()

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
      # Objetos que ela contém:
      self.componentes = []
      self.status = BarraStatus(
         self._janela,
         [
            Horario(), Debug(),
            AtualAcao(str(self._acao)),
            Percentual(timer),
            SistemaLigado()
         ]
      )

   def encerra(self):
      "Encerra a parte semi-gráfica de a janela(o ncurses) em sí."
      napms(self._tempo_limite)
      endwin()

   def referencia(self):
      return self._janela

   ref = property(referencia, None, None, None)

   def _marca_dagua(self, mensagem):
      # ciclos do loop infinito.
      (y, x) = self._janela.getmaxyx()
      X = x - len(mensagem) - 2
      Y = y - 2
      self._janela.addstr(Y, X, mensagem, A_BLINK | A_ITALIC)

   def dimensao(self):
      """
      Retorna a dimensão da janela, que é a mesma da tela principal do
      ncurses
      """
      return self._janela.getmaxyx()

   def __del__(self):
      "Operador explicíto para o método 'encerrar', portanto faz o mesmo."
      self.encerra()

   def desenha(self):
      """
      Desenha componentes da própria janela, assim como objetos externos 
      adicionados.
      """
      self.status.desenha()
      for obj in self.componentes:
         obj.desenha()

   def renderizar(self):
      self._janela.clear()
      self._janela.refresh()
      self.desenha()
      self._janela.refresh()
      napms(int(1.0 * 1.0e3))

   def __iadd__(self, obj):
      "Método, usando de operador para adicionar componentes externos."
      self.componentes.append(obj)
      return self
...

            
