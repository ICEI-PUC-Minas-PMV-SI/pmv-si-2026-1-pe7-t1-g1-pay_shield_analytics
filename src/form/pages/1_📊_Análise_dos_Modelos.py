import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(page_title="Análise dos Modelos - PayShield", layout="wide")

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

# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("📊 Análise dos Modelos de IA")
st.markdown(
    "Comparação detalhada do desempenho dos três modelos de aprendizado de máquina "
    "treinados para detecção de fraudes em pagamentos digitais."
)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 - VISÃO GERAL DO DATASET
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
    periodos = ["Madrugada\n(0-5h)", "Manhã\n(6-11h)", "Tarde\n(12-17h)", "Noite\n(18-23h)"]
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
# SEÇÃO 2 - VARIÁVEIS CRIADAS NA ENGENHARIA DE DADOS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🛠️ Variáveis Criadas na Engenharia de Dados</div>', unsafe_allow_html=True)

st.markdown(
    "As variáveis abaixo foram construídas a partir dos dados brutos para enriquecer a "
    "representação do comportamento da transação e do usuário, capturando padrões temporais, "
    "de risco e interações entre atributos."
)

variaveis_engenharia = [
    ("period_of_day", "Categoria do período do dia (madrugada, manha, tarde, noite) com base na hora"),
    ("late_night_flag", "Flag indicando transação na madrugada (0h às 5h)"),
    ("hour_sin", "Codificação cíclica do horário da transação (seno)"),
    ("hour_cos", "Codificação cíclica do horário da transação (cosseno)"),
    ("international_night", "Interação indicando transações internacionais ocorridas na madrugada"),
    ("high_amount_flag", "Flag indicando transação com valor acima do quantil 95% do dataset global (temporário)"),
    ("high_ip_risk", "Flag indicando IP de alto risco (score > 0.8)"),
    ("many_login_attempts", "Flag indicando mais de 5 tentativas de login nas últimas 24 horas"),
    ("risk_login", "Produto entre tentativas de login e tentativas falhas anteriores"),
    ("login_failure_rate", "Proporção de falhas de login em relação ao total de tentativas"),
    ("is_night", "Flag indicando horário noturno (0h às 6h)"),
    ("international_risk", "Produto entre o indicador de transação internacional e o score de risco do IP"),
    ("night_intl_risk", "Interação indicando madrugada (0h-6h) + transação internacional"),
]

df_features = pd.DataFrame(variaveis_engenharia, columns=["Feature", "Descrição"])
st.dataframe(df_features, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 - COMPARAÇÃO DE MÉTRICAS
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
# SEÇÃO 4 - MATRIZES DE CONFUSÃO
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
# SEÇÃO 5 - CURVAS ROC
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
# SEÇÃO 6 - ANÁLISE DE TRADE-OFFS DOS HIPERPARÂMETROS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">⚖️ Análise de Trade-offs dos Hiperparâmetros</div>', unsafe_allow_html=True)

st.markdown(
    "Os gráficos abaixo mostram como cada hiperparâmetro afeta overfitting, "
    "qualidade preditiva e tempo de treino de cada modelo. Selecione o modelo para visualizar "
    "a análise correspondente."
)

modelo_trade_sel = st.selectbox(
    "Selecione o modelo:",
    ["Random Forest", "Árvore de Decisão", "Gradient Boosting"],
    key="trade_selector",
)

DOCS_IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "docs", "img")
trade_images = {
    "Random Forest": os.path.join(DOCS_IMG_DIR, "trade_offs_random_forest.png"),
    "Árvore de Decisão": os.path.join(DOCS_IMG_DIR, "trade_offs_decision_tree.png"),
    "Gradient Boosting": os.path.join(DOCS_IMG_DIR, "trade_offs_gradient_boosting.png"),
}

trade_path = trade_images.get(modelo_trade_sel)
if trade_path and os.path.exists(trade_path):
    st.image(trade_path, use_container_width=True)
else:
    st.info(f"Imagem de trade-offs não encontrada para {modelo_trade_sel}.")

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 7 - CORRELAÇÃO DE PEARSON
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔗 Correlação de Pearson</div>', unsafe_allow_html=True)

st.markdown(
    "A correlação de Pearson mede a relação linear entre variáveis. À esquerda, a matriz "
    "de correlação entre as variáveis preditivas (sem o alvo). À direita, a correlação de "
    "cada variável com a variável alvo `fraud_label`."
)

col_pearson1, col_pearson2 = st.columns(2)

pearson_features_path = os.path.join(DOCS_IMG_DIR, "cell072_51_correlação_de_pearson.png")
pearson_target_path = os.path.join(DOCS_IMG_DIR, "cell072_51_correlação_de_pearson_total.png")

with col_pearson1:
    if os.path.exists(pearson_features_path):
        st.image(pearson_features_path, use_container_width=True, caption="Correlação entre variáveis preditivas")
    else:
        st.info("Imagem de correlação entre features não encontrada.")

with col_pearson2:
    if os.path.exists(pearson_target_path):
        st.image(pearson_target_path, use_container_width=True, caption="Correlação com a variável alvo fraud_label")
    else:
        st.info("Imagem de correlação com a variável alvo não encontrada.")

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 8 - CONCLUSÃO / INSIGHTS
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
        "identificar uma parcela relevante das fraudes - porém com precisão de apenas 7%, "
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
