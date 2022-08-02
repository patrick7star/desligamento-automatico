
from forma_palavras import forma_texto, forma_palavras,CENTRO,ESQUERDA,DIREITA
from biblioteca.moldura_str import imprime

palavras = forma_palavras("isso é um dia incrívelmente triste")

print("alinhamento padrão, à esquerda:")
texto = forma_texto(palavras, alinhamento=ESQUERDA)
for linha, P in texto.items(): imprime(P)

print("\nalinhamento padrão no centro:")
texto = forma_texto(palavras, alinhamento=CENTRO)
for linha, P in texto.items(): imprime(P)


print("\nalinhamento padrão, à direita:")
texto = forma_texto(palavras, alinhamento=DIREITA)
for linha, P in texto.items(): imprime(P)
