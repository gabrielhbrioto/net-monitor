import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from InquirerPy import inquirer
import shutil
import re
import os

# Cria um diretório raiz para armazenar os gráficos
base_dir = "Graficos"

# Estrutura de diretórios
folders = ["Histogramas", "Graficos_de_Dispersao", "Graficos_de_Variacao_no_Tempo", "Boxplot", "Correlacao_Signal_RTT", "Media_RTT_por_Hora"]

# Inicializa o DataFrame vazio
df = pd.DataFrame()  

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
    df = pd.DataFrame() # Inicializa como um DataFrame vazio

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
        r"^(?P<timestamp>\S+ \S+) - network=(?P<network>\S+|None)\s+"
        r"signal=(?P<signal>\d+) %\s+"
        r"packet-loss=(?P<packet_loss>\d+) %\s+"
        r"rtt-min=(?P<rtt_min>[\d\.]+|null) ms\s+"
        r"rtt-med=(?P<rtt_med>[\d\.]+|null) ms\s+"
        r"rtt-max=(?P<rtt_max>[\d\.]+|null) ms\s+"
        r"rtt-dev=(?P<rtt_dev>[\d\.]+|null) ms$"
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

def boxplot_graph(action):
    """Gera um boxplot comparativo das métricas de RTT.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """

    global df

    # Cria um gráfico de boxplot comparativo
    plt.figure(figsize=(10, 6))
    plt.boxplot([df[column] for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']], 
                vert=True, patch_artist=True, labels=['RTT Min', 'RTT Med', 'RTT Max', 'RTT Dev'])

    # Configurando títulos e rótulos
    plt.title('Boxplot Comparativo de RTT', fontsize=16)
    plt.ylabel('Valores', fontsize=14)
    plt.xlabel('Métricas', fontsize=14)
    plt.grid(True)

    # verifica se deve salvar ou exibir o gráfico
    if action == "save":
        plt.savefig(f'{base_dir}/Boxplot/rtt_boxplot.png')
        plt.close()
    else:
        plt.show()

def histogram_graph(action):
    """Gera histogramas para cada métrica de RTT, sinal e perda de pacotes.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """
    
    global df

    # Cria histogramas para cada métrica
    for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev', 'signal', 'packet_loss']:
        plt.figure(figsize=(12, 6))
        plt.hist(df[column], bins=10, color='blue', alpha=0.7, edgecolor='black')

        # Configurando títulos e rótulos
        plt.title(f'Distribuição do {labels[column]}', fontsize=16)
        plt.xlabel(labels[column], fontsize=14)
        plt.ylabel('Frequência', fontsize=14)

        # Verifica se deve salvar ou exibir o gráfico
        if action == "save":
            plt.savefig(f'{base_dir}/Histogramas/{column}_histogram.png')
            plt.close()
        else:
            plt.show()

def time_series_graph(action):
    """Gera um gráfico de variação no tempo para cada métrica de RTT, sinal e perda de pacotes.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """

    global df

    # Cria gráficos de variação no tempo para cada métrica
    for column in ['signal', 'rtt_min', 'rtt_max', 'rtt_med', 'rtt_dev', 'packet_loss']:

        plt.figure(figsize=(12, 6))
        plt.plot(df["timestamp"], df[column])
        plt.title(f'Gráfico de variação no tempo do {labels[column]}')
        plt.xlabel("Tempo")
        plt.ylabel(labels[column])

        # Rotaciona os rótulos do eixo X para melhor leitura
        plt.xticks(rotation=45)

        # Verifica se deve salvar ou exibir o gráfico
        if action == "save":
            plt.savefig(f'{base_dir}/Graficos_de_Variacao_no_Tempo/{column}_time_series.png')
            plt.close()
        else:
            plt.show()

def dispertion_graph(action):
    """Gerar gráficos de dispersão para cada métrica de RTT, sinal e perda de pacotes.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """

    # Cria gráficos de dispersão para cada métrica
    for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev', 'signal', 'packet_loss']:
        # Plotando o gráfico de dispersão
        plt.figure(figsize=(12, 6))

        plt.scatter(df['timestamp'], df[column], label=column, color='blue', alpha=0.7)

        # Configurando título e rótulos
        plt.title(f'Gráficod e dispersão do {labels[column]}', fontsize=16)
        plt.xlabel('Timestamp', fontsize=14)
        plt.ylabel(labels[column], fontsize=14)

        # Rotacionando os rótulos do eixo X para melhor leitura
        plt.xticks(rotation=45)

        # Adicionando legenda
        plt.legend(fontsize=12)

        # Exibindo o gráfico
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        # Verifica se deve salvar ou exibir o gráfico
        if action == "save":
            plt.savefig(f'{base_dir}/Graficos_de_Dispersao/{column}_dispertion.png')
            plt.close()
        else:
            plt.show()

def stats():
    """Exibe estatísticas descritivas do data frame.
    """

    print("Caracterização do data frame:")
    print(df.describe())

def export_graphs():
    """Exporta os gráficos gerados para um arquivo ZIP.
    """

    # Cria os diretórios
    for folder in folders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    
    # Gerar os gráficos
    time_series_graph("save")
    histogram_graph("save")
    boxplot_graph("save")
    dispertion_graph("save")
    corr_rtt_signal("save")
    rtt_per_hour("save")

    # Cria um arquivo ZIP contendo todos os gráficos
    zip_filename = "Graficos.zip"
    shutil.make_archive("Graficos", "zip", base_dir)

    # Remover a pasta "Graficos" após criar o ZIP
    shutil.rmtree("Graficos")

    # Exibir mensagem de sucesso
    print(f"Todos os gráficos foram salvos e compactados no arquivo \"{zip_filename}\".")

def corr_rtt_signal(action):
    """Gera gráficos de dispersão e calcula a correlação entre Signal e cada métrica de RTT.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """

    global df

    # Gráfico de dispersão entre Signal e cada métrica de RTT
    for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']:
        plt.figure(figsize=(8, 6))
        plt.scatter(df["signal"], df[column], alpha=0.7, edgecolor="k")
        plt.title(f"Relação entre Signal (%) e {labels[column]}", fontsize=16)
        plt.xlabel("Signal (%)", fontsize=12)
        plt.ylabel(f"{labels[column]}", fontsize=12)
        plt.grid(True)

        # Verifica se deve salvar ou exibir o gráfico
        if action == "save":
            plt.savefig(f'{base_dir}/Correlacao_Signal_RTT/Correlacao_Signal_{column}.png')
            plt.close()
        else:
            plt.show()

    if action == "show":

        # Coeficiente de correlação entre Signal e cada métrica de RTT
        correlation_results = {}
        for column in ['rtt_min', 'rtt_med', 'rtt_max', 'rtt_dev']:
            correlation = df["signal"].corr(df[column])  # Correlação de Pearson
            correlation_results[column] = correlation

        # Exibir resultados de correlação
        print("Coeficientes de Correlação entre Signal e Métricas de RTT:")
        for column, corr in correlation_results.items():
            corr_type = ""
            corr_strengh = ""

            corr_type = "positiva" if corr > 0 else "negativa"

            # Classifica a força da correlação
            if abs(corr) >= 0.7:
                corr_strengh = "muito forte"
            elif abs(corr) >= 0.5:
                corr_strengh = "moderada"
            elif abs(corr) >= 0.3:
                corr_strengh = "fraca"
            else:
                corr_strengh = "muito fraca"

            print(f"Signal vs {labels[column]}: {corr:.4f} (correlação {corr_type} {corr_strengh})")

def rtt_per_hour(action):
    """Gera um gráfico de linha da média de RTT por hora do dia.

    Args:
        action (string): Indica se o gráfico deve ser exibido ou salvo. ("show" ou "save")
    """

    global df

    # Extrair a hora do dia
    df["hour"] = df["timestamp"].dt.hour

    # Agrupar por hora e calcular a média de RTT
    hourly_rtt = df.groupby("hour")["rtt_med"].mean()

    if action == "show":
        print("Média de RTT por Hora do Dia:")
        print(hourly_rtt) 

    # Plotar o gráfico de latência média por hora
    plt.figure(figsize=(10, 6))
    hourly_rtt.plot(kind="line", marker="o", title="Média de RTT por Hora do Dia")
    plt.xlabel("Hora do Dia")
    plt.ylabel("Média de RTT (ms)")
    plt.grid(True)

    # Verifica se deve salvar ou exibir o gráfico  
    if action == "save":
        plt.savefig(f'{base_dir}/Media_RTT_por_Hora/Media_RTT_por_Hora.png')
        plt.close()
    else:
        plt.show()

def generate_graphs():
    """Exibe um menu para o usuário escolher o tipo de gráfico a ser gerado.
    """

    global df
    global labels

    while True:
        options = ["Gráficos de variação no tempo", "Histogramas", "Boxplot", "Gráficos de dispersão", "Sair"]
        choice = inquirer.select(
            message="Escolha uma opção:",
            choices=options,
        ).execute()

        if choice == "Gráficos de variação no tempo":

            time_series_graph("show")

        elif choice == "Histogramas":

            histogram_graph("show")

        elif choice == "Boxplot":

            boxplot_graph("show")
        
        elif choice == "Gráficos de dispersão":

            dispertion_graph("show")

        elif choice == "Sair":
            print("Retornando ao menu principal...")
            break
        
def menu():
    """Exibe um menu principal para o usuário escolher as opções disponíveis.
    """

    global df
    options = ["Extrair dados do log", "Exibir dados", "Gerar gráficos", "Correlação entre RTT e Sinal", "RTT por hora do dia", "Estatísticas", "Exportar dados para CSV", "Exportar gráficos", "Sair"]
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

    elif choice == "Gerar gráficos":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            generate_graphs()

    elif choice == "Estatísticas":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            stats()

    elif choice == "Correlação entre RTT e Sinal":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            corr_rtt_signal("show")

    elif choice == "RTT por hora do dia":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            rtt_per_hour("show")

    elif choice == "Exportar dados para CSV":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            export_to_csv()

    elif choice == "Exportar gráficos":
        if df.empty:
            print("Nenhum dado disponível. Extraia os dados primeiro.")
        else:
            export_graphs()

    elif choice == "Sair":
        print("Saindo do programa...")
        os._exit(0)

while True:
    menu()
