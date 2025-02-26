#!/bin/bash

# Endereços para testar conectividade
TARGETS=("8.8.8.8" "8.8.4.4" "1.1.1.1" "1.0.0.1" "208.67.222.222" "208.67.220.220")
INTERFACE="wlan0"
TOTAL_LOSS=60

# Função para logar mensagens
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" 
}

# Função para testar conectividade
check_connectivity() {

    local RETRIES=2
    for ((i=1; i<=RETRIES; i++)); do
        for TARGET in "${TARGETS[@]}"; do

            # Executa o ping e armazena a saída completa em uma variável
            PING_OUTPUT=$(ping -c 5 -W 5 "$TARGET" 2>&1)

            # Captura a perda de pacotes ou "A rede está fora de alcance"
            LOSS=$(echo "$PING_OUTPUT" | grep -oP '\d+(?=% perda de pacote)|A rede está fora de alcance')

            if [[ $LOSS == "A rede está fora de alcance" ]]; then

                log_message "network=None  signal=0 %  packet-loss=100 %  rtt-min=null ms    rtt-med=null ms    rtt-max=null ms   rtt-dev=null ms"
                return 1
            fi

            # Captura as estatísticas de tempo de resposta (mín/méd/máx/mdev)
            RTT=$(echo "$PING_OUTPUT" | grep -oP 'rtt mín/méd/máx/mdev = [\d\.]+/[\d\.]+/[\d\.]+/[\d\.]+ ms')

            if [[ -n "$RTT" ]]; then
                # Remove "rtt mín/méd/máx/mdev = " da string
                RTT_VALUES=$(echo "$RTT" | awk -F' = ' '{print $2}' | awk '{print $1}')

                # Separa os valores (mín, méd, máx, mdev) usando "/"
                MIN=$(echo "$RTT_VALUES" | awk -F'/' '{print $1}')
                MED=$(echo "$RTT_VALUES" | awk -F'/' '{print $2}')
                MAX=$(echo "$RTT_VALUES" | awk -F'/' '{print $3}')
                MDEV=$(echo "$RTT_VALUES" | awk -F'/' '{print $4}')
            fi
            
            # Se a perda de pacotes for menor que o limite, obtém a intensidade do sinal e loga as informações
            if [ "$LOSS" -lt "$TOTAL_LOSS" ]; then

                INFO=$(nmcli -t -f active,ssid,signal dev wifi | grep '^sim')
                SSID=$(echo "$INFO" | awk -F':' '{print $2}')
                SIGNAL=$(echo "$INFO" | awk -F':' '{print $3}')

                log_message "network=$SSID  signal=$SIGNAL %  packet-loss=$LOSS %  rtt-min=$MIN ms    rtt-med=$MED ms    rtt-max=$MAX ms   rtt-dev=$MDEV ms"
                return 0
            fi
        done
        sleep 1
    done
      
    log_message "network=None  signal=0 %  packet-loss=100 %  rtt-min=null ms    rtt-med=null ms    rtt-max=null ms   rtt-dev=null ms"
    return 1

}

while true; do

    check_connectivity
    sleep 60  # Intervalo entre os testes
done
