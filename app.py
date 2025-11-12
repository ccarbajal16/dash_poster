"""
Dashboard de Análisis de Datos del Congreso de Suelos 2025
Aplicación principal desarrollada con Streamlit
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processor import DataProcessor
import io
import base64
import os
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Congreso de Suelos 2025",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el diseño
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .eje-e1 { border-left-color: #1f77b4 !important; }
    .eje-e2 { border-left-color: #2ca02c !important; }
    .eje-e3 { border-left-color: #ff7f0e !important; }
    .eje-e4 { border-left-color: #9467bd !important; }
    .eje-e5 { border-left-color: #d62728 !important; }
    .eje-e6 { border-left-color: #17becf !important; }
    .eje-e7 { border-left-color: #e377c2 !important; }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar el procesador de datos
@st.cache_resource
def init_data_processor():
    return DataProcessor()

def main():
    """Función principal de la aplicación"""

    # Header principal con logo
    # Logo superior centrado
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.image("images/logo_convencion.png", use_container_width=True)

    # Título principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Convención de Suelos - Pucallpa 2025</h1>
        <p>Sistema de Análisis y Gestión de Pósteres</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar procesador de datos
    processor = init_data_processor()
    
    # Cargar datos
    with st.spinner("Cargando datos del congreso..."):
        df = processor.load_data()
    
    if df.empty:
        st.error("❌ No se pudieron cargar los datos. Verifique que el archivo 'bd_congreso.csv' esté en el directorio.")
        return
    
    # Sidebar para navegación
    st.sidebar.title("🧭 Navegación")
    
    # Opciones de navegación
    pages = {
        "🏠 Página Principal": "home",
        "📈 Análisis por Eje": "eje_analysis",
        "👥 Gestión de Duplicados": "duplicates",
        "📊 Visualizaciones": "visualizations",
        "🔍 Filtros y Búsqueda": "filters",
        "📄 Exportar a PDF": "pdf_export",
        "📷 Galería de Fotos": "gallery"
    }
    
    selected_page = st.sidebar.selectbox(
        "Seleccionar página:",
        list(pages.keys()),
        index=0
    )
    
    page_key = pages[selected_page]
    
    # Información general en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Resumen General")
    
    basic_stats = processor.get_basic_stats()
    if basic_stats:
        st.sidebar.metric("Total Ponencias", basic_stats['total_ponencias'])
        st.sidebar.metric("Países Participantes", basic_stats['total_paises'])
        st.sidebar.metric("Instituciones", basic_stats['total_instituciones'])
    
    # Renderizar página seleccionada
    if page_key == "home":
        render_home_page(processor, basic_stats)
    elif page_key == "eje_analysis":
        render_eje_analysis_page(processor)
    elif page_key == "duplicates":
        render_duplicates_page(processor)
    elif page_key == "visualizations":
        render_visualizations_page(processor)
    elif page_key == "filters":
        render_filters_page(processor)
    elif page_key == "pdf_export":
        render_pdf_export_page(processor)
    elif page_key == "gallery":
        render_gallery_page()

def render_home_page(processor, basic_stats):
    """Renderiza la página principal con métricas generales"""
    
    st.header("🏠 Panel Principal")
    
    if not basic_stats:
        st.warning("No hay datos disponibles para mostrar.")
        return
    
    # Métricas principales en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Ponencias",
            value=basic_stats['total_ponencias'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="🌍 Países",
            value=basic_stats['total_paises'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="🏛️ Instituciones", 
            value=basic_stats['total_instituciones'],
            delta=None
        )
    
    with col4:
        total_ejes = len([k for k in basic_stats['distribucion_eje'].keys() if k in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7']])
        st.metric(
            label="📊 Ejes Temáticos",
            value=total_ejes,
            delta=None
        )
    
    st.markdown("---")
    
    # Distribución por eje
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Distribución por Eje Temático")
        
        if 'distribucion_eje' in basic_stats:
            eje_data = basic_stats['distribucion_eje']

            # Filtrar solo E1-E7
            eje_filtered = {k: v for k, v in eje_data.items() if k in ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7']}

            if eje_filtered:
                # Crear gráfico de barras
                fig = px.bar(
                    x=list(eje_filtered.keys()),
                    y=list(eje_filtered.values()),
                    color=list(eje_filtered.keys()),
                    color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'},
                    title="Ponencias por Eje"
                )
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="Eje Temático",
                    yaxis_title="Número de Ponencias"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Mostrar porcentajes
                total = sum(eje_filtered.values())
                for eje, count in eje_filtered.items():
                    percentage = (count / total * 100) if total > 0 else 0
                    st.write(f"**{eje}**: {count} ponencias ({percentage:.1f}%)")
    
    with col2:
        st.subheader("🌍 Top 5 Países Participantes")
        
        if 'paises_top' in basic_stats:
            paises_data = basic_stats['paises_top']
            
            # Crear gráfico de pie
            fig = px.pie(
                values=list(paises_data.values()),
                names=list(paises_data.keys()),
                title="Distribución por País"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    # Instituciones top
    st.subheader("🏛️ Top 10 Instituciones Participantes")

    if 'instituciones_top' in basic_stats:
        inst_data = basic_stats['instituciones_top']

        # Mostrar en tabla
        inst_df = pd.DataFrame(list(inst_data.items()), columns=['Institución', 'Ponencias'])
        st.dataframe(inst_df, use_container_width=True)

    st.markdown("---")

    # Estadísticas de presentación
    st.subheader("📊 Estadísticas de Presentación")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Estado de Presentación:**")
        if 'presento_stats' in basic_stats:
            presento_data = basic_stats['presento_stats']
            total = sum(presento_data.values())

            # Crear gráfico de pie
            fig = px.pie(
                values=list(presento_data.values()),
                names=list(presento_data.keys()),
                title="¿Presentó?",
                color_discrete_sequence=['#2ca02c', '#d62728']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label+value')
            st.plotly_chart(fig, use_container_width=True)

            # Mostrar detalles
            for status, count in presento_data.items():
                percentage = (count / total * 100) if total > 0 else 0
                st.write(f"• {status}: {count} ({percentage:.1f}%)")

    with col2:
        st.write("**Tipo de Ponencia:**")
        if 'ponencia_stats' in basic_stats:
            ponencia_data = basic_stats['ponencia_stats']
            total = sum(ponencia_data.values())

            # Crear gráfico de pie
            fig = px.pie(
                values=list(ponencia_data.values()),
                names=list(ponencia_data.keys()),
                title="¿Ponencia Oral?",
                color_discrete_sequence=['#ff7f0e', '#1f77b4']
            )
            fig.update_traces(textposition='inside', textinfo='percent+label+value')
            st.plotly_chart(fig, use_container_width=True)

            # Mostrar detalles
            for status, count in ponencia_data.items():
                percentage = (count / total * 100) if total > 0 else 0
                st.write(f"• {status}: {count} ({percentage:.1f}%)")

    st.markdown("---")

    # Estadísticas de Evaluación (Puntaje y Resultado)
    st.subheader("🏆 Evaluación y Rankings")

    # Verificar si las columnas existen
    df = processor.df
    if df is not None and 'Puntaje' in df.columns and 'Resultado' in df.columns:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Distribución de Puntajes:**")

            # Estadísticas de puntaje
            puntaje_mean = df['Puntaje'].mean()
            puntaje_max = df['Puntaje'].max()
            puntaje_min = df['Puntaje'].min()

            st.metric("Puntaje Promedio", f"{puntaje_mean:.2f}")
            st.metric("Puntaje Máximo", f"{puntaje_max:.2f}")
            st.metric("Puntaje Mínimo", f"{puntaje_min:.2f}")

            # Histograma de puntajes
            fig = px.histogram(
                df,
                x='Puntaje',
                nbins=20,
                title="Distribución de Puntajes",
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(
                xaxis_title="Puntaje",
                yaxis_title="Frecuencia"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.write("**Top 10 Ponencias por Puntaje:**")

            # Top 10 ponencias - solo las que deben ser evaluadas
            df_evaluables = df.copy()
            if 'Evaluar' in df.columns:
                df_evaluables = df_evaluables[df_evaluables['Evaluar'].str.upper() == 'SI']

            # Filtrar solo los que tienen puntaje válido
            df_evaluables = df_evaluables[df_evaluables['Puntaje'].notna()]

            top_10 = df_evaluables.nlargest(10, 'Puntaje')[['Nombres', 'Apellidos', 'Eje', 'Puntaje', 'Resultado']]
            top_10['Autor'] = top_10['Nombres'] + ' ' + top_10['Apellidos']
            top_10_display = top_10[['Resultado', 'Autor', 'Eje', 'Puntaje']].copy()
            top_10_display.columns = ['Rank', 'Autor', 'Eje', 'Puntaje']

            st.dataframe(
                top_10_display,
                use_container_width=True,
                hide_index=True
            )

            # Gráfico de barras de top 10
            fig = px.bar(
                top_10_display,
                x='Puntaje',
                y='Autor',
                orientation='h',
                title="Top 10 Puntajes",
                color='Eje',
                color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'}
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Puntaje",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)

def render_eje_analysis_page(processor):
    """Renderiza la página de análisis por eje"""
    
    st.header("📈 Análisis por Eje Temático")
    
    eje_stats = processor.get_eje_analysis()
    
    if not eje_stats:
        st.warning("No hay datos disponibles para el análisis por eje.")
        return
    
    # Selector de eje para análisis detallado
    selected_ejes = st.multiselect(
        "Seleccionar ejes para análisis:",
        options=['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7'],
        default=['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7']
    )
    
    if not selected_ejes:
        st.warning("Seleccione al menos un eje para mostrar el análisis.")
        return
    
    # Métricas por eje
    cols = st.columns(len(selected_ejes))
    
    for i, eje in enumerate(selected_ejes):
        if eje in eje_stats:
            with cols[i]:
                eje_info = eje_stats[eje]
                color_class = f"eje-{eje.lower()}"
                
                st.markdown(f"""
                <div class="metric-card {color_class}">
                    <h3>{eje}</h3>
                    <h2>{eje_info['total']}</h2>
                    <p>Ponencias ({eje_info['porcentaje']}%)</p>
                    <p>🌍 {eje_info['paises']} países</p>
                    <p>🏛️ {eje_info['instituciones']} instituciones</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Comparación de Ejes")
        
        # Datos para gráfico
        eje_data = {eje: eje_stats[eje]['total'] for eje in selected_ejes if eje in eje_stats}
        
        if eje_data:
            fig = px.bar(
                x=list(eje_data.keys()),
                y=list(eje_data.values()),
                color=list(eje_data.keys()),
                color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'},
                title="Ponencias por Eje Seleccionado"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Distribución Porcentual")
        
        if eje_data:
            fig = px.pie(
                values=list(eje_data.values()),
                names=list(eje_data.keys()),
                color=list(eje_data.keys()),
                color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'},
                title="Distribución Porcentual por Eje"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Análisis detallado por eje
    st.subheader("🔍 Análisis Detallado por Eje")
    
    for eje in selected_ejes:
        if eje in eje_stats:
            with st.expander(f"Detalles del Eje {eje}"):
                eje_info = eje_stats[eje]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Total de ponencias:** {eje_info['total']}")
                    st.write(f"**Porcentaje del total:** {eje_info['porcentaje']}%")
                    st.write(f"**Países participantes:** {eje_info['paises']}")
                    st.write(f"**Instituciones:** {eje_info['instituciones']}")
                
                with col2:
                    st.write("**Distribución por países:**")
                    paises_eje = eje_info['paises_list']
                    for pais, count in list(paises_eje.items())[:5]:  # Top 5
                        st.write(f"• {pais}: {count} ponencias")

def render_duplicates_page(processor):
    """Renderiza la página de gestión de duplicados"""
    
    st.header("👥 Gestión de Duplicados")
    
    duplicate_analysis = processor.detect_duplicates()
    
    if not duplicate_analysis or duplicate_analysis['total_duplicados'] == 0:
        st.success("✅ No se encontraron nombres duplicados en la base de datos.")
        return
    
    # Métricas de duplicados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "👥 Nombres Duplicados",
            duplicate_analysis['total_duplicados']
        )
    
    with col2:
        st.metric(
            "📋 Registros Afectados",
            duplicate_analysis['total_registros_duplicados']
        )
    
    with col3:
        porcentaje_duplicados = (duplicate_analysis['total_registros_duplicados'] / len(processor.df) * 100) if len(processor.df) > 0 else 0
        st.metric(
            "📊 % del Total",
            f"{porcentaje_duplicados:.1f}%"
        )
    
    st.markdown("---")
    
    # Distribución de duplicados por eje
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Duplicados por Eje")
        
        eje_duplicates = duplicate_analysis['por_eje']
        if eje_duplicates:
            fig = px.bar(
                x=list(eje_duplicates.keys()),
                y=list(eje_duplicates.values()),
                color=list(eje_duplicates.keys()),
                color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'},
                title="Registros Duplicados por Eje"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Distribución Porcentual")
        
        if eje_duplicates and sum(eje_duplicates.values()) > 0:
            fig = px.pie(
                values=list(eje_duplicates.values()),
                names=list(eje_duplicates.keys()),
                color=list(eje_duplicates.keys()),
                color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'},
                title="% Duplicados por Eje"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Lista detallada de duplicados
    st.subheader("📋 Lista Detallada de Duplicados")
    
    for i, duplicate in enumerate(duplicate_analysis['registros']):
        with st.expander(f"👤 {duplicate['nombre']} ({duplicate['cantidad']} registros)"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Nombre:** {duplicate['nombre']}")
                st.write(f"**Cantidad de registros:** {duplicate['cantidad']}")
                st.write(f"**IDs:** {', '.join(map(str, duplicate['ids']))}")
            
            with col2:
                st.write(f"**Ejes:** {', '.join(duplicate['ejes'])}")
                st.write(f"**Países:** {', '.join(set(duplicate['paises']))}")
                st.write(f"**Instituciones:** {', '.join(set(duplicate['instituciones']))}")
            
            # Mostrar registros específicos
            duplicate_records = processor.df[processor.df['Id'].isin(duplicate['ids'])]
            st.dataframe(
                duplicate_records[['Id', 'Nombres', 'Apellidos', 'Título', 'Eje', 'País', 'Institución']],
                use_container_width=True
            )

def render_visualizations_page(processor):
    """Renderiza la página de visualizaciones interactivas"""
    
    st.header("📊 Visualizaciones Interactivas")
    
    # Controles de personalización
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chart_type = st.selectbox(
            "Tipo de gráfico:",
            ["Barras", "Pie", "Barras Horizontales", "Área"]
        )
    
    with col2:
        analysis_field = st.selectbox(
            "Campo de análisis:",
            ["Eje", "País", "Institución", "Origen"]
        )
    
    with col3:
        top_n = st.slider(
            "Mostrar top N:",
            min_value=5,
            max_value=20,
            value=10
        )
    
    # Generar visualización
    df = processor.df
    
    if df.empty:
        st.warning("No hay datos disponibles para visualizar.")
        return
    
    # Procesar datos según el campo seleccionado
    if analysis_field in df.columns:
        data_counts = df[analysis_field].value_counts().head(top_n)
        
        # Crear gráfico según el tipo seleccionado
        if chart_type == "Barras":
            fig = px.bar(
                x=data_counts.index,
                y=data_counts.values,
                title=f"Top {top_n} {analysis_field}",
                labels={'x': analysis_field, 'y': 'Cantidad'}
            )
            
        elif chart_type == "Pie":
            fig = px.pie(
                values=data_counts.values,
                names=data_counts.index,
                title=f"Distribución por {analysis_field}"
            )
            
        elif chart_type == "Barras Horizontales":
            fig = px.bar(
                x=data_counts.values,
                y=data_counts.index,
                orientation='h',
                title=f"Top {top_n} {analysis_field}",
                labels={'x': 'Cantidad', 'y': analysis_field}
            )
            
        elif chart_type == "Área":
            fig = px.area(
                x=data_counts.index,
                y=data_counts.values,
                title=f"Distribución por {analysis_field}"
            )
        
        # Personalizar colores para Eje
        if analysis_field == "Eje":
            color_map = {'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'}
            fig.update_traces(
                marker_color=[color_map.get(x, '#1f77b4') for x in data_counts.index]
            )
        
        fig.update_layout(
            height=500,
            showlegend=True if chart_type == "Pie" else False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos
        st.subheader("📋 Datos de la Visualización")
        
        viz_df = pd.DataFrame({
            analysis_field: data_counts.index,
            'Cantidad': data_counts.values,
            'Porcentaje': (data_counts.values / data_counts.sum() * 100).round(2)
        })
        
        st.dataframe(viz_df, use_container_width=True)
        
        # Botón de exportación
        if st.button("📥 Exportar Gráfico"):
            # Convertir gráfico a imagen
            img_bytes = fig.to_image(format="png", width=800, height=600)
            
            st.download_button(
                label="Descargar PNG",
                data=img_bytes,
                file_name=f"grafico_{analysis_field}_{chart_type.lower()}.png",
                mime="image/png"
            )

def render_filters_page(processor):
    """Renderiza la página de filtros y búsqueda"""
    
    st.header("🔍 Filtros y Búsqueda Avanzada")
    
    # Controles de filtro
    col1, col2, col3 = st.columns(3)

    with col1:
        # Filtro por Eje
        ejes_disponibles = processor.get_unique_values('Eje')
        selected_ejes = st.multiselect(
            "Filtrar por Eje:",
            options=ejes_disponibles,
            default=[]
        )

    with col2:
        # Filtro por País
        paises_disponibles = processor.get_unique_values('País')
        selected_paises = st.multiselect(
            "Filtrar por País:",
            options=paises_disponibles,
            default=[]
        )

    with col3:
        # Filtro por Institución
        instituciones_disponibles = processor.get_unique_values('Institución')
        selected_instituciones = st.multiselect(
            "Filtrar por Institución:",
            options=instituciones_disponibles[:20],  # Limitar para performance
            default=[]
        )

    # Segunda fila de filtros
    col4, col5, col6 = st.columns(3)

    with col4:
        # Filtro por Presentó
        presento_disponibles = processor.get_unique_values('Presentó')
        selected_presento = st.multiselect(
            "Filtrar por Presentó:",
            options=presento_disponibles,
            default=[]
        )

    with col5:
        # Filtro por Ponencia
        ponencia_disponibles = processor.get_unique_values('Ponencia')
        selected_ponencia = st.multiselect(
            "Filtrar por Ponencia:",
            options=ponencia_disponibles,
            default=[]
        )

    with col6:
        # Filtro por Sitio
        sitio_disponibles = processor.get_unique_values('Sitio')
        selected_sitio = st.multiselect(
            "Filtrar por Sitio:",
            options=sitio_disponibles,
            default=[]
        )

    # Tercera fila de filtros - Evaluación
    if processor.df is not None and 'Puntaje' in processor.df.columns and 'Resultado' in processor.df.columns:
        st.markdown("---")
        st.write("**Filtros de Evaluación:**")

        col6, col7 = st.columns(2)

        with col6:
            # Filtro por rango de Puntaje
            puntaje_min = float(processor.df['Puntaje'].min())
            puntaje_max = float(processor.df['Puntaje'].max())

            selected_puntaje_range = st.slider(
                "Rango de Puntaje:",
                min_value=puntaje_min,
                max_value=puntaje_max,
                value=(puntaje_min, puntaje_max),
                step=0.01
            )

        with col7:
            # Filtro por rango de Resultado (ranking)
            resultado_min = int(processor.df['Resultado'].min())
            resultado_max = int(processor.df['Resultado'].max())

            selected_resultado_range = st.slider(
                "Rango de Ranking (Resultado):",
                min_value=resultado_min,
                max_value=resultado_max,
                value=(resultado_min, resultado_max),
                step=1
            )
    else:
        selected_puntaje_range = None
        selected_resultado_range = None

    # Búsqueda de texto
    search_text = st.text_input(
        "🔍 Búsqueda de texto (en títulos, nombres, instituciones):",
        placeholder="Ingrese términos de búsqueda..."
    )
    
    # Botón para limpiar filtros
    if st.button("🧹 Limpiar Filtros"):
        st.experimental_rerun()
    
    # Aplicar filtros
    filters = {
        'eje': selected_ejes,
        'pais': selected_paises,
        'institucion': selected_instituciones,
        'presento': selected_presento,
        'ponencia': selected_ponencia,
        'sitio': selected_sitio,
        'texto': search_text,
        'puntaje_range': selected_puntaje_range,
        'resultado_range': selected_resultado_range
    }
    
    filtered_df = processor.filter_data(filters)
    
    # Mostrar resultados
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Registros Encontrados", len(filtered_df))
    
    with col2:
        total_records = len(processor.df)
        percentage = (len(filtered_df) / total_records * 100) if total_records > 0 else 0
        st.metric("📊 % del Total", f"{percentage:.1f}%")
    
    with col3:
        unique_countries = filtered_df['País'].nunique() if not filtered_df.empty else 0
        st.metric("🌍 Países", unique_countries)
    
    # Mostrar datos filtrados
    if not filtered_df.empty:
        st.subheader("📋 Resultados de la Búsqueda")
        
        # Selector de columnas a mostrar
        all_columns = filtered_df.columns.tolist()
        default_columns = ['Id', 'Nombres', 'Apellidos', 'Título', 'Eje', 'País', 'Institución']
        selected_columns = st.multiselect(
            "Seleccionar columnas a mostrar:",
            options=all_columns,
            default=[col for col in default_columns if col in all_columns]
        )
        
        if selected_columns:
            st.dataframe(
                filtered_df[selected_columns],
                use_container_width=True,
                height=400
            )
            
            # Exportación de datos filtrados
            st.subheader("📥 Exportar Datos Filtrados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Exportar a CSV
                csv_data = filtered_df[selected_columns].to_csv(index=False)
                st.download_button(
                    label="📄 Descargar CSV",
                    data=csv_data,
                    file_name="datos_filtrados.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Exportar a Excel
                if st.button("📊 Generar Excel"):
                    excel_file = processor.export_to_excel(
                        filtered_df[selected_columns],
                        "datos_filtrados.xlsx"
                    )
                    if excel_file:
                        with open(excel_file, "rb") as f:
                            st.download_button(
                                label="📊 Descargar Excel",
                                data=f.read(),
                                file_name="datos_filtrados.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
        
        # Estadísticas de los datos filtrados
        st.subheader("📊 Estadísticas de Datos Filtrados")
        
        if 'Eje' in filtered_df.columns:
            eje_counts = filtered_df['Eje'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Distribución por Eje:**")
                for eje, count in eje_counts.items():
                    percentage = (count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                    st.write(f"• {eje}: {count} ({percentage:.1f}%)")
            
            with col2:
                if len(eje_counts) > 0:
                    fig = px.pie(
                        values=eje_counts.values,
                        names=eje_counts.index,
                        title="Distribución por Eje (Datos Filtrados)",
                        color=eje_counts.index,
                        color_discrete_map={'E1': '#1f77b4', 'E2': '#2ca02c', 'E3': '#ff7f0e', 'E4': '#9467bd', 'E5': '#d62728', 'E6': '#17becf', 'E7': '#e377c2'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning("⚠️ No se encontraron registros que coincidan con los filtros aplicados.")

def render_pdf_export_page(processor):
    """Renderiza la página de exportación a PDF"""
    
    st.header("📄 Exportar Ranking a PDF")
    
    st.markdown("""
    Esta funcionalidad le permite exportar los rankings de las mejores ponencias a un documento PDF 
    profesionalmente formateado. El PDF incluye:
    - Título y fecha de generación
    - Resumen estadístico del ranking
    - Tabla con las mejores ponencias destacando el Top 3 (oro, plata, bronce)
    - Información completa de cada ponencia
    """)
    
    st.markdown("---")
    
    # Verificar que existan las columnas necesarias
    if processor.df is None or processor.df.empty:
        st.error("❌ No hay datos disponibles para exportar.")
        return
    
    if 'Puntaje' not in processor.df.columns or 'Resultado' not in processor.df.columns:
        st.error("❌ Los datos no contienen información de puntajes necesaria para generar el ranking.")
        return
    
    # Controles de configuración
    st.subheader("⚙️ Configuración del Reporte")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Selector de cantidad de registros
        top_n = st.number_input(
            "Número de ponencias a incluir:",
            min_value=1,
            max_value=min(100, len(processor.df)),
            value=10,
            step=1,
            help="Seleccione cuántas de las mejores ponencias desea incluir en el PDF"
        )
    
    with col2:
        # Filtro por eje
        eje_options = ["Todos los ejes"] + processor.eje_values
        selected_eje = st.selectbox(
            "Filtrar por Eje Temático:",
            options=eje_options,
            help="Puede generar el ranking solo para un eje específico"
        )
        
        filter_by_eje = None if selected_eje == "Todos los ejes" else selected_eje
    
    with col3:
        st.write("")  # Espaciado para alinear con otros controles
    
    # Selector de columnas
    st.markdown("### 📋 Seleccionar Columnas a Incluir")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Columnas obligatorias:**")
        st.info("• Resultado (Ranking)\n• Nombres\n• Apellidos\n• Eje\n• Puntaje")
    
    with col2:
        st.write("**Columnas adicionales:**")
        available_columns = []
        if 'Título' in processor.df.columns:
            available_columns.append('Título')
        if 'País' in processor.df.columns:
            available_columns.append('País')
        if 'Institución' in processor.df.columns:
            available_columns.append('Institución')
        if 'Origen' in processor.df.columns:
            available_columns.append('Origen')
        
        selected_additional_columns = st.multiselect(
            "Seleccione columnas adicionales:",
            options=available_columns,
            default=[],
            help="Nota: El Título se ajustará automáticamente con saltos de línea"
        )
    
    # Vista previa de los datos que se exportarán
    st.markdown("---")
    st.subheader("👀 Vista Previa del Ranking")
    
    # Obtener datos para preview
    df_preview = processor.df.copy()

    # Solo incluir registros con Evaluar='SI' si la columna existe
    if 'Evaluar' in df_preview.columns:
        df_preview = df_preview[df_preview['Evaluar'].str.upper() == 'SI']

    # Filtrar por eje si se especifica
    if filter_by_eje:
        df_preview = df_preview[df_preview['Eje'] == filter_by_eje]

    # Filtrar solo los que tienen puntaje válido
    df_preview = df_preview[df_preview['Puntaje'].notna()]

    # Ordenar por puntaje y tomar los top N
    df_preview = df_preview.nlargest(top_n, 'Puntaje')
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Ponencias en el ranking", len(df_preview))
    
    with col2:
        if len(df_preview) > 0:
            st.metric("🏆 Puntaje más alto", f"{df_preview['Puntaje'].max():.2f}")
    
    with col3:
        if len(df_preview) > 0:
            st.metric("📉 Puntaje más bajo", f"{df_preview['Puntaje'].min():.2f}")
    
    with col4:
        if len(df_preview) > 0:
            st.metric("📊 Puntaje promedio", f"{df_preview['Puntaje'].mean():.2f}")
    
    # Tabla de preview
    if not df_preview.empty:
        st.markdown("**Datos a exportar:**")
        
        # Construir columnas según selección
        preview_columns = ['Resultado', 'Nombres', 'Apellidos', 'Eje']
        preview_columns.extend(selected_additional_columns)
        preview_columns.append('Puntaje')
        
        preview_columns = [col for col in preview_columns if col in df_preview.columns]
        
        # Crear DataFrame para mostrar con formato
        display_df = df_preview[preview_columns].copy()
        display_df['Puntaje'] = display_df['Puntaje'].apply(lambda x: f"{x:.2f}")

        # Convertir 'Resultado' a string para poder agregar emojis
        display_df['Resultado'] = display_df['Resultado'].astype(str)

        # Añadir indicadores de medalla para Top 3
        if len(display_df) >= 1:
            display_df.iloc[0, display_df.columns.get_loc('Resultado')] = f"🥇 {display_df.iloc[0]['Resultado']}"
        if len(display_df) >= 2:
            display_df.iloc[1, display_df.columns.get_loc('Resultado')] = f"🥈 {display_df.iloc[1]['Resultado']}"
        if len(display_df) >= 3:
            display_df.iloc[2, display_df.columns.get_loc('Resultado')] = f"🥉 {display_df.iloc[2]['Resultado']}"
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400,
            hide_index=True
        )
    else:
        st.warning("⚠️ No hay datos disponibles con los filtros seleccionados.")
    
    # Botón de exportación
    st.markdown("---")
    st.subheader("💾 Generar y Descargar PDF")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        📝 **Nota:** El PDF generado incluirá:
        - Encabezado con título y fecha
        - Resumen estadístico con promedios y totales
        - Tabla formateada con colores alternados
        - Destacado especial para Top 3 (oro, plata, bronce)
        - Pie de página con información del evento
        """)
    
    with col2:
        st.write("")  # Espaciado
        st.write("")  # Espaciado
        
        if st.button("📄 Generar PDF", type="primary", use_container_width=True):
            if df_preview.empty:
                st.error("❌ No hay datos para exportar con los filtros seleccionados.")
            else:
                try:
                    with st.spinner("Generando PDF... Por favor espere."):
                        # Generar PDF
                        pdf_buffer = processor.export_to_pdf(
                            top_n=top_n,
                            filter_by_eje=filter_by_eje,
                            selected_columns=selected_additional_columns
                        )
                        
                        # Generar nombre de archivo
                        filename = f"ranking_top_{top_n}"
                        if filter_by_eje:
                            filename += f"_{filter_by_eje}"
                        filename += ".pdf"
                        
                        # Botón de descarga
                        st.success("✅ PDF generado exitosamente!")
                        
                        st.download_button(
                            label="⬇️ Descargar PDF",
                            data=pdf_buffer,
                            file_name=filename,
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                        
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {str(e)}")
                    st.exception(e)
    
    # Información adicional
    st.markdown("---")
    
    with st.expander("ℹ️ Información sobre el formato PDF"):
        st.markdown("""
        ### Características del PDF generado:
        
        **Diseño y formato:**
        - Tamaño de página: A4
        - Fuente profesional: Helvetica
        - Colores institucionales del evento
        - Ajuste automático de anchos de columna
        
        **Contenido incluido:**
        - **Encabezado:** Título del ranking y fecha/hora de generación
        - **Resumen estadístico:** Total de ponencias, promedios y rangos de puntajes
        - **Tabla de ranking:** Datos ordenados por puntaje descendente
        - **Destacado Top 3:** Colores oro (🥇), plata (🥈) y bronce (🥉) para los primeros 3 lugares
        - **Pie de página:** Información del evento
        
        **Columnas incluidas:**
        - **Obligatorias:** Resultado, Nombres, Apellidos, Eje, Puntaje
        - **Opcionales:** Seleccione las que necesite (Título, País, Institución, Origen)
        
        **Características especiales:**
        - **Título:** Se ajusta automáticamente con saltos de línea para textos largos
        - **Institución:** También se ajusta para nombres largos de instituciones
        - **Anchos dinámicos:** Las columnas se escalan proporcionalmente para optimizar el espacio
        
        **Uso recomendado:**
        - Para compartir resultados oficiales con participantes
        - Para archivar documentación del evento
        - Para presentaciones y reportes institucionales
        - Para diplomas o certificados de reconocimiento
        """)

def render_gallery_page():
    """Renderiza la página de galería de fotos"""

    st.header("📷 Galería de Fotos del Congreso")

    st.markdown("""
    Imágenes y momentos destacados del **Congreso de Suelos 2025 - Pucallpa**.
    """)

    st.markdown("---")

    # Directorio de fotos
    photos_dir = Path("Photos")

    # Verificar que el directorio existe
    if not photos_dir.exists():
        st.error("❌ No se encontró el directorio 'Photos'. Por favor, cree la carpeta y agregue imágenes.")
        return

    # Obtener todas las imágenes del directorio
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    images = []

    for ext in image_extensions:
        images.extend(list(photos_dir.glob(f'*{ext}')))
        images.extend(list(photos_dir.glob(f'*{ext.upper()}')))

    # Ordenar imágenes por nombre
    images = sorted(set(images))

    if not images:
        st.warning("⚠️ No se encontraron imágenes en el directorio 'Photos'. Por favor, agregue archivos de imagen (PNG, JPG, etc.).")
        return

    # Mostrar contador de imágenes
    st.info(f"📊 Total de imágenes: **{len(images)}**")

    st.markdown("---")

    # Controles de visualización
    col1, col2 = st.columns([1, 2])

    with col1:
        columns_per_row = st.slider(
            "Imágenes por fila:",
            min_value=1,
            max_value=4,
            value=3,
            help="Ajuste el número de imágenes que se muestran por fila"
        )

    with col2:
        view_mode = st.radio(
            "Modo de visualización:",
            options=["Galería", "Lista detallada"],
            horizontal=True,
            help="Seleccione cómo desea ver las imágenes"
        )

    st.markdown("---")

    # Modo de galería (grid)
    if view_mode == "Galería":
        # Calcular el número de filas necesarias
        num_rows = (len(images) + columns_per_row - 1) // columns_per_row

        idx = 0
        for row in range(num_rows):
            cols = st.columns(columns_per_row)
            for col_idx in range(columns_per_row):
                if idx < len(images):
                    with cols[col_idx]:
                        img_path = images[idx]

                        # Mostrar la imagen
                        st.image(
                            str(img_path),
                            use_container_width=True,
                            caption=img_path.name
                        )

                        # Información adicional en un expander
                        with st.expander("ℹ️ Información"):
                            file_size = img_path.stat().st_size
                            file_size_kb = file_size / 1024

                            if file_size_kb < 1024:
                                size_str = f"{file_size_kb:.2f} KB"
                            else:
                                size_str = f"{file_size_kb/1024:.2f} MB"

                            st.write(f"**Nombre:** {img_path.name}")
                            st.write(f"**Tamaño:** {size_str}")
                            st.write(f"**Formato:** {img_path.suffix.upper()[1:]}")

                    idx += 1

    # Modo de lista detallada
    else:
        for idx, img_path in enumerate(images, 1):
            st.markdown(f"### 🖼️ Imagen {idx}: {img_path.name}")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.image(
                    str(img_path),
                    use_container_width=True
                )

            with col2:
                file_size = img_path.stat().st_size
                file_size_kb = file_size / 1024

                if file_size_kb < 1024:
                    size_str = f"{file_size_kb:.2f} KB"
                else:
                    size_str = f"{file_size_kb/1024:.2f} MB"

                st.markdown("**Detalles:**")
                st.write(f"📁 **Nombre:** {img_path.name}")
                st.write(f"📊 **Tamaño:** {size_str}")
                st.write(f"🎨 **Formato:** {img_path.suffix.upper()[1:]}")

                # Botón de descarga (opcional)
                with open(img_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Descargar",
                        data=file,
                        file_name=img_path.name,
                        mime=f"image/{img_path.suffix[1:]}",
                        use_container_width=True
                    )

            if idx < len(images):
                st.markdown("---")

    # Información adicional al final
    st.markdown("---")

    with st.expander("💡 Información sobre la galería"):
        st.markdown("""
        ### Características de la Galería:

        **Formatos soportados:**
        - PNG, JPG/JPEG, GIF, BMP, WEBP

        **Modos de visualización:**
        - **Galería:** Vista en cuadrícula ajustable (1-4 imágenes por fila)
        - **Lista detallada:** Vista ampliada con información completa y opción de descarga

        **Agregar nuevas imágenes:**
        1. Coloque sus imágenes en la carpeta `Photos` del proyecto
        2. Recargue la página para ver las nuevas imágenes

        **Descargar imágenes:**
        - Use el modo "Lista detallada" para descargar imágenes individuales
        """)

if __name__ == "__main__":
    main()