#!/bin/bash

CONFIG_FILE="/etc/netmon.conf"

# Definir valores padrão caso o arquivo não exista
MAX_LOSS=40
TARGETS=("8.8.8.8" "8.8.4.4" "1.1.1.1" "1.0.0.1" "208.67.222.222" "208.67.220.220")
INTERVAL=60
PING_COUNT=5
IFACE=""

# Carregar configurações do arquivo, se ele existir
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
fi

# Detectando automaticamente a interface Wi-Fi, a menos que já tenha sido configurada manualmente
detect_wifi_interface() {
    if [[ -n "$IFACE" ]]; then
        echo "Usando interface Wi-Fi configurada manualmente: $IFACE"
        return
    fi

    IFACE=$(iw dev | awk '$1=="Interface"{print $2}')
    if [[ -z "$IFACE" ]]; then
        IFACE=$(nmcli device status | awk '$2=="wifi" {print $1}')
    fi
    if [[ -z "$IFACE" ]]; then
        echo "Erro: Nenhuma interface Wi-Fi detectada! Configure manualmente com 'netmon set-interface <interface>'." >&2
        exit 1
    fi
    echo "Interface Wi-Fi detectada: $IFACE"
}

detect_wifi_interface

# Função para logar mensagens
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" 
}

# Função para testar conectividade
check_connectivity() {
    for TARGET in "${TARGETS[@]}"; do
        PING_OUTPUT=$(ping -c $PING_COUNT -W $PING_COUNT "$TARGET" 2>&1)
        LOSS=$(echo "$PING_OUTPUT" | grep -oP '\d+(?=% perda de pacote)|A rede está fora de alcance')

        if [[ $LOSS == "A rede está fora de alcance" ]]; then
            log_message "network=None signal=0% packet-loss=100% rtt-min=null ms rtt-med=null ms rtt-max=null ms rtt-dev=null ms"
            return 1
        fi

        RTT=$(echo "$PING_OUTPUT" | grep -oP 'rtt mín/méd/máx/mdev = [\d\.]+/[\d\.]+/[\d\.]+/[\d\.]+ ms')

        if [[ -n "$RTT" ]]; then
            RTT_VALUES=$(echo "$RTT" | awk -F' = ' '{print $2}')
            MIN=$(echo "$RTT_VALUES" | awk -F'/' '{print $1}')
            MED=$(echo "$RTT_VALUES" | awk -F'/' '{print $2}')
            MAX=$(echo "$RTT_VALUES" | awk -F'/' '{print $3}')
            MDEV=$(echo "$RTT_VALUES" | awk -F'/' '{print $4}')
        fi

        if [ "$LOSS" -lt "$MAX_LOSS" ]; then
            INFO=$(nmcli -t -f active,ssid,signal dev wifi | grep '^sim')
            SSID=$(echo "$INFO" | awk -F':' '{print $2}')
            SIGNAL=$(echo "$INFO" | awk -F':' '{print $3}')
            log_message "network=$SSID signal=$SIGNAL% packet-loss=$LOSS% rtt-min=$MIN ms rtt-med=$MED ms rtt-max=$MAX ms rtt-dev=$MDEV ms"
            return 0
        fi
    done

    log_message "network=None signal=0% packet-loss=100% rtt-min=null ms rtt-med=null ms rtt-max=null ms rtt-dev=null ms"
    return 1
}

while true; do
    check_connectivity
    sleep $INTERVAL  # Intervalo entre os testes
done