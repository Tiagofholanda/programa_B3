import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from ta.trend import MACD
from ta.volatility import BollingerBands
from streamlit_option_menu import option_menu

# Função para calcular médias móveis simples (SMA)
def calcular_sma(data, window=20):
    return data['Close'].rolling(window=window).mean()

# Função para calcular indicadores técnicos (MACD)
def calcular_macd(data):
    indicator_macd = MACD(close=data["Close"], window_slow=26, window_fast=12, window_sign=9)
    return indicator_macd.macd(), indicator_macd.macd_signal()

# Função para calcular bandas de Bollinger
def calcular_bollinger_bands(data):
    indicator_bb = BollingerBands(close=data["Close"], window=20, window_dev=2)
    return indicator_bb.bollinger_hband(), indicator_bb.bollinger_lband()

# Função para determinar a indicação de compra ou venda
def calcular_indicacao_compra_venda(data):
    sma_20 = calcular_sma(data, window=20)
    sma_50 = calcular_sma(data, window=50)
    
    last_close = data['Close'].iloc[-1]
    sma_20_last = sma_20.iloc[-1]
    sma_50_last = sma_50.iloc[-1]
    
    if last_close > sma_20_last and last_close > sma_50_last:
        return "Compra"
    elif last_close < sma_20_last and last_close < sma_50_last:
        return "Venda"
    else:
        return "Manter"

# Configuração da página
st.set_page_config(page_title="Análise da B3", layout="wide")

# Menu de navegação
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Principal",
        options=["Home", "Análise de Ações"],
        icons=["house", "bar-chart"],
        menu_icon="cast",
        default_index=0,
    )

# Página inicial
if selected == "Home":
    st.title("Bem-vindo à Análise da B3")
    st.write("Use o menu à esquerda para navegar entre as opções.")

# Página de análise de ações
if selected == "Análise de Ações":
    st.title("Análise de Ações da B3")

    # Lista estática de tickers das ações da B3
    acoes_b3 = [
        'ABEV3.SA', 'BBAS3.SA', 'BBDC3.SA', 'BBDC4.SA', 'BBSE3.SA', 'BRAP4.SA', 
        'BRFS3.SA', 'BRKM5.SA', 'BRML3.SA', 'BRSR6.SA', 'CCRO3.SA', 'CIEL3.SA', 
        'CMIG4.SA', 'CSAN3.SA', 'CSNA3.SA', 'CYRE3.SA', 'ECOR3.SA', 'EGIE3.SA', 
        'ELET3.SA', 'ELET6.SA', 'EMBR3.SA', 'ENBR3.SA', 'ENEV3.SA', 'ENGI11.SA', 
        'EQTL3.SA', 'EZTC3.SA', 'FLRY3.SA', 'GGBR4.SA', 'GOAU4.SA', 'GOLL4.SA', 
        'HAPV3.SA', 'HYPE3.SA', 'ITSA4.SA', 'ITUB4.SA', 'JBSS3.SA', 'KLBN11.SA', 
        'LAME4.SA', 'LREN3.SA', 'MGLU3.SA', 'MRFG3.SA', 'MRVE3.SA', 'MULT3.SA', 
        'NTCO3.SA', 'PCAR3.SA', 'PETR3.SA', 'PETR4.SA', 'QUAL3.SA', 'RADL3.SA', 
        'RAIL3.SA', 'RENT3.SA', 'SANB11.SA', 'SBSP3.SA', 'SULA11.SA', 'SUZB3.SA', 
        'TAEE11.SA', 'TIMP3.SA', 'UGPA3.SA', 'USIM5.SA', 'VALE3.SA', 'VIVT3.SA', 
        'VVAR3.SA', 'WEGE3.SA', 'YDUQ3.SA'
    ]

    # Entrada do usuário para o ticker da ação
    ticker = st.selectbox("Selecione o ticker da ação:", acoes_b3)

    # Defina o intervalo para obter os dados históricos
    interval = st.selectbox("Selecione o intervalo para os dados históricos:",
                            ["1d", "1wk", "1mo"])

    # Defina o período para obter os dados históricos
    start_date = st.date_input("Data de início", datetime.datetime(2020, 1, 1))
    end_date = st.date_input("Data de fim", datetime.datetime.today())

    # Botão para obter os dados
    if st.button("Consultar"):
        if ticker:
            try:
                # Obtenha os dados históricos da ação
                dados_historicos = yf.download(ticker, start=start_date, end=end_date, interval=interval)

                # Obtenha os dados financeiros da ação
                acao = yf.Ticker(ticker)
                dividends = acao.dividends
                info = acao.info

                # Calcular o Preço Justo de Graham
                vpa = info.get('bookValue', np.nan)
                lpa = info.get('trailingEps', np.nan)
                preco_justo_graham = np.sqrt(22.5 * vpa * lpa)

                # Calcular o Preço Teto Bazin
                dividendo_por_acao = dividends[-1] if not dividends.empty else np.nan
                preco_teto_bazin = dividendo_por_acao / 0.06

                # Exibe os dados históricos
                st.write(f"Dados históricos para {ticker}:")
                st.dataframe(dados_historicos)

                # Exibe gráficos
                st.write("Gráfico de Preço de Fechamento:")
                st.line_chart(dados_historicos['Close'])

                st.write("Gráfico de Volume:")
                st.line_chart(dados_historicos['Volume'])

                # Exibe os cálculos financeiros
                st.write(f"Preço Justo de Graham: R$ {preco_justo_graham:.2f}")
                st.write(f"Preço Teto Bazin: R$ {preco_teto_bazin:.2f}")

                # Calcular indicadores técnicos
                macd, macd_signal = calcular_macd(dados_historicos)
                bollinger_high, bollinger_low = calcular_bollinger_bands(dados_historicos)

                # Plotar indicadores técnicos
                st.write("Indicadores Técnicos:")
                fig, ax = plt.subplots()
                ax.plot(dados_historicos.index, dados_historicos['Close'], label='Preço de Fechamento')
                ax.plot(dados_historicos.index, macd, label='MACD', linestyle='--')
                ax.plot(dados_historicos.index, macd_signal, label='MACD Signal', linestyle='-.')
                ax.fill_between(dados_historicos.index, bollinger_high, bollinger_low, alpha=0.1, color='gray')
                ax.set_title(f"Análise Técnica para {ticker}")
                ax.legend()
                st.pyplot(fig)

                # Exibe a indicação de compra ou venda
                st.write("Indicação de Compra ou Venda:")
                indicacao = calcular_indicacao_compra_venda(dados_historicos)
                st.write(f"Indicação atual: {indicacao}")

            except Exception as e:
                st.error(f"Erro ao obter dados para {ticker}: {e}")
        else:
            st.warning("Por favor, selecione um ticker válido.")
