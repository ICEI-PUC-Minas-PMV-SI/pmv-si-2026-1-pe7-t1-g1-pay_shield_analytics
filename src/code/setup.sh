#!/bin/bash

# Define a raiz do projeto (duas pastas acima do src/code/)
cd "$(dirname "$0")/../.."
PROJECT_ROOT=$(pwd)

echo "Verificando se o pacote python3.12-venv está instalado (obrigatório em algumas distribuições Linux)..."
if command -v apt >/dev/null 2>&1 && ! dpkg -l | grep python3.12-venv >/dev/null 2>&1; then
    echo "⚠️  AVISO: Faltam dependências essenciais de sistema para o Python."
    echo "Por favor, execute este comando no terminal para instalar (será pedida sua senha de admin):"
    echo "sudo apt install python3.12-venv"
    echo "Após concluir a instalação, rode este script novamente!"
    exit 1
fi

echo "Criando ambiente virtual (.venv) na raiz do projeto ($PROJECT_ROOT)..."
python3 -m venv .venv

echo "Ativando ambiente virtual..."
source .venv/bin/activate

echo "Atualizando o pip..."
pip install --upgrade pip

if [ -f "src/code/requirements.txt" ]; then
    echo "Instalando dependências do src/code/requirements.txt..."
    pip install -r src/code/requirements.txt
elif [ -f "requirements.txt" ]; then
    echo "Instalando dependências do requirements.txt (raiz)..."
    pip install -r requirements.txt
else
    echo "Aviso: Nenhuma lista de dependências encontrada."
fi

echo ""
echo "===================================================================="
echo "Ambiente configurado com sucesso!"
echo "Entrando automaticamente no ambiente virtual..."
echo "Para sair do ambiente depois de usar, basta digitar: exit"
echo "===================================================================="

# Entra em um novo terminal já com o .venv ativado automaticamente
bash --init-file <(echo "if [ -f ~/.bashrc ]; then source ~/.bashrc; fi; source .venv/bin/activate")
