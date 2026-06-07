import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Configuração visual do Streamlit
st.set_page_config(page_title="Detector de Fraudes", layout="wide")

st.title("🛡️ Simulador de Risco de Fraude")
st.write("Insira os dados operacionais, cadastrais e de comportamento para avaliar o risco da transação.")

# Carrega o modelo do Colab (_rf_search)
@st.cache_resource
def carregar_modelo():
    return joblib.load('modelo_fraude.pkl')

modelo = carregar_modelo()

st.subheader("📋 Dados da Transação, Cliente e Login")

# Divisão da tela em 3 colunas para distribuir as entradas do usuário
col1, col2, col3 = st.columns(3)

with col1:
    transaction_amount = st.number_input("Valor da Transação ($)", min_value=0.0, value=150.0)
    avg_transaction_amount = st.number_input("Média Histórica ($)", min_value=0.0, value=120.0)
    account_age_days = st.number_input("Idade da Conta (dias)", min_value=0, value=365)

    device_type = st.selectbox("Tipo de Dispositivo", ["Android", "iOS", "Web"])

with col2:
    transaction_hour = st.slider("Hora da Transação (0-23h)", 0, 23, 14)

    login_attempts_last_24h = st.number_input("Tentativas de Login (Últimas 24h)", min_value=0, value=1)
    previous_failed_attempts = st.number_input("Tentativas de Login Falhas Anteriores", min_value=0, value=0)
    login_failure_rate = st.slider("Taxa de Falha de Login (0.0 a 1.0)", min_value=0.0, max_value=1.0, value=0.0, step=0.05)

with col3:
    device_location = st.selectbox(
        "Localização do Dispositivo",
        ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Mumbai"]
    )
    is_international = st.selectbox("Transação Internacional?", ["Não", "Sim"])
    is_international_int = 1 if is_international == "Sim" else 0

    payment_mode = st.selectbox("Forma de Pagamento", ["Card", "NetBanking", "UPI", "Wallet"])
    transaction_type = st.selectbox("Tipo de Transação", ["Payment", "Transfer", "Withdrawal"])

st.markdown("---")
st.subheader("🌐 Configurações de Rede/Segurança")
col_net1, col_net2 = st.columns(2)

with col_net1:
    ip_risk = st.selectbox("Nível de Risco do IP", ["Baixo", "Médio/Alto"])
    high_ip_risk = 1 if ip_risk == "Médio/Alto" else 0
with col_net2:
    ip_risk_score = st.slider("Score de Risco do IP (0 a 100)", min_value=0, max_value=100, value=15)

# --- ENGENHARIA DE RECURSOS DERIVADAS (Regras do seu time) ---
amount = transaction_amount
late_night_flag = 1 if (0 <= transaction_hour <= 5) else 0
is_night = 1 if (transaction_hour >= 18 or transaction_hour <= 5) else 0

hour_sin = np.sin(2 * np.pi * transaction_hour / 24)
hour_cos = np.cos(2 * np.pi * transaction_hour / 24)

international_night = 1 if (is_international_int == 1 and transaction_hour <= 5) else 0
night_intl_risk = international_night
international_risk = is_international_int

many_login_attempts = 1 if login_attempts_last_24h > 3 else 0
risk_login = 1 if (login_failure_rate > 0.5 or login_attempts_last_24h > 3) else 0

# Períodos do dia (One-Hot Encoding)
periodos = {f'period_of_day_{p}': 0 for p in ["madrugada", "manha", "tarde", "noite"]}
if 0 <= transaction_hour < 6:
    periodos['period_of_day_madrugada'] = 1
elif 6 <= transaction_hour < 12:
    periodos['period_of_day_manha'] = 1
elif 12 <= transaction_hour < 18:
    periodos['period_of_day_tarde'] = 1
else:
    periodos['period_of_day_noite'] = 1


