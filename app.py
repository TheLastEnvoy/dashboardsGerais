import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Função para carregar dados de uma aba específica do Excel
@st.cache
def load_data(sheet_name, file_path):
    return pd.read_excel(file_path, sheet_name=sheet_name)

# Título do dashboard principal
st.title("Dashboard Consolidado")

# Criar abas para diferentes dashboards
tab1, tab2 = st.tabs(["Dashboard de Documentos PGT", "Dashboard de Planilhas"])

# Conteúdo do primeiro dashboard (Documentos PGT)
with tab1:
    st.header("Dashboard de Documentos PGT")
    file_path_pgt = "docsPGTWeb_SO_01nov2024.xlsx"
    df_pgt = load_data(sheet_name='contPGT', file_path=file_path_pgt)

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
    file_path_planilhas = "contPGT_contPlanilhas.xlsx"
    data_planilhas = load_data(sheet_name='contPlanilhas', file_path=file_path_planilhas)

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
