# 🛡️ Digital Payment Fraud Detection

Este repositório contém o código para análise e detecção de fraude em transações digitais, migrado do Google Colab para execução local. O projeto utiliza um dataset com 129.667 transações e 29 atributos para identificar padrões de comportamento fraudulento.

## 📋 Pré-requisitos

Antes de começar, certifique-se de que possui instalado:

- **Python 3.9+**
- **Visual Studio Code (VS Code)**
- **Git**

---

## 🚀 Configuração do Ambiente

Siga os passos abaixo para configurar a máquina e executar o Jupyter Notebook:

### 1. Clonar o Repositório

```bash
git clone https://github.com/ICEI-PUC-Minas-PMV-SI/pmv-si-2026-1-pe7-t1-g1-pay_shield_analytics.git
cd pmv-si-2026-1-pe7-t1-g1-pay_shield_analytics
```

### 2. Configurar o Ambiente Virtual e Dependências

**⚠️ Atenção (Usuários Linux/Ubuntu):** Antes de prosseguir, é necessário ter o módulo de ambientes virtuais instalado. No seu terminal, execute:
```bash
sudo apt install python3.12-venv
```

Para facilitar a configuração do projeto, disponibilizamos um script de automação (`setup.sh`) na pasta `src/code/`. Ele cria automaticamente um ambiente virtual (`.venv`) na raiz do projeto, ativa o ambiente e instala todas as bibliotecas necessárias.

1. Abra o terminal.
2. Navegue até a pasta do código:
   ```bash
   cd src/code
   ```
3. Execute o script de configuração:
   ```bash
   ./setup.sh
   ```

*(Para execução no Windows, recomenda-se usar o Git Bash para rodar `bash setup.sh`, ou criar e ativar o `.venv` manualmente executando os comandos do script de dentro das pastas no PowerShell).*

---

## 🛠️ Como Executar no VS Code

1. Abra a pasta raiz do projeto (`pmv-si-2026-1-pe7-t1-g1-pay_shield_analytics`) no VS Code.
2. Navegue até o arquivo `src/code/paymment_fraud_notebook.ipynb` e abra-o.
3. Instale as extensões recomendadas (**Python** e **Jupyter**) caso o VS Code solicite.
4. No canto superior direito, clique em **Select Kernel**.
5. Selecione **Python Environments** e procure pelo ambiente `.venv` criado dentro da pasta `src/code/`.
6. Após selecionar o ambiente, execute as células de código clicando no botão ▶️ (Run All ou cell-by-cell).

---

Projeto focado em análise exploratória e identificação de outliers em pagamentos digitais.
