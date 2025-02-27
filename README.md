# 📡 Net Monitor - Monitoramento de Rede

Net Monitor é uma ferramenta para monitoramento da conectividade da rede Wi-Fi, registrando perdas de pacotes, tempo de resposta (RTT) e intensidade do sinal. Além disso, fornece análises detalhadas sobre a estabilidade da rede ao longo do tempo, permitindo analisar os dados para detectar padrões de instabilidade, correlacionar RTT com sinal e identificar periódos críticos na qualidade da conexão.

![Net Monitor Logo](assets/netmon_logo.png)

## ⚡ Recursos

- 📡 **Monitoramento contínuo da conexão Wi-Fi**: Mede qualidade da conexão em intervalos regulares.
- 📊 **Análise estatística**: Visualiza dados coletados para avaliar a estabilidade da rede.
- 🔍 **Correlação entre sinal e latência**: Gera gráficos e calcula correlação entre intensidade do sinal e RTT.
- 📈 **Identificação de horários críticos**: Detecta momentos de maior instabilidade.
- ⏳ **Tempo médio de recuperação**: Mede quanto tempo a rede leva para se estabilizar após uma falha.
- 📄 **Exportação dos dados**: Possibilidade de exportar os dados extraídos dos logs em um arquivo CSV para realização de mais análises.


## 📥 Instalação

### 🔧 Pré-requisitos

- Linux (testado em Ubuntu/Debian)
- Python 3.10+
- `pip` atualizado
- Systemd para gerenciamento do serviço

### 📌 Passo a passo

1️⃣ Clone o repositório:
```sh
 git clone https://github.com/seu-usuario/netmon.git
 cd netmon
```

2️⃣ Execute a instalação:
```sh
 sudo make install
```

Isso instalará os scripts, criará os diretórios necessários e configurará o serviço Systemd.

## 🚀 Uso

Após a instalação, o NetMon pode ser utilizado com os seguintes comandos:

### 🔄 Gerenciamento do Serviço

| Comando                 | Descrição |
|-------------------------|-------------|
| `netmon activate`       | Ativa o monitoramento da rede |
| `netmon deactivate`     | Desativa o monitoramento |
| `netmon status`         | Verifica se o serviço está ativo |
| `netmon analyze`        | Inicia o modo de análise dos logs |
| `netmon config`         | Permite configurar os parâmetros como intervalo e alvos |
| `netmon set-interface <iface>` | Define manualmente a interface Wi-Fi |

Exemplo:
```sh
netmon set-interface wlan0
```

### 📊 Análise dos Dados

---

Ao executar `netmon analyze`, um menu interativo será exibido para selecionar diferentes tipos de análise.

O script analyzer.py permite realizar diversas análises baseadas nos dados extraídos do log gerado pelo netmon. Ele processa informações como RTT, sinal da rede Wi-Fi e perda de pacotes, fornecendo insights detalhados sobre a qualidade da conexão.

📌 **A análise pode ser feita considerando todos os dados ou separando-os por redes. O usuário também pode especificar um intervalo de tempo na extração dos dados do log para conduzir a análise.**

1️⃣ Correlação entre RTT e Sinal

🔍 Descrição: Gera gráficos de dispersão e calcula a correlação entre o sinal da rede Wi-Fi (%) e os valores de RTT (rtt_min, rtt_med, rtt_max e rtt_dev).
📈 Objetivo: Determinar se há uma relação entre a intensidade do sinal e a latência da conexão.
💲 Saída:

- Gráfico de dispersão para cada métrica de RTT

- Coeficiente de correlação de Pearson

- Classificação da correlação: muito fraca, fraca, moderada ou forte

2️⃣ RTT por Hora do Dia

⏳ Descrição: Analisa a variação do tempo de resposta (rtt_med) ao longo do dia.
📈 Objetivo: Identificar horários em que a rede apresenta maior ou menor latência.
💲 Saída:

- Gráfico de linha exibindo a média do RTT por hora do dia

3️⃣ Classificação da Qualidade da Conexão

✅ Descrição: Avalia a qualidade da conexão com base nos valores médios de RTT, sinal e perda de pacotes.
📈 Objetivo: Fornecer um diagnóstico simples sobre a estabilidade e desempenho da rede.
💲 Saída:

- Valores médios de RTT, sinal e perda de pacotes

- Classificação qualitativa da conexão

4️⃣ Horários Críticos da Conexão

🚨 Descrição: Identifica os períodos do dia com maior instabilidade, baseando-se nos valores mais altos de rtt_med e packet_loss.
📈 Objetivo: Descobrir horários em que a rede apresenta mais problemas.
💲 Saída:

- Horário do dia com maior RTT médio

- Horário do dia com maior perda de pacotes

- Indicação de períodos críticos de instabilidade

5️⃣ Tempo Médio de Recuperação da Rede

🔄 Descrição: Mede quanto tempo a rede leva para se recuperar após um evento de alta perda de pacotes (>20%).
📈 Objetivo: Identificar a eficiência da recuperação da rede após problemas de conectividade.
💲 Saída:

- Tempo médio para recuperação após falha

6️⃣ Exportação de Dados para CSV

📂 Descrição: Permite exportar os dados extraídos para um arquivo CSV, facilitando a análise externa.
📈 Objetivo: Armazenar ou processar os dados fora do script analyzer.py.
💲 Saída:

- Arquivo .csv contendo os dados extraídos do log

## ⚙️ Configuração

O NetMon armazena sua configuração no arquivo `/etc/netmon.conf`. Você pode editá-lo manualmente ou usar o comando `netmon config` para alterar os seguintes parâmetros:

| Parâmetro   | Descrição |
|-------------|-------------|
| `MAX_LOSS`  | Percentual máximo de perda de pacotes permitido |
| `TARGETS`   | Endereços IP utilizados para teste de conectividade |
| `INTERVAL`  | Intervalo entre as medições (segundos) |
| `PING_COUNT`| Número de pacotes enviados por teste |

Caso o serviço não detecte automaticamente a interface de conexão sem fio, ela pode ser configurada por meio do comando:

  ```sh
  netmon set-interface <nome-interface>
  ```

O qual altera o valor do parâmetro `IFACE` no arquivo de configurações. Em seguida basta reiniciar o serviço executando os comandos:

  ```sh
  netmon deactivate
  netmon activate
  ```

Dessa forma as novas configurações serão aplicadas ao serviço e isso vale tanto para o comando `config` quanto para o comando `set-interface`.

## 📤 Desinstalação

Se desejar remover o NetMon do seu sistema, basta rodar:
```sh
 sudo make uninstall
```
Isso removerá todos os arquivos, logs e configurações.

---

## 📂 Estrutura do Projeto
```
/netmon
├── Makefile            # Script de instalação e remoção
├── netmon              # Script de controle (CLI)
├── netmon.sh           # Script principal do monitor
├── analyzer.py         # Script de análise de dados
├── netmon.service      # Configuração do systemd
├── README.md           # Documentação
└── /assets
    └── netmon_logo.png # Logo do Net Monitor
```

---

💡 **Dica:** Para visualizar os logs gerados pelo NetMon, utilize:
```sh
cat /var/log/netmon/netmon.log
```

