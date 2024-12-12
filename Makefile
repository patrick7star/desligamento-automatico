
DIR = ../versões
NOME = desligamento-automatico
VERSAO = v1.1.0

salva:
	@tar --wildcards --exclude=*pycache* -cvf $(DIR)/$(NOME).$(VERSAO).tar \
		Makefile *.txt lib/ src/ data/

lista-backups:
	@echo "\nTodas versões salvas:\n"
	@ls -1 --sort=time -sh ../versões/desligamento-automatico*
