install:
	@echo "Instalando dependências Python..."
	pip install --upgrade pip
	pip install pandas numpy matplotlib InquirerPy
	
	@echo "Copiando scripts..."
	mkdir -p /usr/local/share/netmon
	cp netmon.sh analyzer.py /usr/local/share/netmon/
	chmod +x /usr/local/share/netmon/netmon.sh

	@echo "Instalando o comando netmon..."
	cp netmon /usr/local/bin/
	chmod +x /usr/local/bin/netmon

	@echo "Criando arquivo de configuração..."
	if [ ! -f /etc/netmon.conf ]; then \
	    echo "MAX_LOSS=60" | sudo tee /etc/netmon.conf > /dev/null; \
	    echo 'TARGETS=("8.8.8.8" "8.8.4.4" "1.1.1.1" "1.0.0.1")' | sudo tee -a /etc/netmon.conf > /dev/null; \
	fi

	@echo "Instalando serviço systemd..."
	cp netmon.service /etc/systemd/system/
	systemctl daemon-reload
	systemctl enable netmon.service

	@echo "Instalação concluída! Use 'netmon help' para ver os comandos disponíveis."
