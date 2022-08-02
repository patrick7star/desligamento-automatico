# Módulo tem como utilidade emoldurar strings.
# Porém, para isso será necessário primeiro 
# matriciar a string, ou seja, pegar a linha 
# como maior string, e contar tal string para
# ser as colunas do códigos. Contando as quantidade
# de linhas é preciso apenas... contar a quantia
# de linhas.

# transforma a string numa matriz, baseado nas
# quebras de linhas dela, onde tal, será a quantia
# de linhas, e as colunas baseada na linha 
# contendo a maior string.
def matriciar(_str):
	# obtendo as dimensões possíveis da string.
	# m - nº de linhas.
	# n - nº de colunas.
	# k - valor para indexar o caractére da string.
	linhas_str = _str.split('\n')
	n = max(len(s) for s in linhas_str)
	# criando matriz baseado nas dimensões obtidas.
	matriz = [list(linha) for linha in _str.split('\n')]
	# corrigindo linhas irregulares.
	for linha in matriz:
		while len(linha) != n: linha.append(' ')
	return matriz

# imprime a matriz da string "matriciada".
def imprime(matriz):
	# dimensões da matriz.
	(m,n) = (len(matriz), len(matriz[0]))
	# percorrendo e imprimindo.
	for i in range(m):
		# imprime os cactéres na mesma linha 
		# representando colunas.
		for j in range(n): print(matriz[i][j],end='')
		print('') # pula para próxima linha.

# Emoldura a string, retornando uma nova string.
# A função também tem como parâmetro o símbolo que 
# deseja que esteja na moldura.
def emoldura(_str, simbolo = '+'):
	# faz da string uma matriz.
	M = matriciar(_str)
	# pega dimensões da matriz.
	(m, n) = len(M), len(M[0])
	# adicionando primeiro as laterais.
	for linha in M:
		linha.append(simbolo)
		linha.insert(0,simbolo)
	# adicinando arresta superior e inferior.
	barra = list(simbolo * (n+2))
	M.insert(0,barra) # superior.
	M.insert(m,barra) # inferior.
	# transformando a matriz numa string novamente.
	nova_str = ''
	n = max(len(l) for l in M)
	# atualizando dimensões novamente.
	for i in range(m+1):
		for j in range(n): nova_str += M[i][j]
		nova_str += '\n'
	# retornando string emoldurada com o caractére passado.
	return nova_str

if __name__ == '__main__':

	string = 'rosas são vermelhas\nvioletas são azuis\npreciso de uma rima maneira\npara usar com exemplooo'

	outro_poema = 'sabão crá-crá, sabão-crá-crá\nnão deixa os pelos do s*** enrolar.'


	# emoldurando poeminha...
	print(emoldura(string))

	# emoldurando outro poemia.
	print(emoldura(outro_poema))
