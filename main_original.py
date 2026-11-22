import streamlit as st
import pandas as pd
import yfinance as yf

# carregar dados---
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = ','.join(empresas)
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(start='2020-01-01', end='2026-11-20')
    cotacoes_acao = cotacoes_acao['Close']
    return cotacoes_acao

acoes = [
    'ITUB4.SA', 'PETR4.SA', 'VALE3.SA', 'ABEV3.SA',
      'BBDC4.SA', 'BBAS3.SA', 'MGLU3.SA', 'WEGE3.SA', 'LREN3.SA', 'GGBR4.SA'
]

dados = carregar_dados(acoes)

# Interface---
st.write("""
# Dashboard Preços de Ações
O gráfico abaixo mostra a evolução do preço das ações da bolsa.""")

#visuzalização---
st.sidebar.header('Filtros')



# filtros de ações---
lista_acoes = st.sidebar.multiselect("Selecione as ações que deseja visualizar:", dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
        acao_unica = lista_acoes[0]
        dados = dados.rename(columns={acao_unica: 'Close'})
        
# filtros de datas---
data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider(
"Selecione o intervalo de datas:",
min_value=data_inicial, max_value=data_final, value=(data_inicial, data_final))

dados = dados.loc[intervalo_datas[0]:intervalo_datas[1]]

# grafico---
st.line_chart(dados)



# mostrar performance das ações---
st.write("""
### Performance das Ações
O texto abaixo mostra a performance das ações selecionadas no período escolhido.""")
st.write(f"Período selecionado: {intervalo_datas[0].strftime('%d/%m/%Y')} a {intervalo_datas[1].strftime('%d/%m/%Y')}")

texto_perfomance_ativos = ''

carteira = [1000 for acao in lista_acoes]
total_carteira = sum(carteira)

for i, acao in enumerate(lista_acoes):
    # com 1 ação só, a coluna foi renomeada para 'Close' (linha 37)
    coluna = 'Close' if len(lista_acoes) == 1 else acao
    perfomance_ativo = dados[coluna].iloc[-1] / dados[coluna].iloc[0] - 1
    perfomance_ativo = float(perfomance_ativo)

    carteira[i] = carteira[i] * (1 + perfomance_ativo)
    
    if perfomance_ativo > 0:
        texto_perfomance_ativos = texto_perfomance_ativos + f"A ação {acao}: :green[+{perfomance_ativo:.1%}] teve uma performance de {perfomance_ativo:.1%} no período.  \n"
    elif perfomance_ativo < 0:
        texto_perfomance_ativos = texto_perfomance_ativos + f"A ação {acao}: :red[{perfomance_ativo:.1%}] teve uma performance de {perfomance_ativo:.1%} no período.  \n"
    else:
        texto_perfomance_ativos = texto_perfomance_ativos + f"A ação {acao}: :blue[0.0%] não teve variação no período.  \n"

total_carteira_final = sum(carteira)
if total_carteira != 0:
    performance_carteira = total_carteira_final / total_carteira - 1
else:
    performance_carteira = 0

if performance_carteira > 0:
    texto_perfomance_carteira = f"A carteira teve uma performance de :green[+{performance_carteira:.1%}] no período."
elif performance_carteira < 0:
    texto_perfomance_carteira = f"A carteira teve uma performance de :red[{performance_carteira:.1%}] no período."
else:
    texto_perfomance_carteira = f"A carteira não teve variação no período."


st.write(texto_perfomance_ativos)

st.write(texto_perfomance_carteira)
