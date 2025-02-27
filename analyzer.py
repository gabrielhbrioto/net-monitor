import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # Usa TkAgg como backend
import matplotlib.pyplot as plt

from datetime import datetime
from InquirerPy import inquirer
import shutil
import re
import os

# Inicializa o DataFrame vazio
df = pd.DataFrame()  
analyze_by_network = ""

# Rótulos das colunas
labels = {
    'rtt_min': 'RTT Mínimo (ms)',
    'rtt_med': 'RTT Mediano (ms)',
    'rtt_max': 'RTT Máximo (ms)',
    'rtt_dev': 'Desvio do RTT (ms)',
    'signal': 'Sinal (%)',
    'packet_loss': 'Perda de Pacotes (%)'
}


def export_to_csv():
    """Exporta os dados extraídos do log e tratados para um arquivo CSV.
    """
    global df
    
    try:
        # Solicita o nome do arquivo ao usuário
        output_filename = input("Digite o nome do arquivo CSV (com extensão .csv): ").strip()
        if not output_filename.endswith('.csv'):
            output_filename += '.csv'

        # Obtém o diretório atual do script
        current_directory = os.getcwd()
        output_path = os.path.join(current_directory, output_filename)
        
        # Salva o DataFrame como CSV
        df.to_csv(output_path, index=False)
        print(f"Dados exportados com sucesso para {output_path}")

    except Exception as e:
        print(f"Erro ao exportar os dados: {e}")

def extract_data():
    """Extrai os dados do arquivo de log netmon.log e retorna um DataFrame com os dados extraídos.

    Returns:
        DataFrame: Dataframe com os dados extraídos do arquivo de log.
    """

    global df

    # Caminho do arquivo de log
    log_file_path = "/var/log/netmon/netmon.log"

    # Solicitar ao usuário o intervalo de tempo
    start_time = input("Digite o horário de início (YYYY-MM-DD HH:MM:SS) ou deixe em branco para o mais antigo: ").strip()
    if start_time == "":
        # Define uma data mínima segura como padrão (1970-01-01 00:00:00)
        start_time = "1970-01-01 00:00:00"

    end_time = input("Digite o horário de término (YYYY-MM-DD HH:MM:SS) ou deixe em branco para o horário atual: ").strip()
    if end_time == "":
        # Define o horário atual como padrão
        end_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Extraindo dados do arquivo de log entre {start_time} e {end_time}...")

    try:
        # Convertendo as entradas para datetime
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)

    except Exception as e:

        print(f"Erro ao interpretar as datas: {e}")

        # Retorna um DataFrame vazio em caso de erro
        return pd.DataFrame()


    # Lista para armazenar os dados extraídos
    data = []

    log_pattern = re.compile(
        r"^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - network=(?P<network>[^\s]+|None)\s+"
        r"signal=(?P<signal>\d+)%\s+"
        r"packet-loss=(?P<packet_loss>\d+)%\s+"
        r"rtt-min=(?P<rtt_min>[\d\.]+|null)\s+ms\s+"
        r"rtt-med=(?P<rtt_med>[\d\.]+|null)\s+ms\s+"
        r"rtt-max=(?P<rtt_max>[\d\.]+|null)\s+ms\s+"
        r"rtt-dev=(?P<rtt_dev>[\d\.]+|null)\s+ms"
    )

    
    # Lendo o arquivo de log e extraindo os dados dentro do intervalo
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = log_pattern.match(line)
            if match:
                log_entry = match.groupdict()
    
                # Converter o timestamp do log para um objeto datetime
                log_timestamp = datetime.strptime(log_entry['timestamp'], "%Y-%m-%d %H:%M:%S")
    
                # Verificar se está dentro do intervalo
                if start_time <= log_timestamp <= end_time:
                    data.append(log_entry)

    # Criando o DataFrame
    if data:
        extracted_df = pd.DataFrame(data)

        # Convertendo os tipos das colunas
        extracted_df['timestamp'] = pd.to_datetime(extracted_df['timestamp'])
        extracted_df['signal'] = extracted_df['signal'].astype(int)
        extracted_df['packet_loss'] = extracted_df['packet_loss'].astype(int)

        # Substituir valores 'null' por NaN antes de converter para float
        for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']:
            extracted_df[column] = pd.to_numeric(extracted_df[column].replace('null', None), errors='coerce')

        extracted_df.dropna(inplace=True)
        return extracted_df
    else:
        print("Nenhum dado foi encontrado no arquivo de log.")
        return pd.DataFrame()

