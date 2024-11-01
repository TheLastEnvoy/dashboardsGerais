import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import unicodedata

# Função para carregar dados de uma aba específica do Excel
@st.cache
def load_data(sheet_name):
    return pd.read_excel('contPGT_contPlanilhas.xlsx', sheet_name=sheet_name)

# Título do dashboard principal
st.title("Dashboard Consolidado")

# Criar abas para diferentes dashboards
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard de Documentos PGT",
    "Dashboard de Planilhas",
    "Dashboard de Pareceres",
    "Dashboard de Laudos"
])

# Conteúdo do primeiro dashboard (Documentos PGT)
with tab1:
    st.header("Dashboard de Documentos PGT")
    df_pgt = load_data(sheet_name='contPGT')

    # Preencher valores vazios na coluna "Objetivo" com "Não especificado"
    if 'Objetivo' in df_pgt.columns:
        df_pgt['Objetivo'].fillna('Não especificado', inplace=True)

    # Filtros laterais
    tipos_documento = ['Todos'] + sorted(list(df_pgt['Tipo de documento PGT'].unique()))
    assentamentos = ['Todos'] + sorted(list(df_pgt['Assentamento'].unique()))
    nomes_t1 = ['Todos'] + sorted(list(df_pgt['Nome T1'].unique()))

    # Verificar se a coluna "Objetivo" existe e criar lista de opções
    if 'Objetivo' in df_pgt.columns:
        objetivos = ['Todos'] + sorted(list(df_pgt['Objetivo'].unique()))
    else:
        objetivos = ['Todos']

    selected_tipo_documento = st.sidebar.selectbox("Selecione um tipo de documento:", tipos_documento, key="tipo_documento")
    selected_assentamento = st.sidebar.selectbox("Selecione um assentamento:", assentamentos, key="assentamento")
    selected_nome_t1 = st.sidebar.selectbox("Selecione um nome T1:", nomes_t1, key="nome_t1")
    selected_objetivo = st.sidebar.selectbox("Selecione um objetivo:", objetivos, key="objetivo")

    # Filtrar por tipo de documento
    if selected_tipo_documento != "Todos":
        df_pgt = df_pgt[df_pgt['Tipo de documento PGT'] == selected_tipo_documento]

    # Filtrar por assentamento
    if selected_assentamento != "Todos":
        df_pgt = df_pgt[df_pgt['Assentamento'] == selected_assentamento]

    # Filtrar por nome T1
    if selected_nome_t1 != "Todos":
        df_pgt = df_pgt[df_pgt['Nome T1'] == selected_nome_t1]

    # Filtrar por objetivo, se a coluna existir
    if selected_objetivo != "Todos" and 'Objetivo' in df_pgt.columns:
        df_pgt = df_pgt[df_pgt['Objetivo'] == selected_objetivo]

    # Gráfico de pizza para tipos de documento
    st.subheader("Distribuição por Tipo de Documento")
    tipo_documento_data = df_pgt['Tipo de documento PGT'].value_counts()
    fig_tipo_documento = px.pie(
        names=tipo_documento_data.index,
        values=tipo_documento_data.values,
        title='Distribuição dos Documentos por Tipo'
    )
    st.plotly_chart(fig_tipo_documento)

    # Gráfico de barras para assentamentos
    st.subheader("Distribuição por Assentamento")
    assentamento_data = df_pgt['Assentamento'].value_counts()
    st.bar_chart(assentamento_data)

    # Gráfico de barras para objetivos, se a coluna existir
    if 'Objetivo' in df_pgt.columns:
        st.subheader("Distribuição por Objetivo")
        objetivo_data = df_pgt['Objetivo'].value_counts()
        st.bar_chart(objetivo_data)

    # Exibir tabela interativa
    st.subheader("Relação de Documentos")
    st.write(df_pgt)

    # Exibir quadro com os totais por tipo de documento e assentamento
    total_por_tipo_assentamento = df_pgt.groupby(['Tipo de documento PGT', 'Assentamento']).size().reset_index(name='Quantidade de Documentos')
    st.subheader("Quantidade de documentos por tipo e assentamento")
    st.write(total_por_tipo_assentamento)

    # Adicionar barra de progresso para Solicitação de Documentação Complementar
    st.subheader("Progresso da Solicitação de Documentação Complementar")

    # Calcular o total atual de solicitações
    solicitacoes_atual = df_pgt[df_pgt['Tipo de documento PGT'] == 'Solicitação de documentação complementar'].shape[0]

    # Definir o total a atingir
    total_a_atingir = 674

    # Criar gráfico de barras empilhadas para mostrar o progresso
    fig_progress = go.Figure()

    fig_progress.add_trace(go.Bar(
        name='Concluídos',
        x=['Solicitações'],
        y=[solicitacoes_atual],
        marker_color='green'
    ))

    fig_progress.add_trace(go.Bar(
        name='Faltando',
        x=['Solicitações'],
        y=[max(0, total_a_atingir - solicitacoes_atual)],
        marker_color='lightgrey'
    ))

    fig_progress.update_layout(
        barmode='stack',
        title='Progresso das Solicitações de Documentação Complementar',
        xaxis_title='Status',
        yaxis_title='Número de Documentos',
        yaxis=dict(range=[0, total_a_atingir])  # Define o range do eixo y para sempre mostrar a meta completa
    )

    st.plotly_chart(fig_progress)

