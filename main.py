from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots

# ======================================================================
# Configuração da página
# ======================================================================
st.set_page_config(
    page_title="Dashboard de Ações",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

ACOES = [
    "ITUB4.SA", "PETR4.SA", "VALE3.SA", "ABEV3.SA", "BBDC4.SA",
    "BBAS3.SA", "MGLU3.SA", "WEGE3.SA", "LREN3.SA", "GGBR4.SA",
]
BENCHMARK = "^BVSP"
DATA_INICIO = "2020-01-01"
DIAS_UTEIS_ANO = 252

PALETA = [
    "#7C5CFF", "#22D3EE", "#F472B6", "#FBBF24", "#34D399",
    "#FB7185", "#60A5FA", "#A3E635", "#F97316", "#C084FC",
]
VERDE, VERMELHO, NEUTRO = "#22C55E", "#EF4444", "#94A3B8"

# ======================================================================
# Estilo (CSS)
# ======================================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stMarkdown, .stText { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
#MainMenu, footer { visibility: hidden; }

/* Cabeçalho */
.hero {
    background: radial-gradient(1200px 300px at 0% 0%, rgba(124,92,255,.35), transparent 60%),
                radial-gradient(900px 300px at 100% 0%, rgba(34,211,238,.25), transparent 60%),
                linear-gradient(135deg, #131A2A 0%, #0F1524 100%);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 22px;
    box-shadow: 0 10px 40px rgba(0,0,0,.35);
}
.hero h1 {
    margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -.02em;
    background: linear-gradient(90deg, #FFFFFF 0%, #C4B5FD 50%, #67E8F9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { margin: 6px 0 0 0; color: #9AA4BF; font-size: 1rem; }
.hero .chips { margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap; }
.chip {
    background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.10);
    color: #CBD5E1; padding: 4px 12px; border-radius: 999px; font-size: .8rem; font-weight: 500;
}
.chip b { color: #fff; }

/* Cards de KPI */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 18px; }
.kpi {
    background: linear-gradient(180deg, #151C2E 0%, #111727 100%);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 16px; padding: 16px 18px; position: relative; overflow: hidden;
    transition: transform .15s ease, border-color .15s ease;
}
.kpi:hover { transform: translateY(-2px); border-color: rgba(124,92,255,.45); }
.kpi::before {
    content: ""; position: absolute; inset: 0 0 auto 0; height: 3px;
    background: var(--accent, #7C5CFF);
}
.kpi .label { color: #8B95B0; font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; }
.kpi .value { color: #F8FAFC; font-size: 1.65rem; font-weight: 800; margin-top: 6px; letter-spacing: -.02em; }
.kpi .sub { color: #8B95B0; font-size: .8rem; margin-top: 2px; }
.pos { color: #22C55E !important; }
.neg { color: #EF4444 !important; }

/* Cards de ativos */
.asset-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }
.asset {
    background: #121929; border: 1px solid rgba(255,255,255,.06); border-radius: 14px;
    padding: 14px 16px; display: flex; flex-direction: column; gap: 4px;
}
.asset .top { display: flex; justify-content: space-between; align-items: center; }
.asset .ticker { font-weight: 700; color: #E2E8F0; font-size: .95rem; }
.asset .badge { font-size: .78rem; font-weight: 700; padding: 2px 9px; border-radius: 999px; }
.badge.pos { background: rgba(34,197,94,.14); }
.badge.neg { background: rgba(239,68,68,.14); }
.asset .price { color: #94A3B8; font-size: .8rem; }
.asset .bar { height: 5px; background: rgba(255,255,255,.06); border-radius: 99px; overflow: hidden; margin-top: 6px; }
.asset .bar span { display: block; height: 100%; border-radius: 99px; }

/* Títulos de seção */
.section-title {
    display: flex; align-items: center; gap: 10px;
    font-size: 1.15rem; font-weight: 700; color: #E6E9F2; margin: 8px 0 4px 0;
}
.section-title::before {
    content: ""; width: 4px; height: 20px; border-radius: 4px;
    background: linear-gradient(180deg, #7C5CFF, #22D3EE);
}
.section-sub { color: #8B95B0; font-size: .88rem; margin-bottom: 10px; }

/* Abas */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #111727; padding: 6px; border-radius: 14px; }
.stTabs [data-baseweb="tab"] {
    height: 42px; border-radius: 10px; padding: 0 18px; color: #9AA4BF; font-weight: 600;
}
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7C5CFF, #5B3FE0) !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F1524 0%, #0B0F1A 100%); border-right: 1px solid rgba(255,255,255,.06); }
section[data-testid="stSidebar"] .stButton > button {
    width: 100%; border-radius: 12px; border: 0; font-weight: 700; padding: .6rem 1rem;
    background: linear-gradient(135deg, #7C5CFF 0%, #22D3EE 100%); color: white;
    box-shadow: 0 6px 18px rgba(124,92,255,.35);
}
section[data-testid="stSidebar"] .stButton > button:hover { filter: brightness(1.08); }
.side-info { font-size: .78rem; color: #8B95B0; text-align: center; margin-top: 6px; }

/* Container dos gráficos */
div[data-testid="stPlotlyChart"] {
    background: #111727; border: 1px solid rgba(255,255,255,.06);
    border-radius: 16px; padding: 8px 6px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ======================================================================
# Dados
# ======================================================================
@st.cache_data(ttl=60 * 60, show_spinner="Baixando cotações do Yahoo Finance...")
def carregar_dados(tickers: tuple[str, ...], inicio: str):
    """Baixa OHLCV desde `inicio` até o último pregão disponível (sem data final fixa)."""
    amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    bruto = yf.download(
        list(tickers), start=inicio, end=amanha,
        auto_adjust=True, progress=False, group_by="column",
    )
    bruto = bruto.dropna(how="all")
    return bruto, datetime.now()


def fmt_pct(x, sinal=True):
    if pd.isna(x):
        return "—"
    return f"{x:+.1%}" if sinal else f"{x:.1%}"


def classe(x):
    return "pos" if x > 0 else "neg" if x < 0 else ""


def estilo_fig(fig, altura=420, titulo=None):
    fig.update_layout(
        template="plotly_dark",
        height=altura,
        title=dict(text=titulo, font=dict(size=15, color="#E6E9F2"), x=0.01) if titulo else None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#9AA4BF", size=12),
        margin=dict(l=10, r=10, t=50 if titulo else 20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#1E2638", bordercolor="#7C5CFF", font=dict(color="#fff")),
        colorway=PALETA,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False, showline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,.05)", zeroline=False, showline=False)
    return fig


def max_drawdown(serie: pd.Series) -> float:
    return float((serie / serie.cummax() - 1).min())


# ======================================================================
# Sidebar
# ======================================================================
with st.sidebar:
    st.markdown("## ⚙️ Painel de controle")

    if st.button("🔄 Atualizar dados", help="Limpa o cache e baixa as cotações mais recentes"):
        carregar_dados.clear()
        st.rerun()

bruto, horario_carga = carregar_dados(tuple(ACOES + [BENCHMARK]), DATA_INICIO)

fechamento_todos = bruto["Close"].ffill()
ibov_total = fechamento_todos[BENCHMARK]
fechamento = fechamento_todos[ACOES]

with st.sidebar:
    st.markdown(
        f"<div class='side-info'>Dados carregados em {horario_carga:%d/%m/%Y %H:%M}<br>"
        f"Último pregão: <b>{fechamento.index.max():%d/%m/%Y}</b></div>",
        unsafe_allow_html=True,
    )
    st.divider()

    lista_acoes = st.multiselect(
        "📌 Ações",
        options=ACOES,
        default=["ITUB4.SA", "PETR4.SA", "VALE3.SA", "WEGE3.SA"],
        help="Selecione as ações que compõem a carteira",
    )

    data_min = fechamento.index.min().to_pydatetime()
    data_max = fechamento.index.max().to_pydatetime()
    atalho = st.radio(
        "🗓️ Período", ["1M", "6M", "1A", "3A", "Tudo", "Personalizado"],
        index=4, horizontal=True, key="periodo",
    )
    meses = {"1M": 1, "6M": 6, "1A": 12, "3A": 36}
    if atalho in meses:
        inicio_sel = max(data_min, data_max - pd.DateOffset(months=meses[atalho]))
        intervalo = (inicio_sel.to_pydatetime() if hasattr(inicio_sel, "to_pydatetime") else inicio_sel, data_max)
    elif atalho == "Tudo":
        intervalo = (data_min, data_max)
    else:
        intervalo = st.slider(
            "Intervalo de datas",
            min_value=data_min, max_value=data_max,
            value=(data_min, data_max), format="DD/MM/YYYY",
        )

    st.divider()
    valor_por_acao = st.number_input("💰 Valor investido por ação (R$)", min_value=100, value=1000, step=100)
    taxa_livre = st.number_input(
        "🏦 Taxa livre de risco (% a.a.)", min_value=0.0, max_value=30.0, value=10.5, step=0.25,
        help="Usada no cálculo do Índice de Sharpe (ex.: CDI)",
    ) / 100
    janela_vol = st.select_slider("📐 Janela da volatilidade móvel (dias)", options=[10, 21, 42, 63, 126], value=21)

if not lista_acoes:
    st.markdown(
        "<div class='hero'><h1>Dashboard de Ações</h1>"
        "<p>Selecione ao menos uma ação na barra lateral para começar.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ======================================================================
# Cálculos
# ======================================================================
precos = fechamento.loc[intervalo[0]:intervalo[1], lista_acoes].dropna(how="all")
ibov = ibov_total.loc[intervalo[0]:intervalo[1]].dropna()

if len(precos) < 2:
    st.warning("Período muito curto. Escolha um intervalo maior.")
    st.stop()

base = precos.apply(lambda s: s / s.dropna().iloc[0])         # 1.0 no início
carteira = (base * valor_por_acao).sum(axis=1)                # buy & hold, pesos iniciais iguais
carteira_norm = carteira / carteira.iloc[0]
ibov_norm = ibov / ibov.iloc[0]

ret_diario = precos.pct_change().dropna(how="all")
ret_carteira = carteira.pct_change().dropna()
ret_ibov = ibov.pct_change().dropna()

anos = max((precos.index[-1] - precos.index[0]).days / 365.25, 1 / 365.25)

def estatisticas(serie_preco: pd.Series, ret: pd.Series) -> dict:
    serie_preco = serie_preco.dropna()
    total = serie_preco.iloc[-1] / serie_preco.iloc[0] - 1
    cagr = (1 + total) ** (1 / anos) - 1
    vol = ret.std() * np.sqrt(DIAS_UTEIS_ANO)
    sharpe = (cagr - taxa_livre) / vol if vol > 0 else np.nan
    negativos = ret[ret < 0]
    sortino_den = negativos.std() * np.sqrt(DIAS_UTEIS_ANO)
    sortino = (cagr - taxa_livre) / sortino_den if sortino_den > 0 else np.nan
    var95 = ret.quantile(0.05)
    return {
        "Retorno total": total, "Retorno anualizado": cagr, "Volatilidade a.a.": vol,
        "Sharpe": sharpe, "Sortino": sortino, "Máx. drawdown": max_drawdown(serie_preco),
        "VaR 95% (1 dia)": var95, "Melhor dia": ret.max(), "Pior dia": ret.min(),
        "Preço inicial": serie_preco.iloc[0], "Preço final": serie_preco.iloc[-1],
    }

stats = pd.DataFrame({a: estatisticas(precos[a], ret_diario[a].dropna()) for a in lista_acoes}).T
stats_cart = estatisticas(carteira, ret_carteira)
stats_ibov = estatisticas(ibov, ret_ibov)

# Beta da carteira x Ibovespa
alinhado = pd.concat([ret_carteira, ret_ibov], axis=1, join="inner").dropna()
beta = alinhado.cov().iloc[0, 1] / alinhado.iloc[:, 1].var() if len(alinhado) > 2 else np.nan

# ======================================================================
# Cabeçalho
# ======================================================================
st.markdown(
    f"""
<div class="hero">
  <h1>📈 Dashboard de Ações · B3</h1>
  <p>Desempenho, risco e correlação da sua carteira comparados ao Ibovespa.</p>
  <div class="chips">
    <span class="chip">Período <b>{intervalo[0]:%d/%m/%Y} → {intervalo[1]:%d/%m/%Y}</b></span>
    <span class="chip">Ativos <b>{len(lista_acoes)}</b></span>
    <span class="chip">Investido <b>R$ {valor_por_acao * len(lista_acoes):,.0f}</b></span>
    <span class="chip">Pregões <b>{len(precos)}</b></span>
  </div>
</div>
""".replace(",", "."),
    unsafe_allow_html=True,
)

valor_final = carteira.iloc[-1]
alpha_ibov = stats_cart["Retorno total"] - stats_ibov["Retorno total"]
kpis = [
    ("Valor final da carteira", f"R$ {valor_final:,.0f}".replace(",", "."),
     f"<span class='{classe(stats_cart['Retorno total'])}'>{fmt_pct(stats_cart['Retorno total'])}</span> no período", "#7C5CFF"),
    ("Retorno anualizado", f"<span class='{classe(stats_cart['Retorno anualizado'])}'>{fmt_pct(stats_cart['Retorno anualizado'])}</span>",
     f"Ibovespa: {fmt_pct(stats_ibov['Retorno anualizado'])}", "#22D3EE"),
    ("vs. Ibovespa", f"<span class='{classe(alpha_ibov)}'>{alpha_ibov * 100:+.1f} p.p.</span>",
     f"Ibov no período: {fmt_pct(stats_ibov['Retorno total'])}", "#F472B6"),
    ("Volatilidade a.a.", fmt_pct(stats_cart["Volatilidade a.a."], False),
     f"Beta vs. Ibov: {beta:.2f}", "#FBBF24"),
    ("Índice de Sharpe", f"{stats_cart['Sharpe']:.2f}",
     f"Sortino: {stats_cart['Sortino']:.2f}", "#34D399"),
    ("Máx. drawdown", f"<span class='neg'>{fmt_pct(stats_cart['Máx. drawdown'])}</span>",
     f"VaR 95% diário: {fmt_pct(stats_cart['VaR 95% (1 dia)'])}", "#EF4444"),
]
st.markdown(
    "<div class='kpi-grid'>" + "".join(
        f"<div class='kpi' style='--accent:{cor}'><div class='label'>{lbl}</div>"
        f"<div class='value'>{val}</div><div class='sub'>{sub}</div></div>"
        for lbl, val, sub, cor in kpis
    ) + "</div>",
    unsafe_allow_html=True,
)

cores = {a: PALETA[ACOES.index(a) % len(PALETA)] for a in ACOES}

# ======================================================================
# Abas
# ======================================================================
aba_desemp, aba_risco, aba_corr, aba_ind, aba_dados = st.tabs(
    ["📈 Desempenho", "⚠️ Risco", "🔗 Correlação & Distribuição", "🕯️ Análise individual", "📋 Dados"]
)

# ---------------------------------------------------------------- Desempenho
with aba_desemp:
    st.markdown("<div class='section-title'>Evolução de R$ 100 investidos</div>"
                "<div class='section-sub'>Preços normalizados (base 100) — compara ativos, carteira e Ibovespa na mesma escala.</div>",
                unsafe_allow_html=True)
    fig = go.Figure()
    for a in lista_acoes:
        fig.add_trace(go.Scatter(x=base.index, y=base[a] * 100, name=a, line=dict(width=1.6, color=cores[a]),
                                 hovertemplate="%{y:.1f}<extra>" + a + "</extra>"))
    fig.add_trace(go.Scatter(x=carteira_norm.index, y=carteira_norm * 100, name="Carteira",
                             line=dict(width=3.5, color="#FFFFFF"),
                             hovertemplate="%{y:.1f}<extra>Carteira</extra>"))
    fig.add_trace(go.Scatter(x=ibov_norm.index, y=ibov_norm * 100, name="Ibovespa",
                             line=dict(width=2.5, color="#FBBF24", dash="dot"),
                             hovertemplate="%{y:.1f}<extra>Ibovespa</extra>"))
    fig.add_hline(y=100, line=dict(color="rgba(255,255,255,.25)", dash="dash", width=1))
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.05, bgcolor="#0F1524"))
    st.plotly_chart(estilo_fig(fig, 520), width="stretch")

    c1, c2 = st.columns([1.1, 1])
    with c1:
        ordem = stats["Retorno total"].sort_values()
        fig = go.Figure(go.Bar(
            x=ordem.values, y=ordem.index, orientation="h",
            marker=dict(color=[VERDE if v > 0 else VERMELHO for v in ordem.values], line=dict(width=0)),
            text=[fmt_pct(v) for v in ordem.values], textposition="outside",
            hovertemplate="%{y}: %{x:.1%}<extra></extra>",
        ))
        fig.add_vline(x=stats_ibov["Retorno total"], line=dict(color="#FBBF24", dash="dot"),
                      annotation_text="Ibovespa", annotation_font_color="#FBBF24")
        fig.update_xaxes(tickformat=".0%")
        st.plotly_chart(estilo_fig(fig, 380, "Retorno total por ação"), width="stretch")
    with c2:
        alocacao = base.iloc[-1] * valor_por_acao
        fig = go.Figure(go.Pie(
            labels=alocacao.index, values=alocacao.values, hole=0.62,
            marker=dict(colors=[cores[a] for a in alocacao.index], line=dict(color="#0B0F1A", width=3)),
            textinfo="percent", hovertemplate="%{label}<br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
        ))
        fig.add_annotation(text=f"<b>R$ {valor_final:,.0f}</b><br><span style='font-size:11px'>valor atual</span>".replace(",", "."),
                           showarrow=False, font=dict(size=18, color="#fff"))
        st.plotly_chart(estilo_fig(fig, 380, "Composição atual da carteira"), width="stretch")

    st.markdown("<div class='section-title'>Performance individual</div>", unsafe_allow_html=True)
    max_abs = stats["Retorno total"].abs().max() or 1
    cards = []
    for a in stats.sort_values("Retorno total", ascending=False).index:
        r = stats.loc[a, "Retorno total"]
        largura = min(abs(r) / max_abs * 100, 100)
        cor = VERDE if r >= 0 else VERMELHO
        cards.append(
            f"<div class='asset'><div class='top'><span class='ticker'>"
            f"<span style='color:{cores[a]}'>●</span> {a.replace('.SA', '')}</span>"
            f"<span class='badge {classe(r)}'>{fmt_pct(r)}</span></div>"
            f"<div class='price'>R$ {stats.loc[a, 'Preço inicial']:.2f} → <b style='color:#E2E8F0'>R$ {stats.loc[a, 'Preço final']:.2f}</b></div>"
            f"<div class='price'>Vol. {fmt_pct(stats.loc[a, 'Volatilidade a.a.'], False)} · Sharpe {stats.loc[a, 'Sharpe']:.2f}</div>"
            f"<div class='bar'><span style='width:{largura:.0f}%;background:{cor}'></span></div></div>"
        )
    st.markdown("<div class='asset-grid'>" + "".join(cards) + "</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------- Risco
with aba_risco:
    st.markdown("<div class='section-title'>Drawdown</div>"
                "<div class='section-sub'>Quanto cada série está abaixo do seu pico anterior — mostra a profundidade e a duração das quedas.</div>",
                unsafe_allow_html=True)
    dd_cart = carteira / carteira.cummax() - 1
    dd_ibov = ibov / ibov.cummax() - 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dd_cart.index, y=dd_cart, name="Carteira", fill="tozeroy",
                             line=dict(color=VERMELHO, width=1.5), fillcolor="rgba(239,68,68,.25)",
                             hovertemplate="%{y:.1%}<extra>Carteira</extra>"))
    fig.add_trace(go.Scatter(x=dd_ibov.index, y=dd_ibov, name="Ibovespa",
                             line=dict(color="#FBBF24", width=1.5, dash="dot"),
                             hovertemplate="%{y:.1%}<extra>Ibovespa</extra>"))
    pior = dd_cart.idxmin()
    fig.add_annotation(x=pior, y=dd_cart.min(), text=f"Pior queda {dd_cart.min():.1%}<br>{pior:%d/%m/%Y}",
                       showarrow=True, arrowcolor="#fff", font=dict(color="#fff"), bgcolor="#1E2638", ay=40)
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(estilo_fig(fig, 380), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        vol_movel = ret_diario.rolling(janela_vol).std() * np.sqrt(DIAS_UTEIS_ANO)
        vol_cart = ret_carteira.rolling(janela_vol).std() * np.sqrt(DIAS_UTEIS_ANO)
        fig = go.Figure()
        for a in lista_acoes:
            fig.add_trace(go.Scatter(x=vol_movel.index, y=vol_movel[a], name=a,
                                     line=dict(width=1.2, color=cores[a]), opacity=0.7))
        fig.add_trace(go.Scatter(x=vol_cart.index, y=vol_cart, name="Carteira", line=dict(width=3, color="#FFFFFF")))
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(estilo_fig(fig, 420, f"Volatilidade móvel anualizada ({janela_vol} dias)"), width="stretch")
    with c2:
        dispersao = stats.copy()
        dispersao.loc["Carteira"] = pd.Series(stats_cart)
        dispersao.loc["Ibovespa"] = pd.Series(stats_ibov)
        fig = go.Figure()
        for nome, linha in dispersao.iterrows():
            destaque = nome in ("Carteira", "Ibovespa")
            fig.add_trace(go.Scatter(
                x=[linha["Volatilidade a.a."]], y=[linha["Retorno anualizado"]], mode="markers+text",
                name=nome, text=[nome.replace(".SA", "")], textposition="top center",
                marker=dict(size=22 if destaque else 15,
                            color="#FFFFFF" if nome == "Carteira" else "#FBBF24" if nome == "Ibovespa" else cores[nome],
                            symbol="star" if destaque else "circle", line=dict(width=1, color="#0B0F1A")),
                hovertemplate=f"<b>{nome}</b><br>Vol: %{{x:.1%}}<br>Retorno a.a.: %{{y:.1%}}<br>Sharpe: {linha['Sharpe']:.2f}<extra></extra>",
                showlegend=False,
            ))
        fig.add_hline(y=taxa_livre, line=dict(color="rgba(34,211,238,.5)", dash="dash"),
                      annotation_text=f"Livre de risco {taxa_livre:.1%}", annotation_font_color="#22D3EE")
        fig.update_xaxes(tickformat=".0%", title="Volatilidade anualizada (risco)")
        fig.update_yaxes(tickformat=".0%", title="Retorno anualizado")
        st.plotly_chart(estilo_fig(fig, 420, "Risco × Retorno"), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        ordem = stats["Máx. drawdown"].sort_values(ascending=False)
        fig = go.Figure(go.Bar(
            x=ordem.index.str.replace(".SA", ""), y=ordem.values,
            marker=dict(color=ordem.values, colorscale=[[0, "#7F1D1D"], [1, "#FCA5A5"]], line=dict(width=0)),
            text=[f"{v:.0%}" for v in ordem.values], textposition="outside",
            hovertemplate="%{x}: %{y:.1%}<extra></extra>",
        ))
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(estilo_fig(fig, 360, "Máximo drawdown por ação"), width="stretch")
    with c2:
        ordem = stats["Sharpe"].sort_values()
        fig = go.Figure(go.Bar(
            x=ordem.values, y=ordem.index.str.replace(".SA", ""), orientation="h",
            marker=dict(color=[VERDE if v > 0 else VERMELHO for v in ordem.values], line=dict(width=0)),
            text=[f"{v:.2f}" for v in ordem.values], textposition="outside",
        ))
        fig.add_vline(x=stats_cart["Sharpe"], line=dict(color="#FFFFFF", dash="dot"),
                      annotation_text="Carteira", annotation_font_color="#FFFFFF")
        st.plotly_chart(estilo_fig(fig, 360, "Índice de Sharpe por ação"), width="stretch")

# ---------------------------------------------------------------- Correlação & Distribuição
with aba_corr:
    c1, c2 = st.columns([1, 1])
    with c1:
        if len(lista_acoes) > 1:
            corr = ret_diario[lista_acoes].corr()
            rotulos = [a.replace(".SA", "") for a in corr.columns]
            fig = go.Figure(go.Heatmap(
                z=corr.values, x=rotulos, y=rotulos, zmin=-1, zmax=1,
                colorscale=[[0, "#EF4444"], [0.5, "#111727"], [1, "#7C5CFF"]],
                text=np.round(corr.values, 2), texttemplate="%{text}", textfont=dict(size=12),
                hovertemplate="%{x} × %{y}: %{z:.2f}<extra></extra>", xgap=3, ygap=3,
            ))
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(estilo_fig(fig, 460, "Correlação dos retornos diários"), width="stretch")
        else:
            st.info("Selecione 2 ou mais ações para ver a matriz de correlação.")
    with c2:
        fig = go.Figure()
        for a in lista_acoes:
            fig.add_trace(go.Histogram(x=ret_diario[a].dropna(), name=a, opacity=0.55, nbinsx=80,
                                       marker_color=cores[a]))
        fig.add_trace(go.Histogram(x=ret_carteira, name="Carteira", opacity=0.9, nbinsx=80,
                                   marker_color="#FFFFFF"))
        fig.add_vline(x=stats_cart["VaR 95% (1 dia)"], line=dict(color=VERMELHO, dash="dash"),
                      annotation_text="VaR 95%", annotation_font_color=VERMELHO)
        fig.update_layout(barmode="overlay")
        fig.update_xaxes(tickformat=".0%", range=[-0.1, 0.1])
        st.plotly_chart(estilo_fig(fig, 460, "Distribuição dos retornos diários"), width="stretch")

    st.markdown("<div class='section-title'>Retornos mensais da carteira</div>"
                "<div class='section-sub'>Mapa de calor por mês e ano — identifica sazonalidade e meses de estresse.</div>",
                unsafe_allow_html=True)
    mensal = carteira.resample("ME").last().pct_change()
    primeiro_mes = carteira.resample("ME").last().iloc[0] / carteira.iloc[0] - 1
    mensal.iloc[0] = primeiro_mes
    tabela = pd.DataFrame({"Ano": mensal.index.year, "Mes": mensal.index.month, "Ret": mensal.values})
    pivo = tabela.pivot(index="Ano", columns="Mes", values="Ret").reindex(columns=range(1, 13))
    anual = carteira.resample("YE").last()
    anual_ret = anual.pct_change()
    anual_ret.iloc[0] = anual.iloc[0] / carteira.iloc[0] - 1
    pivo["Ano"] = anual_ret.values
    nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez", "Ano"]
    lim = np.nanmax(np.abs(pivo.values)) if np.isfinite(pivo.values).any() else 0.1
    fig = go.Figure(go.Heatmap(
        z=pivo.values, x=nomes_meses, y=pivo.index.astype(str), zmin=-lim, zmax=lim, zmid=0,
        colorscale=[[0, "#B91C1C"], [0.5, "#1E2638"], [1, "#15803D"]],
        text=[[("" if pd.isna(v) else f"{v:+.1%}") for v in linha] for linha in pivo.values],
        texttemplate="%{text}", textfont=dict(size=12, color="#fff"),
        hovertemplate="%{y} · %{x}: %{z:.2%}<extra></extra>", xgap=3, ygap=3, showscale=False,
    ))
    fig.update_yaxes(autorange="reversed", type="category")
    st.plotly_chart(estilo_fig(fig, 90 + 48 * len(pivo)), width="stretch")

# ---------------------------------------------------------------- Análise individual
with aba_ind:
    acao = st.selectbox("Escolha a ação", lista_acoes, format_func=lambda a: a.replace(".SA", ""))
    ohlc = pd.DataFrame({
        c: bruto[c][acao] for c in ["Open", "High", "Low", "Close", "Volume"]
    }).loc[intervalo[0]:intervalo[1]].dropna()

    s = stats.loc[acao]
    mini = [
        ("Preço atual", f"R$ {s['Preço final']:.2f}", f"Início: R$ {s['Preço inicial']:.2f}", cores[acao]),
        ("Retorno no período", f"<span class='{classe(s['Retorno total'])}'>{fmt_pct(s['Retorno total'])}</span>",
         f"a.a.: {fmt_pct(s['Retorno anualizado'])}", "#22D3EE"),
        ("Volatilidade a.a.", fmt_pct(s["Volatilidade a.a."], False), f"Sharpe: {s['Sharpe']:.2f}", "#FBBF24"),
        ("Máx. drawdown", f"<span class='neg'>{fmt_pct(s['Máx. drawdown'])}</span>",
         f"Pior dia: {fmt_pct(s['Pior dia'])}", "#EF4444"),
        ("Máx. / Mín. período", f"R$ {ohlc['High'].max():.2f}", f"Mín.: R$ {ohlc['Low'].min():.2f}", "#34D399"),
    ]
    st.markdown(
        "<div class='kpi-grid'>" + "".join(
            f"<div class='kpi' style='--accent:{cor}'><div class='label'>{lbl}</div>"
            f"<div class='value'>{val}</div><div class='sub'>{sub}</div></div>"
            for lbl, val, sub, cor in mini
        ) + "</div>",
        unsafe_allow_html=True,
    )

    tipo = st.radio("Tipo de gráfico", ["Candlestick", "Linha"], horizontal=True, label_visibility="collapsed")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)
    if tipo == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=ohlc.index, open=ohlc["Open"], high=ohlc["High"], low=ohlc["Low"], close=ohlc["Close"],
            name=acao, increasing=dict(line_color=VERDE, fillcolor=VERDE),
            decreasing=dict(line_color=VERMELHO, fillcolor=VERMELHO),
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=ohlc.index, y=ohlc["Close"], name=acao, fill="tozeroy",
                                 line=dict(color=cores[acao], width=2),
                                 fillcolor="rgba(124,92,255,.12)"), row=1, col=1)
    # médias móveis calculadas sobre o histórico completo para não "começarem" no meio do gráfico
    close_full = fechamento[acao]
    for janela, cor in [(20, "#22D3EE"), (50, "#FBBF24"), (200, "#F472B6")]:
        mm = close_full.rolling(janela).mean().loc[intervalo[0]:intervalo[1]]
        fig.add_trace(go.Scatter(x=mm.index, y=mm, name=f"MM{janela}", line=dict(color=cor, width=1.4)), row=1, col=1)
    cores_vol = [VERDE if c >= o else VERMELHO for c, o in zip(ohlc["Close"], ohlc["Open"])]
    fig.add_trace(go.Bar(x=ohlc.index, y=ohlc["Volume"], name="Volume", marker_color=cores_vol,
                         opacity=0.6, showlegend=False), row=2, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False, hovermode="x unified")
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    st.plotly_chart(estilo_fig(fig, 640, f"{acao.replace('.SA', '')} · preço, médias móveis e volume"),
                    width="stretch")

# ---------------------------------------------------------------- Dados
with aba_dados:
    st.markdown("<div class='section-title'>Tabela de indicadores</div>", unsafe_allow_html=True)
    tabela_stats = stats.copy()
    tabela_stats.loc["Carteira"] = pd.Series(stats_cart)
    tabela_stats.loc["Ibovespa"] = pd.Series(stats_ibov)
    colunas_pct = ["Retorno total", "Retorno anualizado", "Volatilidade a.a.", "Máx. drawdown",
                   "VaR 95% (1 dia)", "Melhor dia", "Pior dia"]
    st.dataframe(
        tabela_stats.style
        .format({c: "{:+.2%}" for c in colunas_pct} | {"Sharpe": "{:.2f}", "Sortino": "{:.2f}",
                                                       "Preço inicial": "{:,.2f}", "Preço final": "{:,.2f}"})
        .map(lambda v: f"color: {VERDE if v > 0 else VERMELHO if v < 0 else NEUTRO}; font-weight: 600",
             subset=["Retorno total", "Retorno anualizado", "Sharpe", "Sortino"]),
        width="stretch",
    )

    st.markdown("<div class='section-title'>Cotações de fechamento</div>", unsafe_allow_html=True)
    tabela_precos = precos.copy()
    tabela_precos["Carteira (R$)"] = carteira
    tabela_precos["Ibovespa"] = ibov
    st.dataframe(tabela_precos.sort_index(ascending=False).style.format("{:,.2f}"),
                 width="stretch", height=380)
    st.download_button(
        "⬇️ Baixar cotações (CSV)", tabela_precos.to_csv(sep=";", decimal=",").encode("utf-8-sig"),
        file_name=f"cotacoes_{intervalo[0]:%Y%m%d}_{intervalo[1]:%Y%m%d}.csv", mime="text/csv",
    )

st.markdown(
    "<div style='text-align:center;color:#5B6584;font-size:.78rem;margin-top:30px'>"
    "Fonte: Yahoo Finance · preços ajustados por proventos · carteira buy &amp; hold com aportes iguais por ação"
    "</div>",
    unsafe_allow_html=True,
)