def stats():
    """Exibe estatísticas descritivas do DataFrame."""

    global df
    global analyze_by_network  # Assegurar acesso à variável global

    if analyze_by_network == "Análise geral (todas as redes)":
        print("Caracterização geral dos dados:")
        print(df.describe())
    else:
        for ssid, group in df.groupby("network"):
            if group.empty:
                print(f"Sem dados disponíveis para a rede: {ssid}")
                continue
            print(f"Estatísticas da rede: {ssid}")
            print(group.describe())

def corr_rtt_signal():
    """Gera gráficos de dispersão e calcula a correlação entre Signal e cada métrica de RTT."""

    global df
    global analyze_by_network

    # Escolher se a análise será geral ou separada por rede
    if analyze_by_network == "Análise geral (todas as redes)":
        dataset = {"Geral": df}  # Criamos um dicionário para facilitar a iteração
    else:
        dataset = {ssid: group for ssid, group in df.groupby("network")}

    # Itera sobre os conjuntos de dados (geral ou por rede)
    for name, group in dataset.items():
        print(f"Rede: {name}")

        # Gráfico de dispersão entre Signal e cada métrica de RTT
        for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']:
            plt.figure(figsize=(8, 6))
            plt.scatter(group["signal"], group[column], alpha=0.7, edgecolor="k")
            plt.title(f"{name} - Relação entre Signal (%) e {labels[column]}", fontsize=16)
            plt.xlabel("Signal (%)", fontsize=12)
            plt.ylabel(f"{labels[column]}", fontsize=12)
            plt.grid(True)
            plt.show()

        # Coeficiente de correlação entre Signal e cada métrica de RTT
        correlation_results = {}
        for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']:
            correlation = group["signal"].corr(group[column])  # Correlação de Pearson
            correlation_results[column] = correlation

        # Exibir resultados de correlação
        print("Coeficientes de Correlação entre Signal e Métricas de RTT:")
        for column, corr in correlation_results.items():
            corr_type = "positiva" if corr > 0 else "negativa"

            # Classifica a força da correlação
            if abs(corr) >= 0.7:
                corr_strength = "muito forte"
            elif abs(corr) >= 0.5:
                corr_strength = "moderada"
            elif abs(corr) >= 0.3:
                corr_strength = "fraca"
            else:
                corr_strength = "muito fraca"

            print(f"Signal vs {labels[column]}: {corr:.4f} (correlação {corr_type} {corr_strength})")

def rtt_per_hour():
    """Gera um gráfico de linha da média de RTT por hora do dia."""

    global df
    global analyze_by_network

    df["hour"] = df["timestamp"].dt.hour

    if analyze_by_network == "Análise geral (todas as redes)":
        dataset = {"Geral": df}
    else:
        dataset = {ssid: group for ssid, group in df.groupby("network")}

    for name, group in dataset.items():
        print(f"Rede: {name}")

        hourly_rtt = group.groupby("hour")["rtt_med"].mean()
        print(hourly_rtt)

        plt.figure(figsize=(10, 6))
        hourly_rtt.plot(kind="line", marker="o", title=f"{name} - Média de RTT por Hora do Dia")
        plt.xlabel("Hora do Dia")
        plt.ylabel("Média de RTT (ms)")
        plt.grid(True)
        plt.show()

def connection_quality():
    """Classifica a qualidade da conexão baseado nos valores médios de RTT, sinal e perda de pacotes."""
    global df
    global analyze_by_network

    if analyze_by_network == "Análise geral (todas as redes)":
        dataset = {"Geral": df}
    else:
        dataset = {ssid: group for ssid, group in df.groupby("network")}

    for name, group in dataset.items():
        print(f"Rede: {name}")

        avg_rtt = group["rtt_med"].mean()
        avg_signal = group["signal"].mean()
        avg_loss = group["packet_loss"].mean()

        print(f"RTT Médio: {avg_rtt:.2f} ms")
        print(f"Sinal Médio: {avg_signal:.2f}%")
        print(f"Perda de Pacotes Média: {avg_loss:.2f}%")

