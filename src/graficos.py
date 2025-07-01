"""
   Aqui cuida-se especificamente da parte gráfica do programa. Sera feita
 no 'ncurses' do Python especificamente.
"""
# o que será exportado:
__all__ = [ "PROGRESSO_ATOMO", "inicia_grafico", "Acao"]

# Importa biblioteca externa:
from externo import (tempo as ul_tempo, forma_string, Temporizador)
# Biblioteca do Python:
import curses
# Próprios módulos do projeto:
from progresso import (BarraMinuto, BarraProgresso, Direcao, Ponto)
from janelas import *

# constantes de personalização.
PROGRESSO_ATOMO = ' '


# === === === === === === === === === === === === === === === === === === =
#                       Implementações das Funções
# === === === === === === === === === === === === === === === === === === =
def controle_do_teclado(janela: curses.window) -> None:
   try:
      code = janela.getch()
      tecla = chr(code).lower()
   except ValueError:
      tecla = 'a'
   finally: pass

   if tecla == 's':
      del janela
      raise KeyboardInterrupt("tecla certa 's' foi pressionada")

def inicia_grafico(timer, mensagem_final="desligando",
  acao=Acao.Desliga) -> None:
   """
     A execução de todo o visual do programa, do seu arranjo de tela, até
   a animação que ele toca.
   """
   # inclui contagem regressiva no minuto final.
   if __debug__:
      MEIA_HORA = 60 * 5 // 2
   else:
      MEIA_HORA = 3600 // 2

   janela = Janela(1.2, Janela.TAXA_PADRAO, acao=acao, timer=timer)
   barra_acionada = False
   outra_barra = timer > MEIA_HORA

   (H, L) = janela.dimensao()
   barL = int(L * 0.70)
   (Y, X) = ((H - 5)// 2, (L - barL) // 2)
   meio = Ponto(Y, X)
   barra = BarraProgresso(janela.ref, posicao=meio, largura=barL, altura=5)
   barraminuto = BarraMinuto(
      janela.ref, altura=3, posicao = (meio + Ponto(5, 0)),
      largura = int(L * 0.70 * 0.70),
   )
   segs = timer.agendado().total_seconds()
   info = Info(janela.ref, ul_tempo(segs, acronomo=True, arredonda=True))
   # Grava dimensão atual da janela, e centralização inicial das barras.
   atual_dimensao = janela.dimensao()
   barra.centraliza()
   barraminuto.centraliza()

   # Adiciona objetos extras a janela que os desenha e renderiza.
   janela += barra
   janela += barraminuto
   janela += info
   temporizador_ja_criado = False

   while timer():
      # Qualquer pressionamento de tecla, será tradado na função abaixo.
      controle_do_teclado(janela.ref)

      if janela.dimensao() != atual_dimensao:
         # Centraliza barra se necessário. Também atualiza atual dimensão.
         centralizas_barras(barra, barraminuto)
         atual_dimensao = janela.dimensao()

      decorrido = timer.agendado().total_seconds()
      contagem_str = ul_tempo(decorrido, arredonda=True, acronomo=True)
      info_de_tempo(janela.ref, contagem_str)
      barra.atualiza(1.0 - timer.percentual())

      # Troca para o timer de 1min. só se o timer foi marcado com mais de
      # meia-hora.
      if outra_barra:
         if timer < 60:
            restante = Temporizador(60)
            barraminuto.aciona_visibilidade()
            temporizador_ja_criado = True

      # Desenha janela, e todos objetos incluido nela na inicialização, ou
      # posteriormente.
      janela.renderizar()

   else:
      # cria texto-desenhado.
      texto_matriz = forma_string(mensagem_final)
      (l, h) = (len(texto_matriz[0]), len(texto_matriz))
      # computação CSE para desenhar o texto-desenhado.
      posicao = posicao_centralizada(janela.ref, h, l)
      # desenha em sí o texto-desenhado.
      escreve_no_curses(janela.ref, posicao, texto_matriz)
      janela.ref.refresh()
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

def escreve_no_curses(janela, ponto, texto_matriz):
   M = texto_matriz
   (altura, largura) = (len(M),len(M[0]))
   (y, x) = (ponto.y, ponto.x)

   for lin in range(altura):
      for col in range(largura):
         janela.addch(y+lin, x+col, M[lin][col])
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

class Info:
   def __init__(self, janela: curses.window, msg: str) -> None:
      (Ymax, Xmax) = janela.getmaxyx()
      texto_grade = forma_string(msg)
      # Largura e altura, nesta ordem:
      (L, H) = (len(texto_grade[0]), len(texto_grade))
      self.dimensao = (L, H)
      self.grade_msg = forma_string(msg) 
      self.msg = msg
      self.janela = janela
      # Posição do objeto.
      self.Y = Ymax // 2 - (H + 3)
      self.X = (Xmax - L) // 2

   def desenha(self) -> None:
      (Y, X) = (self.Y, self.X)

      for y in range(self.dimensao[1]):
         for x in range(self.dimensao[0]):
            self.janela.addch(Y + y, X + x, self.grade_msg[y][x])
# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
# === === === === === === === === === === === === === === === === === === =
from os import get_terminal_size
from random import randint
from unittest import (TestCase, main, skip, skipIf)

class IniciaGraficos(TestCase):
   """
   testes/e protótipos de vários layouts
   que podem ser aplicados à programa. Primeiro,
   é claro, serão aplicados aqui.
   """
   def modeloAntigo(self):
      janela = Janela(
         3.5, Janela.TAXA_PADRAO,
         rotulo="modo debug"
      )
      # mais de cinco minutos
      timer = Temporizador(320)

      # inclui contagem regressiva no minuto final.
      MEIA_HORA = 60 * 5 // 2
      barra_acionada = False
      outra_barra = timer > MEIA_HORA

      # importando aqui dentro, pois pode criar
      # algo circular, se feito na 'main thread'
      # do programa. Como tal função é chamada
      # apenas uma vez por execução, o custo
      #computacional não será tão grande.
      from progresso import (Ponto, BarraProgresso, Direcao)
      global Ponto, BarraProgresso

      def centralizas_barras(b, bm):
         b.centraliza()
         b.anexa(Direcao.BAIXO, bm)
         (N, n) = (b.dimensao[1], bm.dimensao[1])
         bm.desloca(Direcao.BAIXO, 2)
         # computando deslocamento horizontal.
         bm.desloca(Direcao.DIREITA, (N-n)//2)
      ...
      #desenha_barra(janela)
      (H, L) = janela.dimensao()
      largura_barra = int(L * 0.70)
      meio = Ponto((H-5)//2, (L-largura_barra)//2)
      barra = BarraProgresso(
         janela.ref, posicao=meio,
         largura=largura_barra,
         altura=5
      )
      barraminuto = BarraProgresso(
         janela.ref, altura=3,
         posicao=(meio + Ponto(5, 0)),
         largura = int(L * 0.70 * 0.70),
         mais_cores=True
      )
      # grava dimensão atual da janela.
      atual_dimensao = janela.dimensao()
      # centralização inicial.
      centralizas_barras(barra, barraminuto)

      while timer():
         # centraliza barra se necessário.
         if janela.dimensao() != atual_dimensao:
            centralizas_barras(barra, barraminuto)
            # valor atual foi atualizado.
            atual_dimensao = janela.dimensao()

         contagem_str = ul_tempo(
            timer.agendado().total_seconds(),
            arredonda=True,
            acronomo=True
         )
         info_de_tempo(janela.ref, contagem_str)
         percentual = 1.0 - timer.percentual()
         barra.preenche(percentual)

         # Renderização ...
         if timer.percentual() < 0.05:
            barraminuto.aciona_visibilidade()
         janela.desenha()

         # atualização de tela em quase 1min.
         janela.congela(0.8)
         janela.limpa()
      else:
         janela.limpa()
         # cria texto-desenhado.
         texto_matriz = forma_string("desligando")
         (l, h) = (len(texto_matriz[0]), len(texto_matriz))
         # computação CSE para desenhar o texto-desenhado.
         posicao = posicao_centralizada(janela.ref, h, l)
         # desenha em sí o texto-desenhado.
         escreve_no_curses(janela.ref, posicao, texto_matriz)
         janela.renderiza()

   def buscandoLayoutIdeal(self):
      janela = JanelaDebug()
      janela.aumenta_tempo_limite(5.1)
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
      # ajustando as barras.
      barra_geral.centraliza()
      barra_minuto.centraliza()
      barra_minuto.desloca(Direcao.BAIXO, 6)
      # preenchendo apenas para visualização.
      barra_minuto.preenche(randint(20, 100)/100)
      barra_geral.preenche(randint(30, 90)/100)
      # renderização...
      barra_geral(); barra_minuto()
      janela.encerra()
   ...
   @skip("ainda não finalizado!")
   def barraPopupDinamismo(self):
      janela = JanelaDebug()
      (_, L) = janela.dimensao()
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
      L = (lambda j: j.dimensao()[1])

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
         janela.limpa()
      ...
      janela.encerra()
   ...
   @skipIf(
     get_terminal_size().columns < 151,
     "tela muito pequena para esboçar desenhos"
   )
   def layoutParaTelaCheia(self):
      janela = JanelaDebug()
      janela.aumenta_tempo_limite(4.3)
      (H, L) = janela.dimensao()
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
         #curses.napms(1100)
         janela.congela(1.1)
         janela.limpa()
      ...
      janela.encerra()
   ...
   def barraMinutoAtiva(self):
      janela = JanelaDebug()
      info_de_tempo(janela.ref, "2min")
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
      # ajustando as barras.
      barra_geral.centraliza()
      barra_minuto.centraliza()
      barra_minuto.desloca(Direcao.BAIXO, 6)
      # temporizadores para cada barra.
      contador_reverso = Temporizador(120)
      contador_reversoI = Temporizador(30)
      while contador_reverso():
         # resetando o contador da barra-minuto.
         if not contador_reversoI():
            contador_reversoI = Temporizador(30)
         info_de_tempo(janela.ref, "2min")
         # preenchendo apenas para visualização.
         pBG = 1.0 - contador_reverso.percentual()
         pBM = 1.0 - contador_reversoI.percentual()
         barra_minuto.preenche(pBM)
         barra_geral.preenche(pBG)
         # renderização...
         barra_geral(); barra_minuto()
         curses.napms(500)
         # apagando tudo para reescreve novamente.
         janela.limpa()
      ...
      janela.encerra()
   ...

   def simples_carregamento_das_barras(self):
      screen = Janela(1.2, Janela.TAXA_PADRAO)

      (H, L) = janela.dimensao()
      l = int(L * 0.70)
      (Y, X) = ((H - 5)// 2, (L - l) // 2)
      meio = Ponto(Y, X)
      barA = BarraProgresso(screen.ref, posicao=meio, largura=barL, altura=5)
      barB = BarraMinuto(
         janela.ref, altura=3, posicao = (meio + Ponto(5, 0)),
         largura = int(L * 0.70 * 0.70),
      )

      atual_dimensao = screen.dimensao()
      barA.centraliza()
      barB.centraliza()

      screen += barra
      screen += barraminuto

      for p in range(40):
         if screen.dimensao() != atual_dimensao:
            centralizas_barras(barA, barB)
            atual_dimensao = screen.dimensao()

         barA.preenche(100 * (p / 40))
         barB.preenche(1.0 - (p / 2 / 40))
         janela.renderizar()

if __name__ == "__main__":
   main(verbose=1)
