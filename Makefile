PREFIX=/usr/local/bin
SERVICE_DIR=/etc/systemd/system
PYTHON_ENV=/usr/local/share/netmon/env

help:
	@echo "Makefile para instalar o NetMon"
	@echo "Comandos disponíveis:"
	@echo "  make install     - Instala o serviço e dependências"
	@echo "  make uninstall   - Remove o serviço e arquivos do projeto"
	@echo "  make help        - Exibe esta mensagem de ajuda"

install:
	@echo "Instalando dependências Python..."
	pip install --upgrade pip
	pip install pandas numpy matplotlib InquirerPy
	
	@echo "Instalando o comando netmon..."
	mkdir -p /usr/local/share/netmon
	cp netmon.sh analyzer.py /usr/local/share/netmon/
	chmod +x /usr/local/share/netmon/netmon.sh
	cp netmon $(PREFIX)/
	chmod +x $(PREFIX)/netmon

	@echo "Instalando serviço systemd..."
	cp netmon.service $(SERVICE_DIR)/
	systemctl daemon-reload
	systemctl enable netmon.service

	@echo "Instalação concluída! Use 'netmon help' para ver os comandos disponíveis."

uninstall:
	@echo "Desinstalando netmon..."
	rm -f $(PREFIX)/netmon
	
	@echo "Removendo arquivos do projeto..."
	rm -rf /usr/local/share/netmon
	
	@echo "Removendo serviço systemd..."
	systemctl disable netmon.service
	rm -f $(SERVICE_DIR)/netmon.service
	systemctl daemon-reload
	
	@echo "Desinstalação concluída!"

.PHONY: install uninstall help
