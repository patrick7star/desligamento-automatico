
import biblioteca.utilitarios as BU
import biblioteca.moldura_str as BM
import forma_palavras as FP

# letras e números a serem mesclados numa só matriz.
c1 = BU.numero_desenho(8)
c2 = BU.numero_desenho(5)
c3 = BU.numero_desenho(3)
c4 = BU.letra_desenho('A')
c5 = BU.letra_desenho('B')
c6 = BU.letra_desenho('C')
c7 = BU.letra_desenho('D')

BM.imprime(BU.mescla_matrizes(c4,c5,c6,c7,c1,c2,c3))

frase = FP.forma_string("num42")
BM.imprime(frase)
BM.imprime(FP.forma_string("1000"))

for P in FP.forma_palavras("isso é o teste 832"):
   BM.imprime(P)

LINHAS = FP.forma_texto(FP.forma_palavras("isso é um teste 832")).values()
for linha in LINHAS:
   BU.imprime(linha)


