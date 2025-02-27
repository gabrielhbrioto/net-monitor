PREFIX=/usr/local/bin
SERVICE_DIR=/etc/systemd/system
CONFIG_FILE=/etc/netmon.conf
LOG_DIR=/var/log/netmon
LOG_FILE=$(LOG_DIR)/netmon.log
ERROR_LOG_FILE=$(LOG_DIR)/netmon_error.log
INSTALL_DIR=/usr/local/share/netmon

install:
	@echo "Instalando dependências Python..."
	pip install --upgrade pip
	pip install pandas numpy matplotlib InquirerPy
	
	@echo "Instalando Net Monitor..."
	mkdir -p $(INSTALL_DIR)
	cp netmon.sh analyzer.py $(INSTALL_DIR)/
	chmod +x $(INSTALL_DIR)/netmon.sh
	cp netmon $(PREFIX)/
	chmod +x $(PREFIX)/netmon

	@echo "Criando arquivo de configuração..."
	if [ ! -f $(CONFIG_FILE) ]; then \
	    echo "MAX_LOSS=40" | sudo tee $(CONFIG_FILE) > /dev/null; \
	    echo 'TARGETS=("8.8.8.8" "8.8.4.4" "1.1.1.1" "1.0.0.1")' | sudo tee -a $(CONFIG_FILE) > /dev/null; \
	    echo "INTERVAL=60" | sudo tee -a $(CONFIG_FILE) > /dev/null; \
	    echo "PING_COUNT=5" | sudo tee -a $(CONFIG_FILE) > /dev/null; \
	    echo 'IFACE=""' | sudo tee -a $(CONFIG_FILE) > /dev/null; \
	fi

	@echo "Criando diretório e arquivos de log..."
	mkdir -p $(LOG_DIR)
	touch $(LOG_FILE) $(ERROR_LOG_FILE)
	chmod 644 $(LOG_FILE) $(ERROR_LOG_FILE)
	chown root:root $(LOG_FILE) $(ERROR_LOG_FILE)

	@echo "Instalando serviço systemd..."
	cp netmon.service $(SERVICE_DIR)/
	systemctl daemon-reload
	systemctl enable netmon.service

	@echo "Instalação concluída! Use 'netmon help' para ver os comandos disponíveis."

uninstall:
	@echo "Desinstalando Net Monitor..."
	rm -f $(PREFIX)/netmon
	
	@echo "Removendo arquivos do projeto..."
	rm -f $(INSTALL_DIR)/netmon.sh $(INSTALL_DIR)/analyzer.py
	rm -rf $(INSTALL_DIR)

	@echo "Removendo serviço systemd..."
	systemctl disable netmon.service
	rm -f $(SERVICE_DIR)/netmon.service
	systemctl daemon-reload
	
	@echo "Removendo arquivo de configuração..."
	rm -f $(CONFIG_FILE)
	
	@echo "Removendo diretório e arquivos de log..."
	rm -rf $(LOG_DIR)

	@echo "Desinstalação concluída!"

.PHONY: install uninstall help
