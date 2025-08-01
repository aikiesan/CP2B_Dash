# 🌱 Dashboard PRISMA - Geotecnologias e Bioenergia

Dashboard analítico desenvolvido para revisão sistemática PRISMA sobre geotecnologias aplicadas à bioenergia.

## 🚀 Features

- **Análise de Valores Múltiplos**: Separação automática de tecnologias, resíduos e metodologias
- **Padronização Inteligente**: Normalização automática de termos técnicos
- **Visualizações Interativas**: Gráficos avançados com Plotly
- **Análise de Combinações**: Mapa de calor e diagramas Sankey
- **Filtros Avançados**: Sistema completo de busca e filtros
- **Downloads**: Exportação em CSV, Excel e JSON

## 📊 Tabs Disponíveis

1. **📊 Visão Geral** - Estatísticas gerais e evolução temporal
2. **🔬 Tecnologias** - Análise detalhada de tecnologias de bioenergia
3. **♻️ Resíduos** - Distribuição e análise de tipos de resíduos
4. **🔄 Combinações** - Análise de combinações tecnologia-resíduo
5. **📐 Metodologias** - Metodologias de pesquisa utilizadas
6. **🎯 Variáveis Especiais** - Análise das 6 variáveis solicitadas
7. **📑 Dados** - Visualização completa com filtros e downloads

## 🛠️ Instalação Local

```bash
pip install -r requirements.txt
streamlit run dashboard_prisma.py
```

## 📋 Formato dos Dados

O dashboard espera um arquivo CSV com as seguintes colunas principais:
- `ID`, `Título`, `Autores`, `Status_Final`
- `Tecnologia`, `Tipo_Residuo`, `Metodologia`
- `Pais_Regiao`, `Data da Publicacao`
- `Custo`, `Relevo Local`, `Impacto Ambiental`, `Mao_de_Obra`, `Localizacao`, `Cidade_Clima`

## 👥 Créditos

**Centro Paulista de Estudos em Biogás e Bioprodutos (CP2B)**  
**Orientador:** Prof. Rubens Lamparelli

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e de pesquisa.