"""
Módulo de procesamiento de datos para el Dashboard del Congreso de Suelos
Maneja la carga, validación y procesamiento del archivo CSV
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
import os

# Mapeo de países a códigos ISO de 2 letras
COUNTRY_TO_CODE = {
    'Perú': 'PE',
    'Peru': 'PE',
    'Brasil': 'BR',
    'Brazil': 'BR',
    'Argentina': 'AR',
    'Chile': 'CL',
    'Colombia': 'CO',
    'Ecuador': 'EC',
    'Bolivia': 'BO',
    'Venezuela': 'VE',
    'Paraguay': 'PY',
    'Uruguay': 'UY',
    'México': 'MX',
    'Mexico': 'MX',
    'Costa Rica': 'CR',
    'Panamá': 'PA',
    'Panama': 'PA',
    'Guatemala': 'GT',
    'Honduras': 'HN',
    'El Salvador': 'SV',
    'Nicaragua': 'NI',
    'Cuba': 'CU',
    'República Dominicana': 'DO',
    'Puerto Rico': 'PR',
    'España': 'ES',
    'Spain': 'ES',
    'Estados Unidos': 'US',
    'USA': 'US',
    'United States': 'US',
    'Canadá': 'CA',
    'Canada': 'CA',
    'Francia': 'FR',
    'France': 'FR',
    'Alemania': 'DE',
    'Germany': 'DE',
    'Italia': 'IT',
    'Italy': 'IT',
    'Reino Unido': 'GB',
    'United Kingdom': 'GB',
    'Portugal': 'PT',
    'Países Bajos': 'NL',
    'Netherlands': 'NL',
    'Bélgica': 'BE',
    'Belgium': 'BE',
    'Suiza': 'CH',
    'Switzerland': 'CH',
    'Australia': 'AU',
    'Nueva Zelanda': 'NZ',
    'New Zealand': 'NZ',
    'Japón': 'JP',
    'Japan': 'JP',
    'China': 'CN',
    'India': 'IN',
    'Sudáfrica': 'ZA',
    'South Africa': 'ZA'
}

def get_country_code(country_name: str) -> str:
    """
    Obtiene el código ISO de 2 letras para un país dado
    
    Args:
        country_name: Nombre del país
        
    Returns:
        Código ISO del país o string vacío si no se encuentra
    """
    if not country_name or pd.isna(country_name):
        return ''
    
    # Limpiar nombre del país
    country_clean = str(country_name).strip()
    
    # Buscar en el diccionario (case-insensitive)
    for key, code in COUNTRY_TO_CODE.items():
        if key.lower() == country_clean.lower():
            return code
    
    # Si no se encuentra, intentar buscar parcialmente
    for key, code in COUNTRY_TO_CODE.items():
        if key.lower() in country_clean.lower() or country_clean.lower() in key.lower():
            return code
    
    return ''  # No se encontró código

class DataProcessor:
    """Clase para procesar y validar los datos del congreso"""
    
    def __init__(self, csv_path: str = "bd_congreso.csv"):
        self.csv_path = csv_path
        self.df = None
        self.required_columns = ['Id', 'Nombres', 'Apellidos', 'Título', 'Eje', 'País']
        self.eje_values = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7']
        
    @st.cache_data
    def load_data(_self) -> pd.DataFrame:
        """Carga y valida los datos del CSV"""
        try:
            _self.df = pd.read_csv(_self.csv_path, encoding='utf-8')
            _self._validate_data()
            _self._clean_data()
            return _self.df
        except FileNotFoundError:
            st.error(f"❌ No se encontró el archivo {_self.csv_path}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Error al cargar los datos: {str(e)}")
            return pd.DataFrame()
    
    def _validate_data(self):
        """Valida la estructura de los datos"""
        if self.df is None:
            raise ValueError("No hay datos cargados")
        
        # Verificar columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Faltan columnas requeridas: {missing_cols}")
        
        # Verificar valores de Eje
        invalid_ejes = self.df[~self.df['Eje'].isin(self.eje_values + [np.nan])]['Eje'].unique()
        if len(invalid_ejes) > 0:
            st.warning(f"⚠️ Valores de Eje no válidos encontrados: {invalid_ejes}")
    
    def _clean_data(self):
        """Limpia y prepara los datos"""
        if self.df is None:
            return

        # Limpiar espacios en blanco
        string_columns = self.df.select_dtypes(include=['object']).columns
        for col in string_columns:
            self.df[col] = self.df[col].astype(str).str.strip()

        # Reemplazar valores vacíos
        self.df = self.df.replace(['', 'nan', 'None'], np.nan)

        # Crear nombre completo para análisis de duplicados
        self.df['Nombre_Completo'] = self.df['Nombres'].astype(str) + ' ' + self.df['Apellidos'].astype(str)

        # Verificar si existe columna Evaluar
        has_evaluar = 'Evaluar' in self.df.columns

        # Calcular dinámicamente Puntaje si existe Calificativo
        if 'Calificativo' in self.df.columns:
            # Convertir a numérico, forzando errores a NaN
            self.df['Calificativo'] = pd.to_numeric(self.df['Calificativo'], errors='coerce')

            # Solo calcular Puntaje para registros con Evaluar='SI' (si la columna existe)
            if has_evaluar:
                # Inicializar Puntaje como NaN para todos
                self.df['Puntaje'] = np.nan
                # Calcular solo para los que deben ser evaluados
                mask_evaluar = self.df['Evaluar'].str.upper() == 'SI'
                self.df.loc[mask_evaluar, 'Puntaje'] = self.df.loc[mask_evaluar, 'Calificativo'] / 100
            else:
                # Si no existe la columna Evaluar, calcular para todos
                self.df['Puntaje'] = self.df['Calificativo'] / 100

        # Calcular dinámicamente Resultado (ranking) si existe Puntaje
        if 'Puntaje' in self.df.columns:
            # Convertir a numérico, forzando errores a NaN
            self.df['Puntaje'] = pd.to_numeric(self.df['Puntaje'], errors='coerce')

            # Inicializar Resultado como NaN
            self.df['Resultado'] = pd.NA

            # Solo calcular ranking para registros con Evaluar='SI' (si la columna existe)
            if has_evaluar:
                mask_evaluar = self.df['Evaluar'].str.upper() == 'SI'
                # Filtrar solo los que tienen puntaje válido y deben ser evaluados
                mask_valid = mask_evaluar & self.df['Puntaje'].notna()
                if mask_valid.any():
                    # Dense ranking: sin gaps, el mejor Puntaje obtiene rank 1
                    # Usar Int64 para permitir NaN en columnas de tipo entero
                    self.df.loc[mask_valid, 'Resultado'] = self.df.loc[mask_valid, 'Puntaje'].rank(
                        method='dense', ascending=False
                    ).astype('Int64')
            else:
                # Si no existe la columna Evaluar, calcular ranking para todos los que tienen puntaje
                mask_valid = self.df['Puntaje'].notna()
                if mask_valid.any():
                    self.df.loc[mask_valid, 'Resultado'] = self.df.loc[mask_valid, 'Puntaje'].rank(
                        method='dense', ascending=False
                    ).astype('Int64')

            # Asegurar que Resultado sea tipo Int64
            self.df['Resultado'] = self.df['Resultado'].astype('Int64')
    
    def get_basic_stats(self) -> Dict:
        """Obtiene estadísticas básicas de los datos"""
        if self.df is None or self.df.empty:
            return {}

        stats = {
            'total_ponencias': len(self.df),
            'total_paises': self.df['País'].nunique(),
            'total_instituciones': self.df['Institución'].nunique(),
            'distribucion_eje': self.df['Eje'].value_counts().to_dict(),
            'paises_top': self.df['País'].value_counts().head(5).to_dict(),
            'instituciones_top': self.df['Institución'].value_counts().head(5).to_dict(),
            'presento_stats': self.df['Presentó'].value_counts().to_dict(),
            'ponencia_stats': self.df['Ponencia'].value_counts().to_dict()
        }
        return stats
    
    def get_eje_analysis(self) -> Dict:
        """Análisis detallado por eje temático"""
        if self.df is None or self.df.empty:
            return {}
        
        eje_stats = {}
        for eje in self.eje_values:
            eje_data = self.df[self.df['Eje'] == eje]
            eje_stats[eje] = {
                'total': len(eje_data),
                'porcentaje': round(len(eje_data) / len(self.df) * 100, 2),
                'paises': eje_data['País'].nunique(),
                'instituciones': eje_data['Institución'].nunique(),
                'paises_list': eje_data['País'].value_counts().to_dict()
            }
        
        return eje_stats
    
    def detect_duplicates(self) -> Dict:
        """Detecta nombres duplicados y analiza su distribución"""
        if self.df is None or self.df.empty:
            return {}
        
        # Detectar duplicados por nombre completo
        duplicates = self.df[self.df.duplicated(subset=['Nombre_Completo'], keep=False)]
        
        if duplicates.empty:
            return {'total_duplicados': 0, 'registros': [], 'por_eje': {}}
        
        # Agrupar duplicados
        duplicate_groups = duplicates.groupby('Nombre_Completo')
        
        duplicate_analysis = {
            'total_duplicados': len(duplicate_groups),
            'total_registros_duplicados': len(duplicates),
            'registros': [],
            'por_eje': {}
        }
        
        # Análisis por eje de duplicados
        for eje in self.eje_values:
            eje_duplicates = duplicates[duplicates['Eje'] == eje]
            duplicate_analysis['por_eje'][eje] = len(eje_duplicates)
        
        # Detalles de cada grupo de duplicados
        for name, group in duplicate_groups:
            duplicate_analysis['registros'].append({
                'nombre': name,
                'cantidad': len(group),
                'ejes': group['Eje'].tolist(),
                'paises': group['País'].tolist(),
                'instituciones': group['Institución'].tolist(),
                'ids': group['Id'].tolist()
            })
        
        return duplicate_analysis
    
    def filter_data(self, filters: Dict) -> pd.DataFrame:
        """Aplica filtros a los datos"""
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        filtered_df = self.df.copy()

        # Filtro por Eje
        if 'eje' in filters and filters['eje']:
            if isinstance(filters['eje'], list):
                filtered_df = filtered_df[filtered_df['Eje'].isin(filters['eje'])]
            else:
                filtered_df = filtered_df[filtered_df['Eje'] == filters['eje']]

        # Filtro por País
        if 'pais' in filters and filters['pais']:
            if isinstance(filters['pais'], list):
                filtered_df = filtered_df[filtered_df['País'].isin(filters['pais'])]
            else:
                filtered_df = filtered_df[filtered_df['País'] == filters['pais']]

        # Filtro por Institución
        if 'institucion' in filters and filters['institucion']:
            if isinstance(filters['institucion'], list):
                filtered_df = filtered_df[filtered_df['Institución'].isin(filters['institucion'])]
            else:
                filtered_df = filtered_df[filtered_df['Institución'] == filters['institucion']]

        # Filtro por Presentó
        if 'presento' in filters and filters['presento']:
            if isinstance(filters['presento'], list):
                filtered_df = filtered_df[filtered_df['Presentó'].isin(filters['presento'])]
            else:
                filtered_df = filtered_df[filtered_df['Presentó'] == filters['presento']]

        # Filtro por Ponencia
        if 'ponencia' in filters and filters['ponencia']:
            if isinstance(filters['ponencia'], list):
                filtered_df = filtered_df[filtered_df['Ponencia'].isin(filters['ponencia'])]
            else:
                filtered_df = filtered_df[filtered_df['Ponencia'] == filters['ponencia']]

        # Filtro por Sitio
        if 'sitio' in filters and filters['sitio']:
            if isinstance(filters['sitio'], list):
                filtered_df = filtered_df[filtered_df['Sitio'].isin(filters['sitio'])]
            else:
                filtered_df = filtered_df[filtered_df['Sitio'] == filters['sitio']]

        # Búsqueda de texto
        if 'texto' in filters and filters['texto']:
            texto = filters['texto'].lower()
            mask = (
                filtered_df['Título'].str.lower().str.contains(texto, na=False) |
                filtered_df['Nombres'].str.lower().str.contains(texto, na=False) |
                filtered_df['Apellidos'].str.lower().str.contains(texto, na=False) |
                filtered_df['Institución'].str.lower().str.contains(texto, na=False)
            )
            filtered_df = filtered_df[mask]

        # Filtro por rango de Puntaje
        if 'puntaje_range' in filters and filters['puntaje_range'] is not None:
            if 'Puntaje' in filtered_df.columns:
                min_puntaje, max_puntaje = filters['puntaje_range']
                filtered_df = filtered_df[
                    (filtered_df['Puntaje'] >= min_puntaje) &
                    (filtered_df['Puntaje'] <= max_puntaje)
                ]

        # Filtro por rango de Resultado
        if 'resultado_range' in filters and filters['resultado_range'] is not None:
            if 'Resultado' in filtered_df.columns:
                min_resultado, max_resultado = filters['resultado_range']
                filtered_df = filtered_df[
                    (filtered_df['Resultado'] >= min_resultado) &
                    (filtered_df['Resultado'] <= max_resultado)
                ]

        return filtered_df
    
    def get_unique_values(self, column: str) -> List[str]:
        """Obtiene valores únicos de una columna para filtros"""
        if self.df is None or self.df.empty or column not in self.df.columns:
            return []
        
        return sorted(self.df[column].dropna().unique().tolist())
    
    def export_to_excel(self, data: pd.DataFrame, filename: str = "datos_congreso.xlsx"):
        """Exporta datos a Excel"""
        try:
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                data.to_excel(writer, sheet_name='Datos', index=False)
                
                # Obtener el workbook y worksheet
                workbook = writer.book
                worksheet = writer.sheets['Datos']
                
                # Formato para headers
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Aplicar formato a headers
                for col_num, value in enumerate(data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Ajustar ancho de columnas
                for i, col in enumerate(data.columns):
                    max_length = max(
                        data[col].astype(str).map(len).max(),
                        len(str(col))
                    )
                    worksheet.set_column(i, i, min(max_length + 2, 50))
            
            return filename
        except Exception as e:
            st.error(f"Error al exportar a Excel: {str(e)}")
            return None
    
    def export_to_pdf(self, top_n: int = 10, filter_by_eje: Optional[str] = None, 
                      selected_columns: List[str] = None) -> io.BytesIO:
        """
        Exporta el ranking de ponencias a PDF
        
        Args:
            top_n: Número de mejores ponencias a incluir (por defecto 10)
            filter_by_eje: Filtrar por eje específico (opcional)
            selected_columns: Lista de columnas adicionales a incluir (Título, País, Institución, Origen)
            
        Returns:
            BytesIO objeto con el PDF generado
        """
        if selected_columns is None:
            selected_columns = []
        if self.df is None or self.df.empty:
            raise ValueError("No hay datos disponibles para exportar")
        
        if 'Puntaje' not in self.df.columns or 'Resultado' not in self.df.columns:
            raise ValueError("Los datos deben contener columnas 'Puntaje' y 'Resultado'")
        
        # Filtrar datos
        df_filtered = self.df.copy()

        # Solo incluir registros con Evaluar='SI' si la columna existe
        if 'Evaluar' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['Evaluar'].str.upper() == 'SI']

        # Filtrar por eje si se especifica
        if filter_by_eje and filter_by_eje in self.eje_values:
            df_filtered = df_filtered[df_filtered['Eje'] == filter_by_eje]

        # Filtrar solo los que tienen puntaje válido
        df_filtered = df_filtered[df_filtered['Puntaje'].notna()]

        # Ordenar por puntaje y tomar los top N
        df_top = df_filtered.nlargest(top_n, 'Puntaje')
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=30, leftMargin=30,
                              topMargin=50, bottomMargin=30)
        
        # Contenedor para elementos del PDF
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        
        # Título
        title_text = f"Ranking Top {top_n} - Convención de Suelos Pucallpa 2025"
        if filter_by_eje:
            title_text += f" - Eje {filter_by_eje}"
        
        elements.append(Paragraph(title_text, title_style))
        elements.append(Paragraph(f"Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Resumen estadístico
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=10
        )
        
        summary_text = f"""
        <b>Resumen del Ranking:</b><br/>
        • Total de ponencias evaluadas: {len(df_filtered)}<br/>
        • Puntaje promedio: {df_filtered['Puntaje'].mean():.2f}<br/>
        • Puntaje más alto: {df_filtered['Puntaje'].max():.2f}<br/>
        • Puntaje más bajo (Top {top_n}): {df_top['Puntaje'].min():.2f}
        """
        
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Preparar datos para la tabla - Construir columnas dinámicamente
        columns = ['Resultado', 'Nombres', 'Apellidos', 'Eje']
        columns.extend([col for col in selected_columns if col in df_top.columns])
        columns.append('Puntaje')
        
        # Mapeo de nombres de columnas para el PDF (traducción/renombrado)
        column_display_names = {
            'Resultado': 'Rank',
            'Nombres': 'Nombres',
            'Apellidos': 'Apellidos',
            'Eje': 'Eje',
            'Título': 'Título',
            'País': 'País',
            'Institución': 'Institución',
            'Origen': 'Origen',
            'Puntaje': 'Puntaje'
        }
        
        # Estilo para texto con wrapping
        text_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontSize=7.5,
            leading=10,
            wordWrap='CJK',
            splitLongWords=True,
            breakLongWords=True
        )
        
        # Estilo para el código de país con fondo
        country_style = ParagraphStyle(
            'CountryCode',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#FFFFFF'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Crear datos de la tabla
        # Headers con nombres traducidos
        table_headers = [column_display_names.get(col, col) for col in columns]
        table_data = [table_headers]
        
        for idx, row in df_top.iterrows():
            row_data = []
            for col in columns:
                value = row[col]
                # Formatear valores
                if col == 'Resultado':
                    # Obtener código del país
                    country_code = ''
                    if 'País' in row.index:
                        country_code = get_country_code(row['País'])
                    
                    # Crear formato con código de país y ranking
                    if country_code:
                        # Usar HTML con fondo de color para el código de país
                        rank_html = f'''
                        <para alignment="center">
                            <font size="7" color="#FFFFFF" backColor="#1f77b4"><b> {country_code} </b></font>
                            <br/>
                            <font size="9"><b>{int(value)}</b></font>
                        </para>
                        '''
                        row_data.append(Paragraph(rank_html, text_style))
                    else:
                        # Solo mostrar el ranking sin código de país
                        rank_html = f'<para alignment="center"><font size="9"><b>{int(value)}</b></font></para>'
                        row_data.append(Paragraph(rank_html, text_style))
                elif col == 'Puntaje':
                    row_data.append(f"{value:.2f}")
                elif col == 'Título':
                    # Usar Paragraph para permitir wrapping de texto largo
                    titulo_text = str(value)
                    row_data.append(Paragraph(titulo_text, text_style))
                elif col == 'Apellidos':
                    # Usar Paragraph para apellidos que pueden ser largos o compuestos
                    apellidos_text = str(value)
                    row_data.append(Paragraph(apellidos_text, text_style))
                elif col == 'Nombres':
                    # Usar Paragraph también para nombres compuestos
                    nombres_text = str(value)
                    row_data.append(Paragraph(nombres_text, text_style))
                elif col == 'Institución':
                    # Usar Paragraph para instituciones
                    inst_text = str(value)
                    row_data.append(Paragraph(inst_text, text_style))
                else:
                    row_data.append(str(value))
            table_data.append(row_data)
        
        # Calcular anchos de columna dinámicamente
        col_widths = []
        available_width = 7.5 * inch  # Ancho disponible en página A4
        
        # Anchos base por columna
        width_map = {
            'Resultado': 0.6 * inch,
            'Nombres': 1.1 * inch,      # Aumentado para nombres compuestos
            'Apellidos': 1.2 * inch,    # Aumentado para apellidos compuestos
            'Eje': 0.5 * inch,
            'Título': 2.5 * inch,
            'País': 0.8 * inch,
            'Institución': 1.6 * inch,  # Aumentado para instituciones largas
            'Origen': 0.8 * inch,
            'Puntaje': 0.7 * inch
        }
        
        # Calcular ancho total solicitado
        total_width = sum(width_map.get(col, 1*inch) for col in columns)
        
        # Ajustar proporcionalmente si excede el ancho disponible
        if total_width > available_width:
            scale_factor = available_width / total_width
            col_widths = [width_map.get(col, 1*inch) * scale_factor for col in columns]
        else:
            col_widths = [width_map.get(col, 1*inch) for col in columns]
        
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Estilo de la tabla
        table_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),  # Alineación superior para texto con wrap
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 1), (-1, -1), 4),
            ('RIGHTPADDING', (0, 1), (-1, -1), 4),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white]),
            
            # Alinear números al centro
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Resultado
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),  # Puntaje
            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),  # Resultado centrado verticalmente
            ('VALIGN', (-1, 1), (-1, -1), 'MIDDLE'),  # Puntaje centrado verticalmente
        ])
        
        # Destacar top 3
        if len(df_top) >= 1:
            table_style.add('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#FFD700'))  # Oro
        if len(df_top) >= 2:
            table_style.add('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#C0C0C0'))  # Plata
        if len(df_top) >= 3:
            table_style.add('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#CD7F32'))  # Bronce
        
        table.setStyle(table_style)
        elements.append(table)

        # Sección de Integrantes de la Comisión Póster
        elements.append(Spacer(1, 0.4*inch))

        # Título de la sección
        comision_title_style = ParagraphStyle(
            'ComisionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph("Integrantes de la Comisión Póster", comision_title_style))

        # Leer archivo de integrantes
        integrantes_path = "integrantes.xlsx"
        if os.path.exists(integrantes_path):
            try:
                df_integrantes = pd.read_excel(integrantes_path)

                # Estilo para los nombres de integrantes
                integrante_style = ParagraphStyle(
                    'IntegranteStyle',
                    parent=styles['Normal'],
                    fontSize=9,
                    alignment=TA_CENTER,
                    spaceAfter=4
                )

                # Agregar cada integrante
                for _, row in df_integrantes.iterrows():
                    nombre = str(row.iloc[0])  # Primera columna
                    elements.append(Paragraph(f"• {nombre}", integrante_style))

            except Exception as e:
                # Si hay error leyendo el archivo, agregar nota
                error_style = ParagraphStyle(
                    'ErrorStyle',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#999999'),
                    alignment=TA_CENTER
                )
                elements.append(Paragraph(f"(No se pudo cargar la lista de integrantes)", error_style))

        # Pie de página con información adicional
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph("Dashboard Convención de Suelos - Pucallpa 2025", footer_style))
        elements.append(Paragraph("Sistema de Análisis y Gestión de Pósteres", footer_style))

        # Añadir imagen de pie de página (ancho completo)
        elements.append(Spacer(1, 0.4*inch))
        footer_image_path = "images/footer.png"
        if os.path.exists(footer_image_path):
            # Obtener dimensiones reales de la imagen
            from PIL import Image as PILImage
            with PILImage.open(footer_image_path) as img:
                img_width, img_height = img.size
                aspect_ratio = img_height / img_width

            # Ancho completo de la página (de margen a margen)
            page_width = 7.5 * inch
            # Calcular altura manteniendo proporción, con un máximo
            calculated_height = page_width * aspect_ratio
            max_height = 1.0 * inch
            final_height = min(calculated_height, max_height)

            # Crear imagen con ancho completo y altura proporcional
            footer_img = Image(footer_image_path, width=page_width, height=final_height)
            elements.append(footer_img)

        # Construir PDF
        doc.build(elements)
        
        # Mover el puntero al inicio del buffer
        buffer.seek(0)
        return buffer