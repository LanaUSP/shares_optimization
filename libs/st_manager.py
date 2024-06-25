from libs.data_manager import DataManager
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date
import streamlit as st
import seaborn as sns



st.set_page_config(page_title= 'Carteira de Ações', layout = 'wide')
@st.cache(allow_output_mutation=True)


class STmanager(object):
    """
        Class used to manipulate
        the Streamlit object
    """
    def __init__(self):
        self.st = st
        self.data = DataManager()

    def button(self) -> bool:
        actions = {'Habilitar Todos': True, 'Desabilitar Todos': bool()}
        button = self.st.sidebar.radio('Habilitar / Desabilitar Seleção', (list(actions.keys())))
        return actions[button]

    def create_checkbox(self, button: bool) -> list:
        temp_list = list()
        for sector in list(self.data.sectors.keys()):
            option = self.st.sidebar.checkbox(sector, value=button)
            if option: 
                temp_list.append(sector)
        return temp_list

    def generate_graphic(self, title: str, filter: str, ascending: bool=bool(), index: str='papel') -> None:
        self.st.markdown(title)
        values = self.data.df_final.sort_values(filter, ascending=ascending).reset_index().rename(columns= {'index': index}).head(10)
        fig = px.bar(values, x='papel', y=filter)
        self.st.plotly_chart(fig, use_container_width= True)

    def run(self) -> None:
        self.st.sidebar.markdown( '# Selecione os Filtros' )
        self.st.sidebar.markdown( '## ' )
        self.filtro_top_stocks = self.st.sidebar.selectbox( 'Quantidade de ações por setor:', (1,2,3))
        self.st.sidebar.markdown( '''___''' )
        self.button_selected = self.button()
        self.st.sidebar.markdown( '## Selecione os setores: ')
        self.selecting_sectors = self.create_checkbox(self.button_selected)
        self.st.markdown( '## Sugestão de Carteira de Ações')
        self.data.mock_up(self.filtro_top_stocks, self.selecting_sectors)
        self.st.dataframe(self.data.df_final, use_container_width=True)
        self.st.markdown( '''___''')
        self.st.markdown( '## Gráficos dos indicadores')
        with self.st.container():
            col1, col2 = self.st.columns(2)
            with col1:
                self.generate_graphic('##### Top 10 menores P/L (Preço / Lucro)', 'p/l', True)
                self.generate_graphic('##### Top 10 maiores Dividendos', 'div.yield')
                self.generate_graphic('##### Top 10 maiores Margem Líquida', 'marg_liquida')
                self.st.markdown( '## Primeira série de dados')
                self.first_range_from = self.st.date_input("1º De:", value=date(2018, 1, 1))
                self.first_range_to = self.st.date_input("1º Até:", value=date(2020, 12, 31))
            with col2:
                self.generate_graphic('##### Top 10 menores P/VP (Preço / Valor Patrimonial)', 'p/vp', True)
                self.generate_graphic('##### Top 10 maiores Crescimento de Receita', 'cresc. rec.5a')
                self.generate_graphic('##### Top 10 maiores Roe ( Retorno sobre o Investimento)', 'roe', bool(), 'empresa')
                self.st.markdown( '## Segunda série de dados')
                self.second_range_from = self.st.date_input("2º De:", value=date(2023, 1, 1))
                self.second_range_to = self.st.date_input("2º Até:", value=date(2023, 12, 31))
        self.st.markdown( '## Matriz de Correlação')
        self.data.data["first_serie"] = self.data.extract_live_data(str(self.first_range_from), str(self.first_range_to))
        self.data.data["second_serie"] = self.data.extract_live_data(str(self.second_range_from), str(self.second_range_to))
        self.data.first_correlation_matrix = self.data.calculate_correlation(self.data.data["first_serie"])
        self.data.second_correlation_matrix = self.data.calculate_correlation(self.data.data["second_serie"])
        with self.st.container():
            col1, col2 = self.st.columns(2)
            with col1:
                st.dataframe(self.data.first_correlation_matrix)
                st.dataframe(self.data.second_correlation_matrix)
            with col2:
                fig, ax = plt.subplots(figsize=(20, 16))
                sns.heatmap(self.data.first_correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
                self.st.pyplot(fig)
                fig, ax = plt.subplots(figsize=(20, 16))
                sns.heatmap(self.data.second_correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
                self.st.pyplot(fig)
