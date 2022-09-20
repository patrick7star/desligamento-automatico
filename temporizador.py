
from time import time

class TempoEsgotadoError(Exception):
   def __str__(self):
      return "O temporizador não pode atualizar mais."
...

class Temporizador:
   def __init__(self, tempo):
      " tempo é dado em segundos"
      # segundos registrado até agora de uma 
      # data inicial marcada, convertido a um
      # valor inteiro.
      self._registro_inicial = int(time())
      self._limite = tempo
      # marco inicial.
      self._atual = 0
      self._terminado = False
      self._ciclos = 0
   ...

   def __call__(self):
      """
      chamada, atualiza tempo decorrido. Se alcançou
      o tempo delimitado. Retorna True em cada chamada
      validando a existência do Temporizador, False caso
      tenha sido esgotado. Se houver insistência em
      chamar mesmo assim, uma exceção será levantada.
      """
      if self._atual >= self._limite: 
         self._terminado = True
         if self._terminado:
            if self._ciclos > 5:
               raise TempoEsgotadoError()
            else:
               self._ciclos += 1
         return False
         ...
      ...

      # atualizando atual tempo decorrido.
      self._atual = time() - self._registro_inicial
      return True
   ...

   def percentual(self):
      "verifica o percentual decorrido em segundos"
      return self._atual / self._limite
   ...

   def agendado(self):
      "tempo agendado para contagem regressiva"
      # primeiro atualizando o tempo ...
      self(); return self._limite

   def __lt__(self, tempo) -> bool:
      # primeiro atualizando o tempo ...
      self()
      # contagem atual está em ...
      contagem = self._limite - self._atual
      return contagem <= tempo
   ...

   def __gt__(self, tempo) -> bool:
      # primeiro atualizando o tempo ...
      self()
      # contagem atual está em ...
      contagem = self._limite - self._atual
      return contagem > tempo
   ...
...

def stringtime_to_segundos(string):
   caracteres = []
   # remove todos espaços brancos.
   for char in string:
      if not char.isspace():
         caracteres.append(char)
   ...
   # acha divisor entre peso e parte numérica.
   marco = None
   for (i, char) in enumerate(caracteres):
      if char.isalpha():
         marco = i
         break
      ...
   ...
   # transformando em respectivos objetos.
   digitos = float(''.join(caracteres[0:marco]))
   peso = ''.join(caracteres[marco:])

   if marco == None:
      raise Exception("argumento mal formado: %s" % string)

   if peso.startswith("min") or peso == "m":
      return digitos * 60
   elif peso.startswith("seg") or peso == "s":
      return digitos
   elif peso.startswith("hora") or peso == "h":
      return digitos * 3600
   elif peso.startswith("dia") or peso == "d":
      return digitos * 3600 * 24
   else:
      raise Exception("não implementado para tal")
...


if __name__ == "__main__":
   import utilitarios.src.testes as UT
   from time import sleep 

   def strtime_to_seg():
      argumentos = (
         "15min", "38 segundos", "3.5 horas",
         "15.0 min", "38 seg", "3h", "4.53 h",
         "5.8 min    ", "   89     segundos", 
         "3      hfak",  " 12   dios",
      )
      for arg in argumentos:
         try:
            conversao = stringtime_to_segundos(arg)
            print("%s ==> %iseg" % (arg, conversao))
         except:
            print("[%s] mal formado!!" % arg)
         ...
      ...
   ...

   def usa_temporizador():
      t = Temporizador(stringtime_to_segundos("13seg"))
      while t():
         porcentagem = t.percentual() * 100
         print("\r%0.1f%%" % porcentagem, end = '')
      else:
         print("esgotado!".upper())
      ...

      # induzindo ao erro.
      for _ in range(15):
         try: 
            print("resultado: ", t())
         except TempoEsgotadoError():
            print("induzido com sucesso!")
            break
         ...
      ...
   ...

   def comparaTemporizador():
      tempo = stringtime_to_segundos("1.3min")
      a = Temporizador(tempo)
      sleep(20)
      # está em 58seg
      print("agora têm que ser menor que 59.")
      assert a < 59
      print("agora têm que ser menor que 51.")
      sleep(7)
      assert a < 51
   ...

   """
   UT.executa_teste(strtime_to_seg)
   try:
      UT.executa_teste(usa_temporizador)
   except:
      print("perfeito!!!")
   """
   UT.executa_teste(comparaTemporizador)
...
