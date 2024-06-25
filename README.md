# Organização e estrutura do projeto
	Separação das dependências
		- Classe DataManager
		- Classe STManager
		- Classe HillClimb

- Classe DataManager
Classe responsável por vizualização dos dados, utilizando de um objeto único da classe externa streamlit.

- Classe STManager
Classe responsável pelo geração, e tratamento dos dados organizando-os por segmento, filtrando os dados por meio de cálculos financeiros específicos, e aplicando o método AHP-Haussiano, e por fim disponibilizando tabelas de dados que serão consumidas pela classe STManager.

- Classe HillClimb
Classe responsável por gerar a otimização da carteira, após a seleção dos dados pela classe DataManager, realizar o download das informações financeiras por meio da API Yahoo Finance, e aplicar o método Hill-Climbing para determinar as melhores empresas e segmentos para diluir os investimentos e potencializar ao máximo os lucros.


Pontos a serem desenvolvidos:

- Adição de um método para download dos dados financeiros de uma holding específica na classe HillClimb.
- Conexão da classe HillClimb com a visualização na classe STManager.
- Adição de um botão na classe STManager para realizar o input de uma data de ínicio a ser analisada no cálculo.
- Adição de um gráfico pizza para apresentação das porcentagens aplicadas em cada holding após a metodologia Hill-Climb.
- Possibilitar que as escolhas aplicadas ao DataManager seja espelhadas na classe HillClimb.
- Adição de um botão de download do XLSX final de cada uma das tabelas.

A execução do projeto é feito pelo arquivo main.py por meio do seguinte comando:
streamlit run main.py

É possível executar a classe HillClimb para teste, até que a mesma seja conectada com a parte gráfica.
É necessário entrar no caminho libs/ e executar o comando python hill_climb_class.py. Essa execução direta da classe será removida assim que se tornar um componente da Classe STManager.
