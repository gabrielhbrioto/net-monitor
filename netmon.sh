#!/bin/bash

CONFIG_FILE="/etc/netmon.conf"

# Definir valores padrão caso o arquivo não exista
MAX_LOSS=60
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