# Botão para acionar a classificação do modelo
if st.button("Verificar Transação", type="primary"):

    # 1. Mapeamento das Cidades
    cidades = {f'device_location_{c}': 0 for c in ["Bangalore", "Chennai", "Delhi", "Hyderabad", "Mumbai"]}
    if f'device_location_{device_location}' in cidades:
        cidades[f'device_location_{device_location}'] = 1

    # 2. Mapeamento do Tipo de Dispositivo
    dispositivos = {f'device_type_{d}': 0 for d in ["Android", "Web", "iOS"]}
    dispositivos[f'device_type_{device_type}'] = 1

    # 3. Mapeamento das Formas de Pagamento
    pagamentos = {f'payment_mode_{p}': 0 for p in ["Card", "NetBanking", "UPI", "Wallet"]}
    pagamentos[f'payment_mode_{payment_mode}'] = 1

    # 4. Mapeamento dos Tipos de Transação
    tipos_transacao = {f'transaction_type_{t}': 0 for t in ["Payment", "Transfer", "Withdrawal"]}
    tipos_transacao[f'transaction_type_{transaction_type}'] = 1

    # 5. Criar o dicionário completo com todas as variáveis possíveis
    dados_usuario = {
        'account_age_days': account_age_days,
        'amount': amount,
        'avg_transaction_amount': avg_transaction_amount,
        'is_international': is_international_int,
        'late_night_flag': late_night_flag,
        'hour_sin': hour_sin,
        'hour_cos': hour_cos,
        'international_night': international_night,
        'high_ip_risk': high_ip_risk,
        'international_risk': international_risk,
        'ip_risk_score': ip_risk_score,
        'is_night': is_night,
        'login_attempts_last_24h': login_attempts_last_24h,
        'login_failure_rate': login_failure_rate,
        'many_login_attempts': many_login_attempts,
        'night_intl_risk': night_intl_risk,
        'previous_failed_attempts': previous_failed_attempts,
        'risk_login': risk_login,
        'transaction_amount': transaction_amount,
        'transaction_hour': transaction_hour
    }

    # Juntar os dicionários dummies calculados
    dados_usuario.update(cidades)
    dados_usuario.update(dispositivos)
    dados_usuario.update(pagamentos)
    dados_usuario.update(periodos)
    dados_usuario.update(tipos_transacao)

    # Converter para DataFrame do Pandas
    dados_para_prever = pd.DataFrame([dados_usuario])

    # --- 🎯 SEQUÊNCIA EXATA SOLICITADA PELO SEU MODELO NO FIT ---
    colunas_ordem_correta = [
        'transaction_amount', 'account_age_days', 'transaction_hour', 'previous_failed_attempts',
        'avg_transaction_amount', 'is_international', 'ip_risk_score', 'login_attempts_last_24h',
        'late_night_flag', 'hour_sin', 'hour_cos', 'international_night', 'high_ip_risk',
        'many_login_attempts', 'risk_login', 'login_failure_rate', 'is_night', 'international_risk',
        'night_intl_risk', 'transaction_type_Payment', 'transaction_type_Transfer', 'transaction_type_Withdrawal',
        'payment_mode_Card', 'payment_mode_NetBanking', 'payment_mode_UPI', 'payment_mode_Wallet',
        'device_type_Android', 'device_type_Web', 'device_type_iOS', 'device_location_Bangalore',
        'device_location_Chennai', 'device_location_Delhi', 'device_location_Hyderabad', 'device_location_Mumbai',
        'period_of_day_madrugada', 'period_of_day_manha', 'period_of_day_noite', 'period_of_day_tarde'
    ]

    # Forçar o DataFrame a seguir rigorosamente a lista acima
    dados_para_prever = dados_para_prever[colunas_ordem_correta]

    try:
        # Realizar a predição final
        predicao = modelo.predict(dados_para_prever)[0]
        probabilidade = modelo.predict_proba(dados_para_prever)[0][1]

        st.markdown("---")

        if predicao == 1:
            st.error(f"🚨 **Alerta de Fraude!** Transação classificada como de ALTO RISCO. (Probabilidade: {probabilidade:.2%})")
        else:
            st.success(f"✅ **Transação Segura.** Baixo risco detectado. (Probabilidade de fraude: {probabilidade:.2%})")

    except Exception as e:
        st.error(f"Erro ao processar predição: {e}")
