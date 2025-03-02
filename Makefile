
DIR = ../versões
NOME = desligamento-automatico
VERSAO = v1.1.0

salva:
	@tar --wildcards --exclude=*pycache* -cvf $(DIR)/$(NOME).$(VERSAO).tar \
		Makefile *.txt lib/ src/ data/

lista-backups:
	@echo "\nTodas versões salvas:\n"
	@ls -1 --sort=time -sh ../versões/desligamento-automatico*

# Função apenas funciona na máquina do desenvolvedor:
importa-libs:
	@cp -uv $(PYTHON_CODES)/python-utilitarios/lib/tempo.pyc $(PYTHON_CODES)/python-utilitarios/lib/legivel.pyc lib/
