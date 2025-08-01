import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import re
from collections import Counter
import itertools
import warnings
warnings.filterwarnings('ignore')

# URLs das diferentes abas (removido URL_DATABASE não utilizada)
URL_DADOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRnTrJ0DW6_N99xSBTTMrRza3YuRkkzRmB1OuIX28JDBRdsmF1XAginDVCHNbWZGMomjf4B28AZlHHq/pub?gid=0&single=true&output=csv"
URL_RESIDUOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRnTrJ0DW6_N99xSBTTMrRza3YuRkkzRmB1OuIX28JDBRdsmF1XAginDVCHNbWZGMomjf4B28AZlHHq/pub?gid=1882708214&single=true&output=csv"
URL_TECNOLOGIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRnTrJ0DW6_N99xSBTTMrRza3YuRkkzRmB1XAginDVCHNbWZGMomjf4B28AZlHHq/pub?gid=745302211&single=true&output=csv"

# Configuração da página com tema profissional
st.set_page_config(
    page_title="Dashboard PRISMA - Geotecnologias e Bioenergia",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado com design moderno e profissional
st.markdown("""
<style>
    /* Reset e configurações gerais */
    .main {
        padding: 0rem 1rem;
        background-color: #fafafa;
    }
    
    /* Tipografia e hierarquia */
    h1 {
        color: #1a3a52;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #2d5016;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #3d602d;
        font-weight: 500;
    }
    
    /* Cards e containers */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    /* Métricas customizadas */
    [data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    /* Tabs estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent;
        padding-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 0 2rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f7ff;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2d5016 !important;
        color: white !important;
    }
    
    /* Botões customizados */
    .stDownloadButton > button {
        background-color: #2d5016;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background-color: #3d602d;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(45, 80, 22, 0.3);
    }
    
    /* Sidebar estilizada */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Expander customizado */
    .streamlit-expanderHeader {
        background-color: #f0f7ff;
        border-radius: 8px;
        padding: 0.5rem;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        border-radius: 4px;
    }
    
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        border-radius: 4px;
    }
    
    /* Animações suaves */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        [data-testid="metric-container"] {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Funções de processamento aprimoradas
@st.cache_data
def split_multiple_values(text, separators=[',', ';', '/', '|', ' e ', ' and ', ' & ']):
    """
    Separa múltiplos valores em uma célula baseado em diferentes separadores
    """
    if pd.isna(text) or text == '':
        return []
    
    text = str(text).strip()
    pattern = '|'.join(map(re.escape, separators))
    values = re.split(pattern, text)
    values = [v.strip() for v in values if v.strip()]
    
    return values

@st.cache_data
def process_technologies(tech_text):
    """
    Processa e padroniza tecnologias múltiplas
    """
    if pd.isna(tech_text) or tech_text == '':
        return ['Não especificado']
    
    tech_standardization = {
        'biodigestão': 'Biodigestão Anaeróbia',
        'biogas': 'Biodigestão Anaeróbia',
        'biogás': 'Biodigestão Anaeróbia',
        'anaerobic': 'Biodigestão Anaeróbia',
        'digestão anaeróbia': 'Biodigestão Anaeróbia',
        'ad': 'Biodigestão Anaeróbia',
        'pirólise': 'Pirólise',
        'pyrolysis': 'Pirólise',
        'gaseificação': 'Gaseificação',
        'gasification': 'Gaseificação',
        'fermentação': 'Fermentação',
        'fermentation': 'Fermentação',
        'etanol': 'Fermentação Alcoólica',
        'ethanol': 'Fermentação Alcoólica',
        'combustão': 'Combustão Direta',
        'combustion': 'Combustão Direta',
        'incineração': 'Combustão Direta',
        'transesterificação': 'Transesterificação',
        'biodiesel': 'Transesterificação',
        'compostagem': 'Compostagem',
        'composting': 'Compostagem',
        'htl': 'Liquefação Hidrotérmica',
        'hydrothermal': 'Liquefação Hidrotérmica',
        'torrefação': 'Torrefação',
        'torrefaction': 'Torrefação',
        'briquetagem': 'Briquetagem',
        'pelletização': 'Pelletização',
        'codigestão': 'Co-digestão',
        'co-digestion': 'Co-digestão'
    }
    
    technologies = split_multiple_values(tech_text)
    standardized = []
    
    for tech in technologies:
        tech_lower = tech.lower().strip()
        matched = False
        
        for key, value in tech_standardization.items():
            if key in tech_lower:
                standardized.append(value)
                matched = True
                break
        
        if not matched and tech.strip():
            standardized.append(tech.strip().title())
    
    return standardized if standardized else ['Não especificado']

@st.cache_data
def process_waste_types(waste_text):
    """
    Processa e padroniza tipos de resíduos múltiplos
    """
    if pd.isna(waste_text) or waste_text == '':
        return ['Não especificado']
    
    waste_standardization = {
        'agrícola': 'Resíduo Agrícola',
        'agricultural': 'Resíduo Agrícola',
        'crop': 'Resíduo Agrícola',
        'palha': 'Resíduo Agrícola',
        'bagaço': 'Resíduo Agrícola',
        'casca': 'Resíduo Agrícola',
        'pecuária': 'Resíduo Pecuário',
        'animal': 'Resíduo Pecuário',
        'livestock': 'Resíduo Pecuário',
        'esterco': 'Resíduo Pecuário',
        'dejeto': 'Resíduo Pecuário',
        'suíno': 'Resíduo Pecuário',
        'bovino': 'Resíduo Pecuário',
        'urbano': 'Resíduo Urbano',
        'urban': 'Resíduo Urbano',
        'municipal': 'Resíduo Urbano',
        'rsu': 'Resíduo Urbano',
        'lixo': 'Resíduo Urbano',
        'industrial': 'Resíduo Industrial',
        'indústria': 'Resíduo Industrial',
        'factory': 'Resíduo Industrial',
        'florestal': 'Resíduo Florestal',
        'forest': 'Resíduo Florestal',
        'madeira': 'Resíduo Florestal',
        'wood': 'Resíduo Florestal',
        'alimentar': 'Resíduo Alimentar',
        'food': 'Resíduo Alimentar',
        'alimento': 'Resíduo Alimentar',
        'orgânico': 'Resíduo Orgânico',
        'organic': 'Resíduo Orgânico'
    }
    
    wastes = split_multiple_values(waste_text)
    standardized = []
    
    for waste in wastes:
        waste_lower = waste.lower().strip()
        matched = False
        
        for key, value in waste_standardization.items():
            if key in waste_lower:
                if value not in standardized:
                    standardized.append(value)
                matched = True
                break
        
        if not matched and waste.strip():
            standardized.append(waste.strip().title())
    
    return standardized if standardized else ['Não especificado']

@st.cache_data
def process_methodologies(method_text):
    """
    Processa e padroniza metodologias múltiplas
    """
    if pd.isna(method_text) or method_text == '':
        return ['Não especificado']
    
    method_standardization = {
        'gis': 'GIS/SIG',
        'sig': 'GIS/SIG',
        'geographic information': 'GIS/SIG',
        'arcgis': 'GIS/SIG',
        'qgis': 'GIS/SIG',
        'sensoriamento': 'Sensoriamento Remoto',
        'remote sensing': 'Sensoriamento Remoto',
        'satellite': 'Sensoriamento Remoto',
        'satélite': 'Sensoriamento Remoto',
        'landsat': 'Sensoriamento Remoto',
        'sentinel': 'Sensoriamento Remoto',
        'mcda': 'MCDA/MCDM',
        'mcdm': 'MCDA/MCDM',
        'multicritério': 'MCDA/MCDM',
        'multicriteria': 'MCDA/MCDM',
        'ahp': 'AHP',
        'analytic hierarchy': 'AHP',
        'fuzzy': 'Lógica Fuzzy',
        'difuso': 'Lógica Fuzzy',
        'otimização': 'Otimização',
        'optimization': 'Otimização',
        'p-mediana': 'P-Mediana',
        'p-median': 'P-Mediana',
        'localização': 'Localização-Alocação',
        'location': 'Localização-Alocação',
        'allocation': 'Localização-Alocação',
        'machine learning': 'Machine Learning',
        'aprendizado de máquina': 'Machine Learning',
        'ml': 'Machine Learning',
        'neural': 'Redes Neurais',
        'deep learning': 'Deep Learning',
        'lca': 'LCA/ACV',
        'life cycle': 'LCA/ACV',
        'ciclo de vida': 'LCA/ACV',
        'modelagem': 'Modelagem',
        'modeling': 'Modelagem',
        'simulação': 'Simulação',
        'simulation': 'Simulação'
    }
    
    methods = split_multiple_values(method_text)
    standardized = []
    
    for method in methods:
        method_lower = method.lower().strip()
        matched = False
        
        for key, value in method_standardization.items():
            if key in method_lower:
                if value not in standardized:
                    standardized.append(value)
                matched = True
        
        if not matched and method.strip() and len(method.strip()) > 2:
            standardized.append(method.strip())
    
    return standardized if standardized else ['Não especificado']

@st.cache_data
def expand_dataframe(df):
    """
    Expande o dataframe para ter uma linha por combinação de tecnologia/resíduo/metodologia
    """
    expanded_rows = []
    
    for idx, row in df.iterrows():
        technologies = process_technologies(row.get('TECNOLOGIA', ''))
        waste_types = process_waste_types(row.get('TIPO_RESIDUO', ''))
        methodologies = process_methodologies(row.get('METODOLOGIA', ''))
        
        for tech in technologies:
            for waste in waste_types:
                for method in methodologies:
                    new_row = row.copy()
                    new_row['Tecnologia_Processada'] = tech
                    new_row['Tipo_Residuo_Processado'] = waste
                    new_row['Metodologia_Processada'] = method
                    new_row['_original_index'] = idx
                    expanded_rows.append(new_row)
    
    return pd.DataFrame(expanded_rows)

@st.cache_data
def analyze_combinations(df):
    """
    Analisa as combinações mais comuns de tecnologia + resíduo
    """
    combinations = []
    
    for idx, row in df.iterrows():
        techs = process_technologies(row.get('TECNOLOGIA', ''))
        wastes = process_waste_types(row.get('TIPO_RESIDUO', ''))
        
        for tech, waste in itertools.product(techs, wastes):
            if tech != 'Não especificado' and waste != 'Não especificado':
                combinations.append(f"{tech} + {waste}")
    
    return Counter(combinations)

@st.cache_data
def load_data(file):
    """
    Carrega dados com tratamento de erros aprimorado
    """
    try:
        df = pd.read_csv(file, encoding='utf-8')
        return df
    except:
        try:
            df = pd.read_csv(file, encoding='latin-1')
            return df
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo: {str(e)}")
            return None

@st.cache_data
def load_geo_data():
    """Carrega dados geoespaciais das diferentes abas com fallback strategy"""
    try:
        # Primeira tentativa: carregar dados separados
        df_residuos = pd.read_csv(URL_RESIDUOS)
        df_tecnologias = pd.read_csv(URL_TECNOLOGIAS)
        df_dados = pd.read_csv(URL_DADOS)
        return df_residuos, df_tecnologias, df_dados
    except Exception as e:
        # Fallback silencioso: usar apenas a aba principal que contém todos os dados
        try:
            df_dados = pd.read_csv(URL_DADOS)
            # A aba principal já contém as informações de tecnologia e resíduos
            return df_dados, df_dados, df_dados
        except Exception as e2:
            st.error(f"Erro crítico ao carregar dados: {str(e2)}")
            return None, None, None

@st.cache_data
def padronizar_paises(pais):
    """Padroniza nomes de países para compatibilidade com Plotly"""
    mapeamento = {
        # Seus países → Nomes reconhecidos pelo Plotly
        'EUA': 'United States',
        'USA': 'United States',
        'Estados Unidos': 'United States',
        'Reino Unido': 'United Kingdom',
        'UK': 'United Kingdom',
        'Coreia do Sul': 'South Korea',
        'Holanda': 'Netherlands',
        'Alemanha': 'Germany',
        'França': 'France',
        'Espanha': 'Spain',
        'Itália': 'Italy',
        'China': 'China',
        'Brasil': 'Brazil',
        'Canadá': 'Canada',
        'Canada': 'Canada',
        'Austrália': 'Australia',
        'Australia': 'Australia',
        'Japão': 'Japan',
        'India': 'India',
        'Índia': 'India',
        'Turquia': 'Turkey',
        'México': 'Mexico',
        'Iran': 'Iran',
        'Irã': 'Iran',
        'Suécia': 'Sweden',
        'Noruega': 'Norway',
        'Dinamarca': 'Denmark',
        'Finlândia': 'Finland',
        'Bélgica': 'Belgium',
        'Suíça': 'Switzerland',
        'Áustria': 'Austria',
        'Polônia': 'Poland',
        'República Tcheca': 'Czech Republic',
        'Grécia': 'Greece',
        'Portugal': 'Portugal',
        'Tailândia': 'Thailand',
        'Malásia': 'Malaysia',
        'Singapura': 'Singapore',
        'Filipinas': 'Philippines',
        'Indonésia': 'Indonesia',
        'África do Sul': 'South Africa',
        'Egito': 'Egypt',
        'Marrocos': 'Morocco',
        'Israel': 'Israel',
        'Arábia Saudita': 'Saudi Arabia',
        'Emirados Árabes Unidos': 'United Arab Emirates',
        'Argentina': 'Argentina',
        'Chile': 'Chile',
        'Colômbia': 'Colombia',
        'Peru': 'Peru',
        'Equador': 'Ecuador',
        'Venezuela': 'Venezuela',
        'Uruguai': 'Uruguay',
        'Paraguai': 'Paraguay',
        'Bolívia': 'Bolivia',
        'Rússia': 'Russia',
        'Ucrânia': 'Ukraine',
        'Cazaquistão': 'Kazakhstan',
        'Nova Zelândia': 'New Zealand'
    }
    
    return mapeamento.get(pais, pais)

@st.cache_data
def process_country(pais_regiao):
    """
    Processa e padroniza países
    """
    if pd.isna(pais_regiao) or pais_regiao == '':
        return 'Não especificado'
    
    texto = str(pais_regiao).lower()
    
    country_mapping = {
        'brasil': 'Brasil',
        'brazil': 'Brasil',
        'estados unidos': 'Estados Unidos',
        'usa': 'Estados Unidos',
        'united states': 'Estados Unidos',
        'alemanha': 'Alemanha',
        'germany': 'Alemanha',
        'china': 'China',
        'itália': 'Itália',
        'italia': 'Itália',
        'italy': 'Itália',
        'frança': 'França',
        'france': 'França',
        'espanha': 'Espanha',
        'spain': 'Espanha',
        'reino unido': 'Reino Unido',
        'uk': 'Reino Unido',
        'canadá': 'Canadá',
        'canada': 'Canadá',
        'austrália': 'Austrália',
        'australia': 'Austrália',
        'índia': 'Índia',
        'india': 'Índia',
        'japão': 'Japão',
        'japan': 'Japão'
    }
    
    for key, value in country_mapping.items():
        if key in texto:
            return value
    
    return 'Outros'

# Configuração de cores temáticas
COLOR_PALETTE = {
    'primary': '#2d5016',
    'secondary': '#3d602d',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#3B82F6',
    'light': '#F3F4F6',
    'dark': '#1F2937'
}

# Título principal com design moderno
col_title, col_logo = st.columns([5, 1])
with col_title:
    st.markdown("""
    <h1 style='margin-bottom: 0;'>🌱 Dashboard Analítico PRISMA</h1>
    <p style='font-size: 1.2rem; color: #666; margin-top: 0;'>
        Geotecnologias e Bioenergia - Análise Avançada com Separação Automática de Valores
    </p>
    """, unsafe_allow_html=True)

# CSS para botões de navegação elegantes
st.markdown("""
<style>
/* Estilo para botões de navegação */
.stButton > button {
    width: 100%;
    height: 50px;
    background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
    color: #2d5016;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s ease;
    margin-bottom: 8px;
    text-align: left;
    padding-left: 16px;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #2d5016 0%, #3d602d 100%);
    color: white;
    border-color: #2d5016;
    transform: translateX(5px);
    box-shadow: 0 2px 8px rgba(45, 80, 22, 0.3);
}

.stButton > button:active {
    background: linear-gradient(90deg, #1e3a0f 0%, #2d5016 100%);
    transform: translateX(2px);
}

/* Estilo para botão ativo (com ▶️) */
.stButton > button[title*="▶️"] {
    background: linear-gradient(90deg, #2d5016 0%, #3d602d 100%);
    color: white;
    border-color: #2d5016;
    box-shadow: 0 2px 8px rgba(45, 80, 22, 0.4);
}

/* Container da sidebar */
.css-1d391kg {
    background-color: #f8f9fa;
}
</style>
    """, unsafe_allow_html=True)

# Sidebar com design aprimorado
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #2d5016 0%, #3d602d 100%); 
                color: white; border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; margin: 0;'>⚙️ Configurações</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Dados carregados automaticamente do Google Sheets
    st.markdown("""
    <div style='background: #e8f5e9; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
        <p style='margin: 0; font-weight: 500;'>☁️ Dados do Google Sheets</p>
        <small style='color: #666;'>Carregamento automático ativo</small>
    </div>
    """, unsafe_allow_html=True)
    
    # uploaded_file = st.file_uploader(
    #     "Selecione o arquivo CSV",
    #     type=['csv'],
    #     help="Faça upload do arquivo com os dados da revisão sistemática"
    # )
    
    st.markdown("---")
    
    # Opções de processamento com visual aprimorado
    st.markdown("### 🔄 Modo de Processamento")
    
    process_option = st.radio(
        "Como processar valores múltiplos?",
        ["Expandir dados (análise detalhada)", 
         "Manter original (análise agregada)"],
        help="Expandir cria múltiplas linhas para análise mais granular"
    )
    
    st.markdown("---")
    
    # ========== NAVEGAÇÃO COM BOTÕES ==========
    st.markdown("### 🧭 Navegação Principal")

    # Lista de seções com ícones e nomes
    sections = [
        ("📊", "Visão Geral", "📊 Visão Geral"),
        ("🔬", "Tecnologias", "🔬 Tecnologias"),
        ("♻️", "Resíduos", "♻️ Resíduos"),
        ("🔄", "Combinações", "🔄 Combinações"),
        ("📐", "Metodologias", "📐 Metodologias"),
        ("🎯", "Variáveis", "🎯 Variáveis Especiais"),
        ("📑", "Dados", "📑 Dados"),
        ("🗺️", "Mapas", "🗺️ Análise Geoespacial")
    ]
    
    # Inicializar session_state se não existir
    if 'current_section' not in st.session_state:
        st.session_state['current_section'] = "📊 Visão Geral"
    
    # Botões organizados em lista vertical
    for icon, name, section_key in sections:
        # Verificar se esta é a seção ativa
        is_active = st.session_state.get('current_section') == section_key
        button_text = f"{'▶️ ' if is_active else ''}{icon} {name}"
        
        if st.button(button_text, key=f"btn_{name.lower().replace(' ', '_')}", use_container_width=True):
            st.session_state['current_section'] = section_key
    
    # Usar a seção armazenada no session_state
    section_selected = st.session_state['current_section']
    
    # Seção ativa
    st.markdown(f"**Seção Ativa:** {section_selected}")
    
    st.markdown("---")
    
    # Informações do projeto com cards
    st.markdown("### 📊 Recursos do Dashboard")
    
    features = [
        ("🔍", "Separação automática de valores"),
        ("🎯", "Padronização inteligente"),
        ("📈", "Análise de combinações"),
        ("🗺️", "Visualizações interativas")
    ]
    
    for icon, feature in features:
        st.markdown(f"""
        <div style='background: white; padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;
                    border-left: 3px solid #2d5016;'>
            <span style='font-size: 1.2rem;'>{icon}</span> <strong>{feature}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Informações do projeto
    st.markdown("---")
    with st.expander("ℹ️ Sobre o Projeto"):
        st.markdown("""
        **Centro Paulista de Estudos em Biogás e Bioprodutos (CP2B)**
        
        Este dashboard foi desenvolvido para apoiar a revisão sistemática PRISMA 
        sobre geotecnologias aplicadas à bioenergia.
        
        **Orientador:** Prof. Rubens Lamparelli
        """)
    
    # Adicione esta opção no sidebar
    st.markdown("---")
    if st.button("🧪 Testar Dados Geo"):
        st.write("Testando carregamento...")
        df_residuos, df_tecnologias, df_dados = load_geo_data()
        
        if df_residuos is not None:
            st.success(f"✅ Resíduos: {df_residuos.shape[0]} linhas, {df_residuos.shape[1]} colunas")
        if df_tecnologias is not None:
            st.success(f"✅ Tecnologias: {df_tecnologias.shape[0]} linhas, {df_tecnologias.shape[1]} colunas")
        if df_dados is not None:
            st.success(f"✅ Dados: {df_dados.shape[0]} linhas, {df_dados.shape[1]} colunas")

# Carregar dados automaticamente do Google Sheets
with st.spinner('Carregando dados do Google Sheets...'):
    df_residuos, df_tecnologias, df_original = load_geo_data()

if df_original is not None:
    # Processar país
    df_original['País_Processado'] = df_original['PAIS'].apply(process_country)
    
    # Decidir se expande ou não
    if process_option == "Expandir dados (análise detalhada)":
        df = expand_dataframe(df_original)
        st.info(f"📊 Dados expandidos: {len(df_original)} artigos → {len(df)} linhas de análise")
    else:
        df = df_original.copy()
        df['Tecnologias_Lista'] = df['TECNOLOGIA'].apply(process_technologies)
        df['Residuos_Lista'] = df['TIPO_RESIDUO'].apply(process_waste_types)
        df['Metodologias_Lista'] = df['METODOLOGIA'].apply(process_methodologies)
    
    # Preparação de dados para todas as seções
    # Coletar estatísticas globais
    all_techs = []
    for techs in df_original['TECNOLOGIA'].apply(process_technologies):
        all_techs.extend(techs)
    
    all_wastes = []
    for wastes in df_original['TIPO_RESIDUO'].apply(process_waste_types):
        all_wastes.extend(wastes)
    
    all_methods = []
    for methods in df_original['METODOLOGIA'].apply(process_methodologies):
        all_methods.extend(methods)
    
    # Dados por ano
    df_original['Ano'] = pd.to_numeric(df_original['ANO'], errors='coerce')
    df_year = df_original[df_original['Ano'].notna()]
    
    # Sistema de navegação baseado na seleção do sidebar
    if section_selected == "📊 Visão Geral":
        st.markdown("## 📊 Visão Geral do Projeto")
        
        # Métricas principais em cards
        col1, col2, col3, col4 = st.columns(4)
        
        total_artigos = len(df_original)
        # Status_Final não existe mais nos dados atuais
        incluidos = total_artigos  # Assumindo que todos os dados são incluídos
        excluidos = 0
        pendentes = 0
        
        with col1:
            st.metric(
                "📚 Total de Artigos", 
                f"{total_artigos:,}",
                help="Total de artigos analisados"
            )
        
        with col2:
            st.metric(
                "✅ Incluídos", 
                f"{incluidos:,}",
                f"{(incluidos/total_artigos*100):.1f}%",
                help="Artigos que atendem aos critérios"
            )
        
        with col3:
            st.metric(
                "❌ Excluídos", 
                f"{excluidos:,}",
                f"{(excluidos/total_artigos*100):.1f}%",
                help="Artigos que não atendem aos critérios"
            )
        
        with col4:
            st.metric(
                "⏳ Pendentes", 
                f"{pendentes:,}",
                f"{(pendentes/total_artigos*100):.1f}%",
                help="Artigos aguardando análise"
            )
        
        st.markdown("---")
        
        # Análise de valores múltiplos
        st.markdown("### 📊 Análise de Campos com Valores Múltiplos")
        
        # Coletar estatísticas
        unique_techs = len(set(all_techs)) - (1 if 'Não especificado' in all_techs else 0)
        unique_wastes = len(set(all_wastes)) - (1 if 'Não especificado' in all_wastes else 0)
        unique_methods = len(set(all_methods)) - (1 if 'Não especificado' in all_methods else 0)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class='metric-card'>
                <h3 style='color: #2d5016; margin-bottom: 0.5rem;'>🔬 Tecnologias Únicas</h3>
                    <h2 style='margin: 0; color: #1a3a52;'>{}</h2>
                    <p style='color: #666; margin-top: 0.5rem;'>Média por artigo: {:.1f}</p>
                </div>
                """.format(
                    unique_techs,
                    np.mean([len(techs) for techs in df_original['TECNOLOGIA'].apply(process_technologies)])
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='metric-card'>
                    <h3 style='color: #2d5016; margin-bottom: 0.5rem;'>♻️ Tipos de Resíduos</h3>
                    <h2 style='margin: 0; color: #1a3a52;'>{}</h2>
                    <p style='color: #666; margin-top: 0.5rem;'>Média por artigo: {:.1f}</p>
                </div>
                """.format(
                    unique_wastes,
                    np.mean([len(wastes) for wastes in df_original['TIPO_RESIDUO'].apply(process_waste_types)])
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class='metric-card'>
                    <h3 style='color: #2d5016; margin-bottom: 0.5rem;'>📐 Metodologias</h3>
                    <h2 style='margin: 0; color: #1a3a52;'>{}</h2>
                    <p style='color: #666; margin-top: 0.5rem;'>Média por artigo: {:.1f}</p>
                </div>
                """.format(
                    unique_methods,
                    np.mean([len(methods) for methods in df_original['METODOLOGIA'].apply(process_methodologies)])
                ), unsafe_allow_html=True)
            
            # Gráfico de distribuição com design aprimorado
            st.markdown("### 📈 Distribuição de Valores por Campo")
            
            multi_value_data = []
            for idx, row in df_original.iterrows():
                n_techs = len(process_technologies(row.get('TECNOLOGIA', '')))
                n_wastes = len(process_waste_types(row.get('TIPO_RESIDUO', '')))
                n_methods = len(process_methodologies(row.get('METODOLOGIA', '')))
                
                multi_value_data.extend([
                    {'Tipo': 'Tecnologias', 'Quantidade': n_techs},
                    {'Tipo': 'Resíduos', 'Quantidade': n_wastes},
                    {'Tipo': 'Metodologias', 'Quantidade': n_methods}
                ])
            
            df_multi = pd.DataFrame(multi_value_data)
            
            fig_violin = px.violin(
                df_multi, 
                x='Tipo', 
                y='Quantidade',
                color='Tipo',
                title="",
                box=True,
                color_discrete_map={
                    'Tecnologias': COLOR_PALETTE['primary'],
                    'Resíduos': COLOR_PALETTE['success'],
                    'Metodologias': COLOR_PALETTE['info']
                }
            )
            
            fig_violin.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig_violin, use_container_width=True)
            
            # Timeline de publicações
            st.markdown("### 📅 Evolução Temporal das Publicações")
            
            if len(df_year) > 0:
                year_counts = df_year.groupby('Ano').size().reset_index(name='Quantidade')
                
                fig_timeline = px.area(
                    year_counts,
                    x='Ano',
                    y='Quantidade',
                    title="",
                    line_shape='spline',
                    color_discrete_sequence=[COLOR_PALETTE['primary']]
                )
                
                fig_timeline.update_traces(
                    fill='tozeroy',
                    fillcolor='rgba(45, 80, 22, 0.2)',
                    line=dict(color=COLOR_PALETTE['primary'], width=3)
                )
                
                fig_timeline.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Ano'),
                    yaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Número de Publicações'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
    
    # TAB 2: TECNOLOGIAS
    elif section_selected == "🔬 Tecnologias":
        st.markdown("## 🔬 Análise Detalhada de Tecnologias")
        
        # Estatísticas de tecnologias
        tech_counter = Counter(all_techs)
        if 'Não especificado' in tech_counter:
            del tech_counter['Não especificado']
            
            # Cards de estatísticas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                most_common_tech = tech_counter.most_common(1)[0] if tech_counter else ('N/A', 0)
                st.markdown(f"""
                <div class='metric-card'>
                    <p style='color: #666; margin: 0;'>Tecnologia mais comum</p>
                    <h3 style='color: #2d5016; margin: 0.5rem 0;'>{most_common_tech[0]}</h3>
                    <p style='color: #999; margin: 0;'>{most_common_tech[1]} ocorrências</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_tech_per_article = np.mean([len(techs) for techs in df_original['TECNOLOGIA'].apply(process_technologies)])
                st.markdown(f"""
                <div class='metric-card'>
                    <p style='color: #666; margin: 0;'>Média por artigo</p>
                    <h3 style='color: #2d5016; margin: 0.5rem 0;'>{avg_tech_per_article:.2f}</h3>
                    <p style='color: #999; margin: 0;'>tecnologias</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                tech_coverage = sum(1 for techs in df_original['TECNOLOGIA'].apply(process_technologies) 
                                  if 'Não especificado' not in techs) / len(df_original) * 100
                st.markdown(f"""
                <div class='metric-card'>
                    <p style='color: #666; margin: 0;'>Cobertura</p>
                    <h3 style='color: #2d5016; margin: 0.5rem 0;'>{tech_coverage:.1f}%</h3>
                    <p style='color: #999; margin: 0;'>dos artigos</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico principal de tecnologias
            st.markdown("### 📊 Top 15 Tecnologias de Bioenergia")
            
            tech_df = pd.DataFrame(tech_counter.most_common(15), columns=['Tecnologia', 'Quantidade'])
            
            fig_tech_bar = px.bar(
                tech_df,
                x='Quantidade',
                y='Tecnologia',
                orientation='h',
                title="",
                color='Quantidade',
                color_continuous_scale=[[0, '#e8f5e9'], [0.5, '#4caf50'], [1, '#2d5016']],
                text='Quantidade'
            )
            
            fig_tech_bar.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker=dict(cornerradius=5)
            )
            
            fig_tech_bar.update_layout(
                height=600,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Número de Artigos'),
                yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig_tech_bar, use_container_width=True)
            
            # Análise de co-ocorrência
            st.markdown("### 🔗 Análise de Co-ocorrência de Tecnologias")
            
            tech_cooccurrence = {}
            for techs in df_original['TECNOLOGIA'].apply(process_technologies):
                techs = [t for t in techs if t != 'Não especificado']
                for i, tech1 in enumerate(techs):
                    for tech2 in techs[i+1:]:
                        pair = tuple(sorted([tech1, tech2]))
                        tech_cooccurrence[pair] = tech_cooccurrence.get(pair, 0) + 1
            
            if tech_cooccurrence:
                top_combinations = sorted(tech_cooccurrence.items(), key=lambda x: x[1], reverse=True)[:10]
                
                comb_data = []
                for (tech1, tech2), count in top_combinations:
                    comb_data.append({
                        'Combinação': f"{tech1} + {tech2}",
                        'Ocorrências': count
                    })
                
                df_comb = pd.DataFrame(comb_data)
                
                fig_comb = px.bar(
                    df_comb,
                    x='Ocorrências',
                    y='Combinação',
                    orientation='h',
                    title="",
                    color='Ocorrências',
                    color_continuous_scale=[[0, '#fff3e0'], [0.5, '#ff9800'], [1, '#e65100']],
                    text='Ocorrências'
                )
                
                fig_comb.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker=dict(cornerradius=5)
                )
                
                fig_comb.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Número de Co-ocorrências'),
                    yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig_comb, use_container_width=True)
        
    # TAB 3: RESÍDUOS
    elif section_selected == "♻️ Resíduos":
            st.markdown("## ♻️ Análise Detalhada de Tipos de Resíduos")
            
            waste_counter = Counter(all_wastes)
            if 'Não especificado' in waste_counter:
                del waste_counter['Não especificado']
            
            # Layout em duas colunas
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Gráfico de pizza aprimorado
                waste_df = pd.DataFrame(waste_counter.most_common(), columns=['Resíduo', 'Quantidade'])
                
                fig_waste_pie = px.pie(
                    waste_df,
                    values='Quantidade',
                    names='Resíduo',
                    title="Distribuição de Tipos de Resíduos",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig_waste_pie.update_traces(
                    textposition='auto',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
                )
                
                fig_waste_pie.update_layout(
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
                    margin=dict(l=0, r=150, t=50, b=0)
                )
                
                st.plotly_chart(fig_waste_pie, use_container_width=True)
            
            with col2:
                # Estatísticas de resíduos
                st.markdown("### 📊 Estatísticas")
                
                for waste, count in waste_counter.most_common(5):
                    percentage = (count / sum(waste_counter.values())) * 100
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, {COLOR_PALETTE['success']} {percentage}%, 
                               {COLOR_PALETTE['light']} {percentage}%);
                               padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;'>
                        <strong>{waste}</strong>
                        <span style='float: right;'>{count} ({percentage:.1f}%)</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Evolução temporal
            st.markdown("### 📈 Evolução Temporal dos Tipos de Resíduos")
            
            if len(df_year) > 0:
                waste_year_data = []
                for idx, row in df_year.iterrows():
                    year = row['Ano']
                    wastes = process_waste_types(row.get('TIPO_RESIDUO', ''))
                    for waste in wastes:
                        if waste != 'Não especificado':
                            waste_year_data.append({'Ano': year, 'Resíduo': waste})
                
                if waste_year_data:
                    df_waste_year = pd.DataFrame(waste_year_data)
                    waste_evolution = df_waste_year.groupby(['Ano', 'Resíduo']).size().reset_index(name='Quantidade')
                    
                    # Criar gráfico de área empilhada
                    fig_waste_time = px.area(
                        waste_evolution,
                        x='Ano',
                        y='Quantidade',
                        color='Resíduo',
                        title="",
                        line_shape='spline',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    
                    fig_waste_time.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Ano'),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Quantidade de Estudos'),
                        hovermode='x unified',
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                    )
                    
                    st.plotly_chart(fig_waste_time, use_container_width=True)
        
    # TAB 4: COMBINAÇÕES
    elif section_selected == "🔄 Combinações":
            st.markdown("## 🔄 Análise de Combinações Tecnologia-Resíduo")
            
            combinations = analyze_combinations(df_original)
            
            if combinations:
                # Estatísticas de combinações
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p style='color: #666; margin: 0;'>Total de Combinações</p>
                        <h3 style='color: #2d5016; margin: 0.5rem 0;'>{len(combinations)}</h3>
                        <p style='color: #999; margin: 0;'>únicas identificadas</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    most_common_comb = combinations.most_common(1)[0] if combinations else ('N/A', 0)
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p style='color: #666; margin: 0;'>Combinação mais comum</p>
                        <h3 style='color: #2d5016; margin: 0.5rem 0; font-size: 1rem;'>{most_common_comb[0]}</h3>
                        <p style='color: #999; margin: 0;'>{most_common_comb[1]} ocorrências</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    avg_comb = sum(combinations.values()) / len(df_original)
                    st.markdown(f"""
                    <div class='metric-card'>
                        <p style='color: #666; margin: 0;'>Média por artigo</p>
                        <h3 style='color: #2d5016; margin: 0.5rem 0;'>{avg_comb:.2f}</h3>
                        <p style='color: #999; margin: 0;'>combinações</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Top combinações
                st.markdown("### 🏆 Top 20 Combinações Tecnologia + Resíduo")
                
                top_20 = combinations.most_common(20)
                comb_df = pd.DataFrame(top_20, columns=['Combinação', 'Frequência'])
                
                fig_comb_bar = px.bar(
                    comb_df,
                    x='Frequência',
                    y='Combinação',
                    orientation='h',
                    title="",
                    color='Frequência',
                    color_continuous_scale=[[0, '#fce4ec'], [0.5, '#e91e63'], [1, '#880e4f']],
                    text='Frequência'
                )
                
                fig_comb_bar.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    marker=dict(cornerradius=5)
                )
                
                fig_comb_bar.update_layout(
                    height=700,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Frequência'),
                    yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig_comb_bar, use_container_width=True)
                
                # Heatmap de combinações
                st.markdown("### 🗺️ Mapa de Calor: Tecnologia vs Tipo de Resíduo")
                
                # Criar matriz
                tech_waste_matrix = {}
                for idx, row in df_original.iterrows():
                    techs = process_technologies(row.get('TECNOLOGIA', ''))
                    wastes = process_waste_types(row.get('TIPO_RESIDUO', ''))
                    
                    for tech in techs:
                        if tech != 'Não especificado':
                            if tech not in tech_waste_matrix:
                                tech_waste_matrix[tech] = {}
                            for waste in wastes:
                                if waste != 'Não especificado':
                                    tech_waste_matrix[tech][waste] = tech_waste_matrix[tech].get(waste, 0) + 1
                
                matrix_df = pd.DataFrame(tech_waste_matrix).fillna(0).T
                
                if not matrix_df.empty:
                    # Selecionar top tecnologias e resíduos para melhor visualização
                    top_techs = matrix_df.sum(axis=1).nlargest(10).index
                    top_wastes = matrix_df.sum(axis=0).nlargest(8).index
                    matrix_subset = matrix_df.loc[top_techs, top_wastes]
                    
                    fig_heatmap = px.imshow(
                        matrix_subset.values,
                        labels=dict(x="Tipo de Resíduo", y="Tecnologia", color="Frequência"),
                        x=matrix_subset.columns,
                        y=matrix_subset.index,
                        color_continuous_scale='YlOrRd',
                        aspect='auto',
                        title=""
                    )
                    
                    fig_heatmap.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(size=11)
                    )
                    
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Diagrama Sankey
                st.markdown("### 🕸️ Fluxo de Conexões: Tecnologias → Resíduos")
                
                sankey_data = []
                for combo, count in combinations.most_common(30):
                    if ' + ' in combo:
                        parts = combo.split(' + ')
                        if len(parts) == 2:
                            tech_name, waste_name = parts
                            sankey_data.append({
                                'source': tech_name,
                                'target': waste_name,
                                'value': count
                            })
                
                if sankey_data:
                    all_nodes = set()
                    for item in sankey_data:
                        all_nodes.add(item['source'])
                        all_nodes.add(item['target'])
                    
                    node_list = list(all_nodes)
                    node_dict = {node: i for i, node in enumerate(node_list)}
                    
                    # Cores para os nós
                    node_colors = []
                    for node in node_list:
                        if node in [item['source'] for item in sankey_data]:
                            node_colors.append(COLOR_PALETTE['primary'])
                        else:
                            node_colors.append(COLOR_PALETTE['success'])
                    
                    links = []
                    for item in sankey_data:
                        links.append({
                            'source': node_dict[item['source']],
                            'target': node_dict[item['target']],
                            'value': item['value']
                        })
                    
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(color="white", width=0.5),
                            label=node_list,
                            color=node_colors
                        ),
                        link=dict(
                            source=[link['source'] for link in links],
                            target=[link['target'] for link in links],
                            value=[link['value'] for link in links],
                            color='rgba(45, 80, 22, 0.3)'
                        )
                    )])
                    
                    fig_sankey.update_layout(
                        title="",
                        font_size=10,
                        height=600,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig_sankey, use_container_width=True)
        
    # TAB 5: METODOLOGIAS
    elif section_selected == "📐 Metodologias":
            st.markdown("## 📐 Análise de Metodologias")
            
            method_counter = Counter(all_methods)
            if 'Não especificado' in method_counter:
                del method_counter['Não especificado']
            
            # Visualização em treemap
            method_df = pd.DataFrame(method_counter.most_common(15), columns=['Metodologia', 'Quantidade'])
            
            fig_method = px.treemap(
                method_df,
                path=['Metodologia'],
                values='Quantidade',
                title="Distribuição de Metodologias Utilizadas",
                color='Quantidade',
                color_continuous_scale=[[0, '#e3f2fd'], [0.5, '#2196f3'], [1, '#0d47a1']],
                hover_data={'Quantidade': ':,'}
            )
            
            fig_method.update_traces(
                textinfo="label+value+percent parent",
                marker=dict(cornerradius=5)
            )
            
            fig_method.update_layout(
                height=600,
                margin=dict(t=50, l=0, r=0, b=0)
            )
            
            st.plotly_chart(fig_method, use_container_width=True)
            
            # Distribuição de quantidade de metodologias
            st.markdown("### 📊 Distribuição: Quantidade de Metodologias por Artigo")
            
            method_counts = [len(process_methodologies(m)) for m in df_original['METODOLOGIA']]
            method_count_df = pd.DataFrame({'Número de Metodologias': method_counts})
            
            fig_hist = px.histogram(
                method_count_df,
                x='Número de Metodologias',
                title="",
                nbins=10,
                color_discrete_sequence=[COLOR_PALETTE['info']]
            )
            
            fig_hist.update_traces(marker=dict(cornerradius=5))
            
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Número de Metodologias'),
                yaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Quantidade de Artigos'),
                bargap=0.1
            )
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Metodologias por status
            st.markdown("### 📊 Metodologias por Status do Artigo")
            
            method_status_data = []
            for idx, row in df_original.iterrows():
                methods = process_methodologies(row.get('METODOLOGIA', ''))
                status = 'Incluído'  # Status_Final não existe mais, assumindo incluído
                for method in methods:
                    if method != 'Não especificado':
                        method_status_data.append({
                            'Metodologia': method,
                            'Status': status
                        })
            
            if method_status_data:
                df_method_status = pd.DataFrame(method_status_data)
                method_status_counts = df_method_status.groupby(['Status', 'Metodologia']).size().reset_index(name='Quantidade')
                
                # Selecionar top metodologias
                top_methods = df_method_status['Metodologia'].value_counts().head(10).index
                method_status_filtered = method_status_counts[method_status_counts['Metodologia'].isin(top_methods)]
                
                fig_method_status = px.bar(
                    method_status_filtered,
                    x='Metodologia',
                    y='Quantidade',
                    color='Status',
                    title="",
                    color_discrete_map={
                        'Incluido': COLOR_PALETTE['success'],
                        'Excluido': COLOR_PALETTE['danger'],
                        'Pendente': COLOR_PALETTE['warning']
                    },
                    barmode='group'
                )
                
                fig_method_status.update_traces(marker=dict(cornerradius=5))
                
                fig_method_status.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(gridcolor='rgba(0,0,0,0)', title='', tickangle=-45),
                    yaxis=dict(gridcolor='rgba(0,0,0,0.1)', title='Quantidade'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    bargap=0.15,
                    bargroupgap=0.1
                )
                
                st.plotly_chart(fig_method_status, use_container_width=True)
        
    # ========== SEÇÃO 6: VARIÁVEIS ESPECIAIS ==========
    elif section_selected == "🎯 Variáveis Especiais":
        st.header("🎯 Análise de Variáveis - Prof. Rubens")
        st.markdown("*Análise das variáveis disponíveis no dataset*")
        
        # Variáveis disponíveis no dataset
        col1, col2 = st.columns(2)
        
        with col1:
            if 'LOCALIZACAO' in df_original.columns:
                loc_count = df_original['LOCALIZACAO'].notna().sum()
                loc_pct = (loc_count / len(df_original)) * 100
                st.metric("🌍 Localização", loc_count, f"{loc_pct:.1f}% preenchido")
            else:
                st.metric("🌍 Localização", "0", "Não disponível")
        
        with col2:
            if 'CLIMA' in df_original.columns:
                clima_count = df_original['CLIMA'].notna().sum()
                clima_pct = (clima_count / len(df_original)) * 100
                st.metric("🌡️ Clima", clima_count, f"{clima_pct:.1f}% preenchido")
            else:
                st.metric("🌡️ Clima", "0", "Não disponível")
        
        # Análise simples por país
        if 'LOCALIZACAO' in df_original.columns and 'PAIS' in df_original.columns:
            st.subheader("🌍 Análise por País")
            
            paises_dados = []
            for pais in df_original['PAIS'].unique()[:10]:  # Top 10 países
                dados_pais = df_original[df_original['PAIS'] == pais]
                loc_count = dados_pais['LOCALIZACAO'].notna().sum()
                total_pais = len(dados_pais)
                pct = (loc_count / total_pais * 100) if total_pais > 0 else 0
                
                paises_dados.append({
                    'País': pais,
                    'Total': total_pais,
                    'Com_Localização': loc_count,
                    'Percentual': pct
                })
            
            df_paises = pd.DataFrame(paises_dados).sort_values('Total', ascending=False)
            st.dataframe(df_paises, use_container_width=True)
    
    # ========== SEÇÃO 7: DADOS ==========
    elif section_selected == "📑 Dados":
        st.markdown("## 📑 Visualização e Download dos Dados")
        
        # Opções de visualização
        col1, col2 = st.columns(2)
        
        with col1:
            data_view = st.selectbox(
                "Escolha os dados para visualizar:",
                ["Dados Originais", "Dados Expandidos", "Dados Processados"],
                help="Diferentes visões dos dados para análise"
            )
            
            with col2:
                # Colunas padrão que existem nos dados atuais
                default_columns = [col for col in ['ID', 'TITULO', 'ANO', 'TECNOLOGIA', 'TIPO_RESIDUO', 'METODOLOGIA'] 
                                 if col in df_original.columns]
                show_columns = st.multiselect(
                    "Selecionar colunas para exibir:",
                    df_original.columns.tolist(),
                    default=default_columns,
                    help="Escolha as colunas que deseja visualizar"
                )
            
            # Preparar dados conforme seleção
            if data_view == "Dados Originais":
                display_df = df_original.copy()
                description = "Dados originais sem processamento"
            elif data_view == "Dados Expandidos":
                if process_option == "Expandir dados (análise detalhada)":
                    display_df = df_original.copy()  # Usar df_original em vez de df
                    description = "Dados expandidos com múltiplas linhas por artigo"
                else:
                    display_df = expand_dataframe(df_original)
                    description = "Dados expandidos (gerados dinamicamente)"
            else:  # Dados Processados
                display_df = df_original.copy()
                display_df['Tecnologias_Processadas'] = display_df['TECNOLOGIA'].apply(
                    lambda x: ', '.join(process_technologies(x))
                )
                display_df['Residuos_Processados'] = display_df['TIPO_RESIDUO'].apply(
                    lambda x: ', '.join(process_waste_types(x))
                )
                display_df['Metodologias_Processadas'] = display_df['METODOLOGIA'].apply(
                    lambda x: ', '.join(process_methodologies(x))
                )
                description = "Dados originais com colunas processadas adicionais"
            
            # Filtrar colunas selecionadas
            if show_columns:
                # Verificar se as colunas existem no DataFrame
                available_columns = [col for col in show_columns if col in display_df.columns]
                if available_columns:
                    display_df = display_df[available_columns]
                else:
                    st.warning("⚠️ Nenhuma das colunas selecionadas está disponível nos dados escolhidos.")
            
            # Informações dos dados
            st.info(f"📊 **{description}** - Total de linhas: **{len(display_df):,}**")
            
            # Filtros adicionais
            st.markdown("### 🔍 Filtros")
            
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Status_Final não existe mais nos dados atuais
                st.info("📊 Filtro por Status não disponível (dados atuais não possuem Status_Final)")
            
            with filter_col2:
                if 'Ano' in display_df.columns or 'ANO' in display_df.columns:
                    year_col = 'Ano' if 'Ano' in display_df.columns else 'ANO'
                    years = pd.to_numeric(display_df[year_col], errors='coerce').dropna()
                    if len(years) > 0:
                        year_range = st.slider(
                            "Filtrar por período:",
                            int(years.min()),
                            int(years.max()),
                            (int(years.min()), int(years.max()))
                        )
                        year_mask = pd.to_numeric(display_df[year_col], errors='coerce').between(year_range[0], year_range[1])
                        display_df = display_df[year_mask]
            
            with filter_col3:
                if 'País_Processado' in display_df.columns:
                    country_filter = st.multiselect(
                        "Filtrar por País:",
                        sorted(display_df['País_Processado'].unique()),
                        default=[]
                    )
                    if country_filter:
                        display_df = display_df[display_df['País_Processado'].isin(country_filter)]
            
            # Busca por texto
            st.markdown("### 🔎 Busca por Texto")
            search_col1, search_col2 = st.columns(2)
            
            with search_col1:
                search_column = st.selectbox(
                    "Buscar na coluna:",
                    ['Todas'] + [col for col in display_df.columns if display_df[col].dtype == 'object'],
                    help="Selecione a coluna para busca ou 'Todas' para buscar em todo o dataset"
                )
            
            with search_col2:
                search_term = st.text_input(
                    "Termo de busca:",
                    placeholder="Digite o termo que deseja buscar...",
                    help="Busca não diferencia maiúsculas/minúsculas"
                )
            
            # Aplicar busca
            if search_term:
                if search_column == 'Todas':
                    # Buscar em todas as colunas de texto
                    text_columns = [col for col in display_df.columns if display_df[col].dtype == 'object']
                    mask = pd.Series([False] * len(display_df))
                    for col in text_columns:
                        mask |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
                    display_df = display_df[mask]
                else:
                    display_df = display_df[display_df[search_column].astype(str).str.contains(search_term, case=False, na=False)]
            
            # Estatísticas atualizadas
            st.success(f"✅ Exibindo **{len(display_df):,}** registros após filtros")
            
            # Visualizar dados
            if len(display_df) > 0:
                st.markdown("### 📋 Tabela de Dados")
                
                # Configurações de exibição
                display_col1, display_col2 = st.columns(2)
                
                with display_col1:
                    page_size = st.selectbox(
                        "Linhas por página:",
                        [25, 50, 100, 200, 500],
                        index=1,
                        help="Número de linhas a exibir na tabela"
                    )
                
                with display_col2:
                    if len(display_df) > page_size:
                        total_pages = (len(display_df) - 1) // page_size + 1
                        page_number = st.number_input(
                            f"Página (1-{total_pages}):",
                            min_value=1,
                            max_value=total_pages,
                            value=1
                        )
                        start_idx = (page_number - 1) * page_size
                        end_idx = min(start_idx + page_size, len(display_df))
                        display_subset = display_df.iloc[start_idx:end_idx]
                        st.caption(f"Exibindo linhas {start_idx + 1} a {end_idx} de {len(display_df)}")
                    else:
                        display_subset = display_df
                
                # Exibir tabela
                st.dataframe(
                    display_subset,
                    use_container_width=True,
                    height=600,
                    hide_index=True
                )
                
                # Downloads
                st.markdown("### 📥 Downloads")
                
                download_col1, download_col2, download_col3 = st.columns(3)
                
                with download_col1:
                    # CSV completo
                    csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label=f"📄 Download CSV ({len(display_df):,} linhas)",
                        data=csv_data,
                        file_name=f"dados_prisma_{data_view.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download dos dados filtrados em formato CSV"
                    )
                
                with download_col2:
                    # Excel
                    try:
                        import io
                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            display_df.to_excel(writer, index=False, sheet_name='Dados')
                        excel_data = buffer.getvalue()
                        
                        st.download_button(
                            label=f"📊 Download Excel ({len(display_df):,} linhas)",
                            data=excel_data,
                            file_name=f"dados_prisma_{data_view.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="Download dos dados filtrados em formato Excel"
                        )
                    except ImportError:
                        st.caption("📊 Excel indisponível (requer openpyxl)")
                
                with download_col3:
                    # JSON
                    json_data = display_df.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        label=f"📋 Download JSON ({len(display_df):,} linhas)",
                        data=json_data,
                        file_name=f"dados_prisma_{data_view.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        help="Download dos dados filtrados em formato JSON"
                    )
                
                # Estatísticas rápidas
                st.markdown("### 📊 Estatísticas Rápidas dos Dados Filtrados")
                
                stats_col1, stats_col2 = st.columns(2)
                
                with stats_col1:
                    # Status_Final não existe mais nos dados atuais
                    st.markdown("**Status dos Artigos:**")
                    st.write(f"- Todos incluídos: {len(display_df)} (100.0%)")
                    st.info("Status_Final não disponível nos dados atuais")
                
                with stats_col2:
                    if 'País_Processado' in display_df.columns:
                        country_counts = display_df['País_Processado'].value_counts().head(5)
                        st.markdown("**Top 5 Países:**")
                        for country, count in country_counts.items():
                            percentage = (count / len(display_df)) * 100
                            st.write(f"- {country}: {count} ({percentage:.1f}%)")
            
            else:
                st.warning("⚠️ Nenhum dado disponível com os filtros aplicados.")
        
    # ========== SEÇÃO 8: ANÁLISE GEOESPACIAL ==========
    elif section_selected == "🗺️ Análise Geoespacial":
        st.header("🗺️ Análise Geoespacial dos Estudos")
        
        # TABS para organizar os diferentes mapas
        tab1, tab2, tab3, tab4 = st.tabs(["🌍 Mapa Mundial", "📍 Pontos Exatos", "🔥 Mapa de Calor", "📊 Dashboard Completo"])
        
        # ========== TAB 1: MAPA MUNDIAL COLORIDO ==========
        with tab1:
            st.subheader("🌍 Mapa Mundial - Distribuição por País")
            
            # Seletor de tecnologia
            tech_cols = [col for col in df_original.columns if col in [
                'Aterro_Sanitario', 'BECCS', 'Biocombustiveis', 'Biocombustivel_Aviacao',
                'Biodigestao_Anaerobia', 'Bioetanol_Fermentacao', 'Biorrefinaria_Integrada',
                'Briquetagem_Solar', 'CHP', 'Co_Firing', 'Codigestao', 'Combustao_Direta',
                'Compostagem', 'Gaseificacao', 'Pelletizacao', 'Pirolise', 
                'Transesterificacao', 'W2VA'
            ]]
            
            tecnologia_selecionada = st.selectbox(
                "🔬 Selecione a tecnologia:",
                tech_cols,
                format_func=lambda x: x.replace('_', ' ').title(),
                key="tech_world_map"
            )
            
            if tecnologia_selecionada:
                # Filtrar dados
                paises_com_tech = df_original[df_original[tecnologia_selecionada] == 'Sim']
                
                if not paises_com_tech.empty:
                    # Contar por país e padronizar nomes
                    contagem_paises = paises_com_tech['PAIS'].value_counts().reset_index()
                    contagem_paises.columns = ['País', 'Quantidade_Estudos']
                    
                    # PADRONIZAR NOMES DOS PAÍSES
                    contagem_paises['País_Padronizado'] = contagem_paises['País'].apply(padronizar_paises)

                    # Debug: mostrar mapeamento
                    st.write("🔍 **Países mapeados:**")
                    st.write(contagem_paises[['País', 'País_Padronizado', 'Quantidade_Estudos']])
                    
                    # MAPA CHOROPLETH
                    import plotly.express as px
                    
                    fig = px.choropleth(
                        data_frame=contagem_paises,
                        locations='País_Padronizado',
                        color='Quantidade_Estudos',
                        locationmode='country names',
                        hover_name='País',  # Mostra nome original no hover
                        color_continuous_scale='Viridis',
                        title=f"Distribuição Mundial - {tecnologia_selecionada.replace('_', ' ').title()}",
                        labels={'Quantidade_Estudos': 'Nº de Estudos', 'País_Padronizado': 'País'},
                        height=600
                    )
                    
                    fig.update_layout(
                        geo=dict(
                            showframe=False,
                            showcoastlines=True,
                            projection_type='equirectangular'
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Métricas rápidas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("🌍 Total de Países", len(contagem_paises))
                    with col2:
                        st.metric("📚 Total de Estudos", contagem_paises['Quantidade_Estudos'].sum())
                    with col3:
                        st.metric("🏆 País Líder", contagem_paises.iloc[0]['País'])
                    
                else:
                    st.warning(f"❌ Nenhum estudo encontrado para {tecnologia_selecionada}")
        
        # ========== TAB 2: PONTOS EXATOS ==========
        with tab2:
            st.subheader("📍 Localização Exata dos Estudos")
            
            # Seletor de tecnologia para pontos
            tecnologia_pontos = st.selectbox(
                "🔬 Selecione a tecnologia para visualizar pontos:",
                tech_cols,
                format_func=lambda x: x.replace('_', ' ').title(),
                key="tech_points_map"
            )
            
            if tecnologia_pontos:
                # Filtrar dados com coordenadas válidas
                dados_filtrados = df_original[
                    (df_original[tecnologia_pontos] == 'Sim') &
                    (df_original['LATITUDE_DECIMAL'].notna()) &
                    (df_original['LONGITUDE_DECIMAL'].notna()) &
                    (df_original['LATITUDE_DECIMAL'] != 0) &
                    (df_original['LONGITUDE_DECIMAL'] != 0)
                ].copy()
                
                if not dados_filtrados.empty:
                    st.success(f"✅ Encontrados {len(dados_filtrados)} estudos com coordenadas exatas")
                    
                    # Preparar dados para hover
                    dados_filtrados['hover_text'] = (
                        "🏛️ <b>" + dados_filtrados['TITULO'].str[:50] + "...</b><br>" +
                        "🌍 " + dados_filtrados['PAIS'] + "<br>" +
                        "📍 " + dados_filtrados['LOCALIZACAO'] + "<br>" +
                        "🌡️ " + dados_filtrados['CLIMA'].fillna('N/A') + "<br>" +
                        "📅 " + dados_filtrados['ANO'].astype(str)
                    )
                    
                    # MAPA DE PONTOS EXATOS
                    import plotly.express as px
                    
                    fig_points = px.scatter_geo(
                        dados_filtrados,
                        lat='LATITUDE_DECIMAL',
                        lon='LONGITUDE_DECIMAL',
                        color='PAIS',
                        size_max=15,
                        hover_name='TITULO',
                        hover_data={
                            'PAIS': True,
                            'LOCALIZACAO': True,
                            'CLIMA': True,
                            'ANO': True,
                            'LATITUDE_DECIMAL': ':,.3f',
                            'LONGITUDE_DECIMAL': ':,.3f'
                        },
                        title=f"Localização Exata - {tecnologia_pontos.replace('_', ' ').title()}",
                        height=600,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig_points.update_traces(
                        marker=dict(size=8, opacity=0.8, line=dict(width=1, color='white')),
                        selector=dict(mode='markers')
                    )
                    
                    fig_points.update_layout(
                        geo=dict(
                            showframe=False,
                            showcoastlines=True,
                            projection_type='natural earth',
                            showland=True,
                            landcolor='rgb(243, 243, 243)',
                            coastlinecolor='rgb(204, 204, 204)',
                        )
                    )
                    
                    st.plotly_chart(fig_points, use_container_width=True)
                    
                    # Estatísticas por continente/região
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📍 Total de Pontos", len(dados_filtrados))
                    
                    with col2:
                        paises_unicos = dados_filtrados['PAIS'].nunique()
                        st.metric("🌍 Países Diferentes", paises_unicos)
                    
                    with col3:
                        lat_range = dados_filtrados['LATITUDE_DECIMAL'].max() - dados_filtrados['LATITUDE_DECIMAL'].min()
                        st.metric("🗺️ Dispersão Lat", f"{lat_range:.1f}°")
                    
                    with col4:
                        lon_range = dados_filtrados['LONGITUDE_DECIMAL'].max() - dados_filtrados['LONGITUDE_DECIMAL'].min()
                        st.metric("🗺️ Dispersão Lon", f"{lon_range:.1f}°")
                    
                    # Tabela detalhada com filtros
                    st.subheader("📋 Detalhes dos Estudos")
                    
                    # Filtro por país
                    paises_disponiveis = ['Todos'] + sorted(dados_filtrados['PAIS'].unique().tolist())
                    pais_filtro = st.selectbox("🌍 Filtrar por país:", paises_disponiveis, key="country_filter_points")
                    
                    if pais_filtro != 'Todos':
                        dados_mostrar = dados_filtrados[dados_filtrados['PAIS'] == pais_filtro]
                    else:
                        dados_mostrar = dados_filtrados
                    
                    # Colunas para mostrar na tabela
                    colunas_mostrar = ['TITULO', 'PAIS', 'LOCALIZACAO', 'CLIMA', 'ANO', 'LATITUDE_DECIMAL', 'LONGITUDE_DECIMAL']
                    
                    st.dataframe(
                        dados_mostrar[colunas_mostrar].rename(columns={
                            'TITULO': '📚 Título',
                            'PAIS': '🌍 País',
                            'LOCALIZACAO': '📍 Localização',
                            'CLIMA': '🌡️ Clima',
                            'ANO': '📅 Ano',
                            'LATITUDE_DECIMAL': '📐 Latitude',
                            'LONGITUDE_DECIMAL': '📐 Longitude'
                        }),
                        use_container_width=True,
                        height=300
                    )
                    
                else:
                    st.warning(f"❌ Nenhum estudo com coordenadas válidas encontrado para {tecnologia_pontos}")
                    st.info("💡 **Dica:** Alguns estudos podem ter coordenadas em branco ou inválidas (0,0)")
        with tab3:
            st.info("🔥 Em desenvolvimento...")  
        with tab4:
            st.info("📊 Em desenvolvimento...")
else:
    # Erro no carregamento dos dados do Google Sheets
    st.error("❌ **Erro ao carregar dados do Google Sheets**")
    st.markdown("""
    ## 🚨 Problemas de Conectividade
    
    Não foi possível carregar os dados automaticamente do Google Sheets.
    
    ### 🔍 Possíveis causas:
    1. **Conexão com internet** instável
    2. **URLs do Google Sheets** podem estar incorretas  
    3. **Permissões de acesso** aos dados
    4. **Limite de requisições** do Google Sheets atingido
    
    ### 🛠️ Para resolver:
    - Verifique sua conexão com a internet
    - Tente recarregar a página (F5)
    - Use o botão "🧪 Testar Dados Geo" no sidebar para diagnosticar
    
    ### 📋 Recursos Disponíveis:
    
    **📊 Visão Geral**
    - Estatísticas gerais do projeto
    - Evolução temporal das publicações
    - Análise de valores múltiplos
    
    **🔬 Tecnologias**
    - Top tecnologias de bioenergia
    - Análise de co-ocorrência
    - Padronização automática
    
    **♻️ Resíduos**
    - Distribuição por tipos
    - Evolução temporal
    - Estatísticas detalhadas
    
    **🔄 Combinações**
    - Análise Tecnologia × Resíduo
    - Mapa de calor interativo
    - Diagrama Sankey
    
    **📐 Metodologias**
    - Distribuição em treemap
    - Análise por status
    - Metodologias por artigo
    
    **🎯 Variáveis Especiais**
    - Análise das 6 variáveis solicitadas
    - Cruzamento com tecnologias
    - Filtros avançados
    
    **📑 Dados**
    - Visualização completa
    - Filtros e busca
    - Downloads em múltiplos formatos
    
    ### 🔧 Recursos Técnicos:
    - ✅ Separação automática de valores múltiplos
    - ✅ Padronização inteligente de termos
    - ✅ Visualizações interativas
    - ✅ Cache para performance
    - ✅ Downloads em CSV, Excel e JSON
    - ✅ Design responsivo
    
    ---
    
    **📞 Suporte Técnico:**  
    Centro Paulista de Estudos em Biogás e Bioprodutos (CP2B)  
    **Orientador:** Prof. Rubens Lamparelli
    """)
    
    # Cards informativos na página inicial
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card' style='text-align: center;'>
            <h3 style='color: #2d5016;'>🔍 Análise Avançada</h3>
            <p>Separação e padronização automática de valores múltiplos em campos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='metric-card' style='text-align: center;'>
            <h3 style='color: #2d5016;'>📊 Visualizações</h3>
            <p>Gráficos interativos com Plotly para análise completa dos dados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='metric-card' style='text-align: center;'>
            <h3 style='color: #2d5016;'>⚡ Performance</h3>
            <p>Cache inteligente e processamento otimizado para grandes datasets</p>
        </div>
        """, unsafe_allow_html=True)