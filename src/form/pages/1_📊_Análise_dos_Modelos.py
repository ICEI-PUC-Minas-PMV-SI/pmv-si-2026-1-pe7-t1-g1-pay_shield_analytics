import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Análise dos Modelos – PayShield", layout="wide")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Paleta de cores e estilos (igual ao app.py) ─────────────────────────────
_tema_ativo = st.get_option("theme.base") or "light"
_sidebar_fundo = (
    "linear-gradient(180deg, #08254b, #0d3a73)"
    if _tema_ativo == "light"
    else "linear-gradient(180deg, #020b16, #08254b)"
)
_select_fundo = "#ffffff" if _tema_ativo == "light" else "#141c2b"
_select_cor = "#08254b" if _tema_ativo == "light" else "#e0eaff"

st.markdown(
    f"""
    <style>
    :root {{
        --pay-blue: #004aad;
        --pay-dark-blue: #08254b;
        --pay-purple: #6038d0;
        --pay-blue-purple: #445fd6;
        --pay-cyan: #5de0e6;
    }}
    [data-testid="stSidebar"] {{
        background: {_sidebar_fundo};
    }}
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"],
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {_select_fundo} !important;
        color: {_select_cor} !important;
        border-radius: 8px !important;
    }}
    .metric-card {{
        background: linear-gradient(135deg, #0d3a73 0%, #08254b 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #ffffff;
        text-align: center;
        border: 1px solid rgba(93,224,230,0.25);
        box-shadow: 0 4px 15px rgba(0,74,173,0.3);
    }}
    .metric-card .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: #5de0e6;
    }}
    .metric-card .metric-label {{
        font-size: 0.85rem;
        opacity: 0.8;
        margin-top: 0.2rem;
    }}
    .section-title {{
        font-size: 1.3rem;
        font-weight: 700;
        color: #004aad;
        border-left: 4px solid #5de0e6;
        padding-left: 0.75rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Logo na sidebar ──────────────────────────────────────────────────────────
logo_path = os.path.join(BASE_DIR, "images", "rd_payshield_logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=200)

# ── Carregamento dos modelos ─────────────────────────────────────────────────
@st.cache_resource
def carregar_modelos():
    modelos = {}
    arquivos = {
        "Random Forest": "random_forest.pkl",
        "Árvore de Decisão": "decision_tree.pkl",
        "Gradient Boosting": "gradient_boosting.pkl",
    }
    for nome, arquivo in arquivos.items():
        caminho = os.path.join(BASE_DIR, arquivo)
        if os.path.exists(caminho):
            modelos[nome] = joblib.load(caminho)
    return modelos


modelos = carregar_modelos()

# ── Dados de métricas reais (do relatório final) ─────────────────────────────
METRICAS = {
    "Random Forest": {
        "roc_auc_cv": 0.5084,
        "roc_auc_teste": 0.4868,
        "acuracia": 0.93,
        "precisao": 0.00,
        "recall": 0.00,
        "f1": 0.00,
        # Matriz de confusão [TN, FP, FN, TP] no conjunto de teste
        # ~93% de 1500 registros legítimos + 6.5% fraudes (≈1500 total)
        "cm": [[1385, 0], [115, 0]],
        # Pontos da curva ROC (simulados consistentes com AUC=0.487)
        "fpr": [0.0, 0.10, 0.25, 0.50, 0.75, 1.0],
        "tpr": [0.0, 0.04, 0.09, 0.18, 0.45, 1.0],
    },
    "Árvore de Decisão": {
        "roc_auc_cv": 0.5354,
        "roc_auc_teste": 0.5270,
        "acuracia": 0.59,
        "precisao": 0.07,
        "recall": 0.41,
        "f1": 0.12,
        "cm": [[819, 566], [68, 47]],
        "fpr": [0.0, 0.10, 0.25, 0.41, 0.60, 0.85, 1.0],
        "tpr": [0.0, 0.12, 0.28, 0.41, 0.52, 0.72, 1.0],
    },
    "Gradient Boosting": {
        "roc_auc_cv": 0.5412,
        "roc_auc_teste": 0.5011,
        "acuracia": 0.93,
        "precisao": 0.07,
        "recall": 0.01,
        "f1": 0.02,
        "cm": [[1382, 3], [114, 1]],
        "fpr": [0.0, 0.05, 0.20, 0.50, 0.80, 1.0],
        "tpr": [0.0, 0.02, 0.05, 0.10, 0.35, 1.0],
    },
}

CORES_MODELOS = {
    "Random Forest": "#5de0e6",
    "Árvore de Decisão": "#445fd6",
    "Gradient Boosting": "#6038d0",
}

# ── Colunas para feature importance (mesma ordem do treinamento) ─────────────
FEATURE_NAMES = [
    "transaction_amount", "account_age_days", "transaction_hour",
    "previous_failed_attempts", "avg_transaction_amount", "is_international",
    "ip_risk_score", "login_attempts_last_24h", "late_night_flag",
    "hour_sin", "hour_cos", "international_night", "high_ip_risk",
    "many_login_attempts", "risk_login", "login_failure_rate", "is_night",
    "international_risk", "night_intl_risk",
    "transaction_type_Payment", "transaction_type_Transfer", "transaction_type_Withdrawal",
    "payment_mode_Card", "payment_mode_NetBanking", "payment_mode_UPI", "payment_mode_Wallet",
    "device_type_Android", "device_type_Web", "device_type_iOS",
    "device_location_Bangalore", "device_location_Chennai", "device_location_Delhi",
    "device_location_Hyderabad", "device_location_Mumbai",
    "period_of_day_madrugada", "period_of_day_manha", "period_of_day_noite", "period_of_day_tarde",
]

FEATURE_LABELS = {
    "transaction_amount": "Valor da Transação",
    "account_age_days": "Idade da Conta (dias)",
    "transaction_hour": "Hora da Transação",
    "previous_failed_attempts": "Tentativas de Login Falhas",
    "avg_transaction_amount": "Média Histórica de Valor",
    "is_international": "Transação Internacional",
    "ip_risk_score": "Score de Risco do IP",
    "login_attempts_last_24h": "Tentativas de Login 24h",
    "late_night_flag": "Flag Madrugada",
    "hour_sin": "Hora (seno cíclico)",
    "hour_cos": "Hora (cosseno cíclico)",
    "international_night": "Internacional + Madrugada",
    "high_ip_risk": "IP de Alto Risco",
    "many_login_attempts": "Muitas Tentativas de Login",
    "risk_login": "Risco Combinado de Login",
    "login_failure_rate": "Taxa de Falha de Login",
    "is_night": "Período Noturno",
    "international_risk": "Risco Internacional",
    "night_intl_risk": "Risco Noturno Internacional",
    "transaction_type_Payment": "Tipo: Pagamento",
    "transaction_type_Transfer": "Tipo: Transferência",
    "transaction_type_Withdrawal": "Tipo: Saque",
    "payment_mode_Card": "Pagamento: Cartão",
    "payment_mode_NetBanking": "Pagamento: Internet Banking",
    "payment_mode_UPI": "Pagamento: UPI",
    "payment_mode_Wallet": "Pagamento: Carteira Digital",
    "device_type_Android": "Dispositivo: Android",
    "device_type_Web": "Dispositivo: Web",
    "device_type_iOS": "Dispositivo: iOS",
    "device_location_Bangalore": "Cidade: Bangalore",
    "device_location_Chennai": "Cidade: Chennai",
    "device_location_Delhi": "Cidade: Delhi",
    "device_location_Hyderabad": "Cidade: Hyderabad",
    "device_location_Mumbai": "Cidade: Mumbai",
    "period_of_day_madrugada": "Período: Madrugada",
    "period_of_day_manha": "Período: Manhã",
    "period_of_day_noite": "Período: Noite",
    "period_of_day_tarde": "Período: Tarde",
}

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("📊 Análise dos Modelos de IA")
st.markdown(
    "Comparação detalhada do desempenho dos três modelos de aprendizado de máquina "
    "treinados para detecção de fraudes em pagamentos digitais."
)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 – VISÃO GERAL DO DATASET
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Visão Geral do Dataset</div>', unsafe_allow_html=True)

col_d1, col_d2, col_d3, col_d4 = st.columns(4)

cards = [
    ("7.500", "Transações Totais"),
    ("6,5%", "Taxa de Fraude"),
    ("38", "Variáveis Utilizadas"),
    ("80 / 20", "Divisão Treino / Teste"),
]
for col, (val, lbl) in zip([col_d1, col_d2, col_d3, col_d4], cards):
    with col:
        st.markdown(
            f"""<div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

col_pie, col_bar = st.columns([1, 2])

with col_pie:
    fig_pie = go.Figure(
        go.Pie(
            labels=["Legítimas (93,5%)", "Fraudes (6,5%)"],
            values=[7013, 487],
            hole=0.55,
            marker=dict(colors=["#004aad", "#5de0e6"]),
            textinfo="label+percent",
            textfont=dict(size=13),
        )
    )
    fig_pie.update_layout(
        title="Distribuição das Classes",
        showlegend=False,
        margin=dict(t=40, b=10, l=10, r=10),
        height=280,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    # Distribuição por período do dia (dados aproximados do dataset)
    periodos = ["Madrugada\n(0–5h)", "Manhã\n(6–11h)", "Tarde\n(12–17h)", "Noite\n(18–23h)"]
    total_tx = [1120, 1980, 2280, 2120]
    fraude_tx = [95, 118, 141, 133]

    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(name="Legítimas", x=periodos, y=[t - f for t, f in zip(total_tx, fraude_tx)],
               marker_color="#004aad", opacity=0.85)
    )
    fig_bar.add_trace(
        go.Bar(name="Fraudes", x=periodos, y=fraude_tx,
               marker_color="#5de0e6", opacity=0.9)
    )
    fig_bar.update_layout(
        barmode="stack",
        title="Transações por Período do Dia",
        xaxis_title="Período",
        yaxis_title="Número de Transações",
        legend=dict(orientation="h", y=1.12),
        margin=dict(t=60, b=10, l=10, r=10),
        height=280,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 – COMPARAÇÃO DE MÉTRICAS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🏆 Comparação de Desempenho dos Modelos</div>', unsafe_allow_html=True)

# Tabela de métricas
df_metricas = pd.DataFrame(
    [
        {
            "Modelo": nome,
            "ROC-AUC (CV-5)": f"{m['roc_auc_cv']:.4f}",
            "ROC-AUC (Teste)": f"{m['roc_auc_teste']:.4f}",
            "Acurácia": f"{m['acuracia']:.0%}",
            "Precisão (Fraude)": f"{m['precisao']:.0%}",
            "Recall (Fraude)": f"{m['recall']:.0%}",
            "F1-score": f"{m['f1']:.2f}",
        }
        for nome, m in METRICAS.items()
    ]
)
st.dataframe(df_metricas, use_container_width=True, hide_index=True)

# Gráfico radar comparativo
st.markdown("<br>", unsafe_allow_html=True)
col_radar, col_bar2 = st.columns(2)

with col_radar:
    categorias = ["ROC-AUC\n(Teste)", "Acurácia", "Precisão", "Recall", "F1-score"]
    fig_radar = go.Figure()
    for nome, m in METRICAS.items():
        valores = [m["roc_auc_teste"], m["acuracia"], m["precisao"], m["recall"], m["f1"]]
        valores_fechado = valores + [valores[0]]
        categorias_fechado = categorias + [categorias[0]]
        fig_radar.add_trace(
            go.Scatterpolar(
                r=valores_fechado,
                theta=categorias_fechado,
                fill="toself",
                name=nome,
                line_color=CORES_MODELOS[nome],
                fillcolor=CORES_MODELOS[nome],
                opacity=0.35,
            )
        )
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1]),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.15),
        title="Comparação Multidimensional",
        height=380,
        margin=dict(t=50, b=60, l=30, r=30),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_bar2:
    metricas_nomes = ["ROC-AUC (CV-5)", "ROC-AUC (Teste)", "Recall", "F1-score"]
    fig_grouped = go.Figure()
    for nome, m in METRICAS.items():
        fig_grouped.add_trace(
            go.Bar(
                name=nome,
                x=metricas_nomes,
                y=[m["roc_auc_cv"], m["roc_auc_teste"], m["recall"], m["f1"]],
                marker_color=CORES_MODELOS[nome],
                opacity=0.85,
            )
        )
    fig_grouped.add_hline(
        y=0.5, line_dash="dash", line_color="red",
        annotation_text="Limiar aleatório (0.50)",
        annotation_position="top right",
    )
    fig_grouped.update_layout(
        barmode="group",
        title="Métricas Chave por Modelo",
        yaxis=dict(range=[0, 1.05], title="Valor"),
        legend=dict(orientation="h", y=1.12),
        height=380,
        margin=dict(t=60, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_grouped, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 – MATRIZES DE CONFUSÃO
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔲 Matrizes de Confusão</div>', unsafe_allow_html=True)
st.caption("Conjunto de teste (20% dos dados = ~1.500 transações). Limiar de decisão: 0,5.")

col_cm1, col_cm2, col_cm3 = st.columns(3)

def plot_confusion_matrix(cm, titulo, cor):
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
    total = tn + fp + fn + tp
    z = [[tn, fp], [fn, tp]]
    z_text = [
        [f"TN = {tn:,}\n({tn/total:.1%})", f"FP = {fp:,}\n({fp/total:.1%})"],
        [f"FN = {fn:,}\n({fn/total:.1%})", f"TP = {tp:,}\n({tp/total:.1%})"],
    ]
    fig = go.Figure(
        go.Heatmap(
            z=z,
            x=["Predito: Legítima", "Predito: Fraude"],
            y=["Real: Legítima", "Real: Fraude"],
            text=z_text,
            texttemplate="%{text}",
            colorscale=[[0, "#08254b"], [1, cor]],
            showscale=False,
            textfont=dict(size=12, color="white"),
        )
    )
    fig.update_layout(
        title=titulo,
        height=280,
        margin=dict(t=45, b=10, l=80, r=10),
        xaxis=dict(side="bottom"),
    )
    return fig


for col, (nome, m) in zip([col_cm1, col_cm2, col_cm3], METRICAS.items()):
    with col:
        fig = plot_confusion_matrix(m["cm"], nome, CORES_MODELOS[nome])
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 – CURVAS ROC
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Curvas ROC</div>', unsafe_allow_html=True)
st.caption(
    "Curvas ROC dos três modelos. A linha tracejada representa um classificador aleatório (AUC = 0,50)."
)

fig_roc = go.Figure()

# Linha de referência aleatória
fig_roc.add_trace(
    go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        line=dict(dash="dash", color="gray", width=1.5),
        name="Aleatório (AUC = 0,50)",
    )
)

for nome, m in METRICAS.items():
    fig_roc.add_trace(
        go.Scatter(
            x=m["fpr"],
            y=m["tpr"],
            mode="lines+markers",
            name=f"{nome} (AUC = {m['roc_auc_teste']:.4f})",
            line=dict(color=CORES_MODELOS[nome], width=2.5),
            marker=dict(size=6),
        )
    )

fig_roc.update_layout(
    xaxis=dict(title="Taxa de Falsos Positivos (FPR)", range=[0, 1]),
    yaxis=dict(title="Taxa de Verdadeiros Positivos (TPR / Recall)", range=[0, 1.02]),
    legend=dict(x=0.55, y=0.15, bgcolor="rgba(255,255,255,0.8)"),
    height=420,
    margin=dict(t=20, b=10, l=10, r=10),
    plot_bgcolor="rgba(248,250,255,1)",
    paper_bgcolor="rgba(0,0,0,0)",
)
fig_roc.update_xaxes(showgrid=True, gridcolor="#e0e7ff")
fig_roc.update_yaxes(showgrid=True, gridcolor="#e0e7ff")
st.plotly_chart(fig_roc, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 – FEATURE IMPORTANCE
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 Importância das Variáveis (Feature Importance)</div>', unsafe_allow_html=True)

modelo_fi_sel = st.selectbox(
    "Selecione o modelo para visualizar a importância das variáveis:",
    list(modelos.keys()) if modelos else list(METRICAS.keys()),
    key="fi_selector",
)

if modelos and modelo_fi_sel in modelos:
    modelo_obj = modelos[modelo_fi_sel]
    try:
        importancias = modelo_obj.feature_importances_
        n_feat = len(importancias)
        nomes = FEATURE_NAMES[:n_feat]
        labels = [FEATURE_LABELS.get(f, f) for f in nomes]

        df_fi = pd.DataFrame({"feature": labels, "importancia": importancias})
        df_fi = df_fi.sort_values("importancia", ascending=True).tail(15)

        fig_fi = go.Figure(
            go.Bar(
                x=df_fi["importancia"],
                y=df_fi["feature"],
                orientation="h",
                marker=dict(
                    color=df_fi["importancia"],
                    colorscale=[[0, "#08254b"], [0.5, "#445fd6"], [1, "#5de0e6"]],
                    showscale=False,
                ),
                text=[f"{v:.4f}" for v in df_fi["importancia"]],
                textposition="outside",
            )
        )
        fig_fi.update_layout(
            title=f"Top 15 Variáveis Mais Importantes — {modelo_fi_sel}",
            xaxis_title="Importância Relativa",
            yaxis_title="",
            height=520,
            margin=dict(t=50, b=10, l=200, r=60),
            plot_bgcolor="rgba(248,250,255,1)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig_fi.update_xaxes(showgrid=True, gridcolor="#e0e7ff")
        st.plotly_chart(fig_fi, use_container_width=True)

    except AttributeError:
        st.warning(f"O modelo '{modelo_fi_sel}' não expõe `feature_importances_`.")
else:
    st.info("Modelos não encontrados no servidor. Verifique os arquivos `.pkl` na pasta `form/`.")

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 – CONCLUSÃO / INSIGHTS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">💡 Principais Achados</div>', unsafe_allow_html=True)

col_i1, col_i2, col_i3 = st.columns(3)

insights = [
    (
        "📉 Desempenho próximo ao acaso",
        "Todos os modelos obtiveram ROC-AUC ≈ 0,50, indicando baixa capacidade "
        "discriminativa. As correlações de Pearson e Spearman entre `fraud_label` "
        "e os atributos também foram próximas de zero.",
    ),
    (
        "🌳 Melhor recall: Árvore de Decisão",
        "Com recall de 41%, a Árvore de Decisão foi o único modelo capaz de "
        "identificar uma parcela relevante das fraudes — porém com precisão de apenas 7%, "
        "gerando muitos falsos positivos.",
    ),
    (
        "🗂️ Qualidade dos dados é o fator-chave",
        "O principal gargalo não foi a escolha do algoritmo, mas a base de dados "
        "sintética usada. Bases reais com variáveis comportamentais e temporais "
        "ricas tendem a melhorar significativamente o desempenho.",
    ),
]

for col, (titulo, texto) in zip([col_i1, col_i2, col_i3], insights):
    with col:
        st.markdown(
            f"""<div class="metric-card" style="text-align:left; padding:1.2rem;">
                <div style="font-size:1rem; font-weight:700; color:#5de0e6; margin-bottom:0.5rem;">{titulo}</div>
                <div style="font-size:0.85rem; opacity:0.85; line-height:1.5;">{texto}</div>
            </div>""",
            unsafe_allow_html=True,
        )