# Conteúdo do segundo dashboard (Planilhas)
with tab2:
    st.header("Dashboard de Planilhas")
    data_planilhas = load_data(sheet_name='contPlanilhas')

    # Tabela com total de planilhas e abas
    st.header("Totais")
    total_planilhas = len(data_planilhas)
    total_abas = data_planilhas["Quantidade de Abas"].sum()
    totais_df = pd.DataFrame({
        "Total de Planilhas": [total_planilhas],
        "Total de Abas": [total_abas]
    })
    st.table(totais_df)

    # Mostrar a tabela completa
    st.header("Tabela Completa")
    st.dataframe(data_planilhas)

    # Gráfico de barras
    st.header("Distribuição de Abas por Planilha")
    st.bar_chart(data_planilhas.set_index("Nome da Planilha")["Quantidade de Abas"])

# Conteúdo do terceiro dashboard (Pareceres)
with tab3:
    st.header("Dashboard de Pareceres")
    df_pareceres = load_data(sheet_name='contPareceres')

    # Filtros laterais
    assentamentos = ['Todos'] + sorted(list(df_pareceres['Assentamento'].unique()))
    formatos = ['Todos'] + sorted(list(df_pareceres['Formato'].unique()))
    andamentos = ['Todos'] + sorted(list(df_pareceres['Andamento'].unique()))

    selected_assentamento = st.sidebar.selectbox("Selecione um assentamento:", assentamentos, key="parecer_assentamento")
    selected_formato = st.sidebar.selectbox("Selecione um formato:", formatos, key="parecer_formato")
    selected_andamento = st.sidebar.selectbox("Selecione um andamento:", andamentos, key="parecer_andamento")

    # Filtrar por assentamento
    if selected_assentamento != "Todos":
        df_pareceres = df_pareceres[df_pareceres['Assentamento'] == selected_assentamento]

    # Filtrar por formato
    if selected_formato != "Todos":
        df_pareceres = df_pareceres[df_pareceres['Formato'] == selected_formato]

    # Filtrar por andamento
    if selected_andamento != "Todos":
        df_pareceres = df_pareceres[df_pareceres['Andamento'] == selected_andamento]

    # Calcular o total de pareceres em elaboração e concluídos
    pareceres_em_elaboracao = df_pareceres[df_pareceres['Andamento'] == 'Em elaboração'].shape[0]
    pareceres_concluidos = df_pareceres[df_pareceres['Andamento'] == 'Concluído'].shape[0]

    # Definir o total a atingir
    total_a_atingir = 5861

    # Criar gráfico de barras empilhadas para mostrar o progresso
    fig_progress_pareceres = go.Figure()

    fig_progress_pareceres.add_trace(go.Bar(
        name='Em elaboração',
        x=['Pareceres'],
        y=[pareceres_em_elaboracao],
        marker_color='orange'
    ))

    fig_progress_pareceres.add_trace(go.Bar(
        name='Concluídos',
        x=['Pareceres'],
        y=[pareceres_concluidos],
        marker_color='green'
    ))

    fig_progress_pareceres.add_trace(go.Bar(
        name='Faltando',
        x=['Pareceres'],
        y=[max(0, total_a_atingir - (pareceres_em_elaboracao + pareceres_concluidos))],
        marker_color='lightgrey'
    ))

    # Atualizar layout do gráfico
    fig_progress_pareceres.update_layout(
        barmode='stack',
        title='Progresso dos Pareceres',
        xaxis_title='Status',
        yaxis_title='Quantidade',
        legend_title='Legenda'
    )

    # Exibir gráfico de progresso
    st.plotly_chart(fig_progress_pareceres)

    # Gráfico de pizza para assentamentos
    st.subheader("Gráfico de pizza - Assentamentos")
    assentamento_data = df_pareceres['Assentamento'].value_counts()
    fig_assentamento = px.pie(
        names=assentamento_data.index,
        values=assentamento_data.values,
        title='Distribuição dos Pareceres por Assentamento'
    )
    st.plotly_chart(fig_assentamento)

    # Exibir tabela interativa
    st.subheader("Relação de pareceres")
    st.write(df_pareceres)

    # Exibir gráfico de barras para andamento
    st.subheader("Gráfico de barras - andamento")
    chart_data_andamento = df_pareceres['Andamento'].value_counts()
    st.bar_chart(chart_data_andamento)

    # Calcular o total de pareceres para cada formato e andamento
    total_por_formato_andamento = df_pareceres.groupby(['Formato', 'Andamento']).size().reset_index(name='Quantidade de Pareceres')

    # Exibir quadro com os totais por formato e andamento
    st.subheader("Quantidade de pareceres por formato e andamento")
    st.write(total_por_formato_andamento)

