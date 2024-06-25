from datetime import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd
import fundamentus
import json
import os


class DataManager(object):
    """
        Class used to treat data
        using the AHP-Gaussiano method
    """
    def __init__(self) -> None:
        self.sectors = self.load_sectors()
        self.df_final = None
        self.df_filtered = None
        self.data_raw = self.data_collect()
        self.df_cleaned = self.data_cleaning(self.data_raw)
        self.df_sectors = self.sectors_definition(self.df_cleaned)
        self.df_filtered = self.data_filtering(self.df_sectors)
        self.df_separated = self.separate_sectors(self.df_filtered)
        self.best_shares = list()
        self.data = {
            "first_serie": None,
            "second_serie": None
        }
        self.first_correlation_matrix = None
        self.second_correlation_matrix = None

    def mock_up(self, action_per_sector: int=1, filtered_sectors: list or None=None) -> None:  # type: ignore
        if not filtered_sectors:
            filtered_sectors = list(self.sectors.keys())
        self.df_final = self.final_table(action_per_sector)
        self.df_final = self.df_final.loc[ self.df_final['setor'].isin(filtered_sectors), : ]
        self.best_shares = list(self.df_final.index)

    def data_collect(self) -> pd.DataFrame:
        return fundamentus.get_resultado_raw()

    def data_cleaning(self, df: pd.DataFrame) -> pd.DataFrame:
        old_cols = ['Cotação', 'P/L', 'P/VP', 'PSR', 'Div.Yield', 'P/Ativo', 'P/Cap.Giro',
        'P/EBIT', 'P/Ativ Circ.Liq', 'EV/EBIT', 'EV/EBITDA', 'Mrg Ebit',
        'Marg_Liquida', 'Liq. Corr.', 'ROIC', 'ROE', 'Liq.2meses', 'Patrim. Líq',
        'Dív.Brut/ Patrim.', 'Cresc. Rec.5a']
        df.columns = [cols.lower() for cols in old_cols]
        return df.reset_index()

    def load_sectors(self) -> dict:
        my_path = os.getcwd().replace('\\', '/')
        file = Path(my_path + f'/libs/storage/sectors.JSON')
        return json.loads(open(file).read())

    def sectors_definition(self, df: pd.DataFrame) -> pd.DataFrame:
        df['setor'] = df['papel'].apply((lambda x: next((setor for setor, codigos in self.sectors.items()
                                    if x in codigos), 'setor_desconhecido')))
        return df


    def data_filtering(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_selected = ['papel', 'setor', 'p/l', 'p/vp', 'div.yield', 
                        'cresc. rec.5a', 'marg_liquida', 'roe']

        df = df.loc[ :, cols_selected]
        df = df.loc[df['setor'] != 'setor_desconhecido']
        df = df.loc[df['p/l'] > 0 , :]
        df = df.loc[df['p/vp'] > 0 , :]
        df = df.loc[df['div.yield'] < 100 , :]
        return df.set_index('papel')

    def separate_sectors(self, df: pd.DataFrame) -> pd.DataFrame:
        sectors_list = list()

        for sector in list(self.sectors.keys()):
            sector = df[df['setor'] == sector].drop('setor', axis=1)
            sectors_list.append(sector)
        return sectors_list

    def ahp_gaussiano(self, df: pd.DataFrame, top_stocks) -> pd.DataFrame:
        df['p/l'] = df['p/l'].apply( lambda x: 1/x )
        df['p/vp'] = df['p/vp'].apply( lambda x: 1/x )

        normalized_sector = ( df[['p/l', 'p/vp', 'div.yield', 'cresc. rec.5a', 'marg_liquida', 'roe']]
                            .apply( lambda x: x/sum(x)) )

        gaussiano_factor = normalized_sector.std() / normalized_sector.mean()
        fator_normalizado = gaussiano_factor / gaussiano_factor.sum()

        normalized_sector['p/l']           = normalized_sector['p/l'] * fator_normalizado['p/l']
        normalized_sector['p/vp']          = normalized_sector['p/vp'] * fator_normalizado['p/vp']
        normalized_sector['div.yield']    = normalized_sector['div.yield'] * fator_normalizado['div.yield']
        normalized_sector['cresc. rec.5a'] = normalized_sector['cresc. rec.5a'] * fator_normalizado['cresc. rec.5a']
        normalized_sector['marg_liquida'] = normalized_sector['marg_liquida'] * fator_normalizado['marg_liquida']
        normalized_sector['roe']          = normalized_sector['roe'] * fator_normalizado['roe']
        normalized_sector['ranking_(%)'] = normalized_sector.sum( axis=1 )*100
        normalized_sector = normalized_sector.sort_values('ranking_(%)', ascending= False).head(top_stocks)

        return normalized_sector

    def final_table(self, top_stocks, table_type: str = 'original') -> pd.DataFrame:
        df_result = pd.DataFrame()
        for setor in self.df_separated:
            df_aux = self.ahp_gaussiano(setor, top_stocks)
            df_result = pd.concat([df_result, df_aux])
        
        if table_type == 'normalizada':
            df_final = pd.merge( df_result, self.df_filtered['setor'], how='left', 
            right_index= True, left_index=True).sort_values('setor')

        else:
            df_final = ( pd.merge( df_result['ranking_(%)'], self.df_filtered, how='left', 
                                    left_index=True, right_index= True ).sort_values( 'setor' ))
            
            df_final = df_final[['p/l', 'p/vp', 'div.yield', 'cresc. rec.5a', 'marg_liquida', 'roe', 'ranking_(%)', 'setor']]
        return df_final

    def extract_live_data(self, start_date: str or None=None, end_date: str or None=None) -> None:  # type: ignore
        if not start_date:
            start_date = "2018-01-01"
        if not end_date:
            end_date = '2022-01-12'
        self.best_shares = [term + '.SA' if not term.endswith(".SA") else term for term in self.best_shares]
        df = yf.download(self.best_shares, start=start_date, end=end_date)
        return df['Adj Close']

    def calculate_correlation(self, df: pd.DataFrame) -> None:
        return df.corr()

    def calculate_daily_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        return prices.pct_change().dropna()

    def calculate_annual_risk(self, daily_returns: pd.DataFrame) -> pd.DataFrame:
        return daily_returns.std() * np.sqrt(252) * 100

    def calculate_annual_returns(self, daily_returns: pd.DataFrame) -> pd.DataFrame:
        return daily_returns.mean() * 252 * 100

    def calculate_return_and_risk(self) -> None:
        daily_returns = self.calculate_daily_returns(self.data["first_serie"])
        annual_returns = self.calculate_annual_returns(daily_returns)
        annual_risk = self.calculate_annual_risk(daily_returns)
        final_data = {
            'Código da Ação Utilizada': tickers,
            'Taxa de Retorno Médio Anual (%)': annual_returns.values,
            'Desvio Padrão Médio Anual (%)': annual_risk.values
        }
        final_df = pd.DataFrame(final_data)




# import pandas as pd
# import numpy as np
# import yfinance as yf
# import streamlit as st


# # Função para calcular retornos diários
# def calculate_daily_returns(prices):
#     returns = prices.pct_change().dropna()
#     return returns

# # Função para calcular retornos anuais
# def calculate_annual_returns(daily_returns):
#     annual_returns = daily_returns.mean() * 252 * 100  # Convertendo para porcentagem
#     return annual_returns

# # Função para calcular o risco anual (desvio padrão anualizado)
# def calculate_annual_risk(daily_returns):
#     annual_risk = daily_returns.std() * np.sqrt(252) * 100  # Convertendo para porcentagem
#     return annual_risk

# # Definir parâmetros
# tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'ABEV3.SA', 'BBDC4.SA', 
#            'BBAS3.SA', 'WEGE3.SA', 'BPAC11.SA', 'SANB11.SA', 'ITSA4.SA']
# start_date = '2018-01-01'
# end_date = '2022-12-31'

# # Obter dados históricos
# prices = get_historical_data(tickers, start=start_date, end=end_date)

# # Calcular retornos diários
# daily_returns = calculate_daily_returns(prices)

# # Calcular retornos anuais
# annual_returns = calculate_annual_returns(daily_returns)

# # Calcular risco anual
# annual_risk = calculate_annual_risk(daily_returns)

# # Criar DataFrame final
# data = {
#     'Código da Ação Utilizada': tickers,
#     'Empresa': ['PETROBRAS', 'VALE', 'ITAÚ UNIBANCO', 'AMBEV S/A', 'BRADESCO', 
#                 'BANCO DO BRASIL', 'WEG', 'BTGP BANCO', 'SANTANDER BRASIL', 'ITAÚSA'],
#     'Taxa de Retorno Médio Anual (%)': annual_returns.values,
#     'Desvio Padrão Médio Anual (%)': annual_risk.values
# }
# final_df = pd.DataFrame(data)

# # Interface do Streamlit
# st.title('Retorno e Risco Médios Anuais das Ações (2018 - 2022)')

# st.write(final_df)

# # Exibir tabela final
# st.table(final_df)