def peak_instability_periods():
    """Identifica os horários do dia onde ocorrem os maiores RTTs médios e maior perda de pacotes."""

    global df
    global analyze_by_network

    df["hour"] = df["timestamp"].dt.hour  # Extrai a hora do timestamp

    if analyze_by_network == "Análise geral (todas as redes)":
        dataset = {"Geral": df}
    else:
        dataset = {ssid: group for ssid, group in df.groupby("network")}

    for name, group in dataset.items():
        high_rtt_hour = group.groupby("hour")["rtt_med"].mean().idxmax()
        high_loss_hour = group.groupby("hour")["packet_loss"].mean().idxmax()

        print(f"Rede: {name}")
        print(f"Maior RTT médio ocorre por volta das {high_rtt_hour}:00")
        print(f"Maior perda de pacotes ocorre por volta das {high_loss_hour}:00")

        if high_rtt_hour == high_loss_hour:
            print(f"A maior instabilidade ocorre no horário das {high_rtt_hour}:00.")
        else:
            print("A instabilidade pode variar ao longo do dia.")

def recovery_time():
    """Analisa o tempo médio necessário para a rede se recuperar após uma falha (alta perda de pacotes)."""
    
    global df
    global analyze_by_network

    threshold = 20  # Limite de perda de pacotes considerada alta

    if analyze_by_network == "Análise geral (todas as redes)":
        dataset = {"Geral": df}
    else:
        dataset = {ssid: group for ssid, group in df.groupby("network")}

    for name, group in dataset.items():
        group["prev_loss"] = group["packet_loss"].shift(1)  # Adiciona uma coluna para comparar com a anterior
        recovery_times = []

        for i in range(1, len(group)):
            if group.iloc[i - 1]["prev_loss"] >= threshold and group.iloc[i]["packet_loss"] < threshold:
                recovery_time = (group.iloc[i]["timestamp"] - group.iloc[i - 1]["timestamp"]).total_seconds()
                recovery_times.append(recovery_time)

        if recovery_times:
            avg_recovery_time = sum(recovery_times) / len(recovery_times)
            print(f"Rede: {name}")
            print(f"Tempo médio para recuperação após falha: {avg_recovery_time:.2f} segundos.")
        else:
            print(f"Rede: {name} | Nenhuma falha detectada no intervalo analisado.")

def menu():
    """Exibe um menu principal para o usuário escolher as opções disponíveis."""

    global df
    global analyze_by_network

    options = ["Extrair dados do log", "Exibir dados", "Correlação entre RTT e Sinal", "RTT por hora do dia", 
               "Estatísticas", "Classificação da Qualidade da Conexão", "Horários Críticos da Conexão", 
               "Tempo Médio de Recuperação da Rede", "Exportar dados para CSV", "Sair"]

    choice = inquirer.select(
        message="Escolha uma opção:",
        choices=options,
    ).execute()

    if choice == "Extrair dados do log":
        df = extract_data()

    elif choice == "Exibir dados":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            print(df)

    elif choice == "Estatísticas":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            stats()

    elif choice == "Correlação entre RTT e Sinal":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            corr_rtt_signal()

    elif choice == "RTT por hora do dia":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            rtt_per_hour()
            
    elif choice == "Classificação da Qualidade da Conexão":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            connection_quality()

    elif choice == "Horários Críticos da Conexão":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            peak_instability_periods()

    elif choice == "Tempo Médio de Recuperação da Rede":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            recovery_time()
    
    elif choice == "Exportar dados para CSV":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            export_to_csv()

    elif choice == "Sair":
        print("Saindo do programa...")
        os._exit(0)




def main():
    
    global analyze_by_network

    # Pergunta ao usuário se deseja analisar todas as redes juntas ou separadamente
    analyze_by_network = inquirer.select(
        message="Como deseja realizar a análise?",
        choices=["Análise geral (todas as redes)", "Análise separada por rede"],
    ).execute()

    while True:
        menu()

if __name__ == "__main__":
    main()