# Conteúdo do quarto dashboard (Laudos)
with tab4:
    st.header("(SO - TED INCRA/UFPR) - Laudos de Supervisão Ocupacional")
    df_laudos = load_data(sheet_name='contLaudos')

    # Função para remover caracteres especiais e normalizar texto
    def remove_special_chars(text):
        return ''.join(ch for ch in unicodedata.normalize('NFKD', text) if not unicodedata.combining(ch))

    # Ordenar opções de pesquisa
    tecnicos = ['Todos'] + sorted(list(df_laudos['Técnico'].unique()))
    assentamentos = ['Todos'] + sorted(list(df_laudos['Assentamento'].unique()))
    tipos_de_laudo = ['Todos'] + sorted(list(df_laudos['Tipo de Laudo'].unique()))
    municipios = ['Todos'] + sorted(list(df_laudos['Município'].apply(remove_special_chars).unique()))
    modalidade = ['Todos'] + sorted(list(df_laudos['Modalidade'].unique()))

    # Data inicial padrão: 01/01/2022
    start_date = datetime(2022, 1, 1).date()

    # Data final padrão: dia atual
    end_date = datetime.now().date()

    # Filtros laterais
    selected_tecnico = st.sidebar.selectbox("Selecione um técnico:", tecnicos, key="tecnico")
    selected_municipio = st.sidebar.selectbox("Selecione um município:", municipios, key="municipio")
    selected_assentamento = st.sidebar.selectbox("Selecione um assentamento:", assentamentos, key="assentamento")
    selected_tipo_laudo = st.sidebar.selectbox("Selecione um tipo de laudo:", tipos_de_laudo, key="tipo_laudo")
    selected_modalidade = st.sidebar.selectbox("Selecione uma modalidade:", modalidade, key="modalidade")

    # Filtrar por técnico
    if selected_tecnico != "Todos":
        df_laudos = df_laudos[df_laudos['Técnico'] == selected_tecnico]

    # Filtrar por município
    if selected_municipio != "Todos":
        df_laudos = df_laudos[df_laudos['Município'].apply(remove_special_chars) == remove_special_chars(selected_municipio)]

    # Filtrar por assentamento
    if selected_assentamento != "Todos":
        df_laudos = df_laudos[df_laudos['Assentamento'] == selected_assentamento]

    # Filtrar por tipo de laudo
    if selected_tipo_laudo != "Todos":
        df_laudos = df_laudos[df_laudos['Tipo de Laudo'] == selected_tipo_laudo]

    # Filtrar por modalidade
    if selected_modalidade != "Todos":
        df_laudos = df_laudos[df_laudos['Modalidade'] == selected_modalidade]

    # Filtrar por data
    start_date = st.sidebar.date_input("Data inicial:", start_date, key="start_date")
    end_date = st.sidebar.date_input("Data final:", end_date, key="end_date")
    df_laudos['Data'] = pd.to_datetime(df_laudos['Data'], format='%d/%m/%Y').dt.date
    df_laudos = df_laudos[(df_laudos['Data'] >= start_date) & (df_laudos['Data'] <= end_date)]

    # Exibir tabela interativa
    st.subheader("Relação de laudos")
    st.write(df_laudos)

    # Exibir gráfico interativo
    st.subheader("Gráfico de barras - tipo de laudo")
    chart_data = df_laudos['Tipo de Laudo'].value_counts()
    st.bar_chart(chart_data)

    # Gráfico de pizza
    st.subheader("Gráfico de pizza - tipo de laudo")
    pie_chart_data = df_laudos['Tipo de Laudo'].value_counts()
    fig = px.pie(names=pie_chart_data.index, values=pie_chart_data.values, title='Distribuição dos Laudos')
    st.plotly_chart(fig)

    # Calcular o total de laudos para cada tipo de laudo
    total_por_tipo_laudo = df_laudos['Tipo de Laudo'].value_counts()

    # Calcular o total de laudos
    total_de_laudos = total_por_tipo_laudo.sum()

    # Adicionar o total de laudos ao DataFrame
    total_por_tipo_laudo = total_por_tipo_laudo.reset_index()
    total_por_tipo_laudo.columns = ['Tipo de Laudo', 'Quantidade de Laudos']
    total_por_tipo_laudo.loc[len(total_por_tipo_laudo)] = ['Total', total_de_laudos]

    # Exibir quadro com os totais
    st.subheader("Quantidade de laudos por tipo")
    st.write(total_por_tipo_laudo)
