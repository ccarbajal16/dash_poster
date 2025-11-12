# Dashboard de Análisis de Datos de Convención Internacional de Suelos - Pucallpa 2025

## 📋 Descripción

Dashboard interactivo desarrollado en Python con Streamlit para la gestión y análisis de la base de datos de la III Convención Internacional de Suelos y XX Congreso Peruano de la Ciencia del Suelo. Permite visualizar estadísticas, detectar duplicados y generar reportes de las ponencias de pósteres.

## ✨ Características Principales

- 🏠 **Panel Principal**: Métricas generales, resumen estadístico y rankings de evaluación
- 📈 **Análisis por Eje**: Distribución de ponencias por eje temático (E1-E7)
- 👥 **Gestión de Duplicados**: Detección de nombres repetidos y análisis por eje
- 📊 **Visualizaciones Interactivas**: Gráficos pie, barras e histogramas personalizables
- 🔍 **Filtros Avanzados**: Búsqueda por País, Eje, Institución, Presentación, Ponencia, Puntaje y Ranking
- 🏆 **Sistema de Evaluación**: Cálculo automático de Puntaje y Rankings (Resultado) con actualización dinámica
- 📥 **Exportación**: Datos y gráficos en múltiples formatos (CSV, Excel, PNG)

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Streamlit 1.51.0
- **Procesamiento de Datos**: Pandas 2.3.3, NumPy 2.3.4
- **Visualizaciones**: Plotly 6.4.0
- **Exportación**: OpenPyXL 3.1.5, XlsxWriter 3.2.9
- **Generación de PDFs**: ReportLab 4.4.4

## 📦 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

   ```bash
   # Si tienes el proyecto en un repositorio
   git clone https://github.com/ccarbajal16/dash_poster.git
   cd dash_poster
   ```
2. **Crear un entorno virtual (recomendado)**

   ```bash
   python -m venv venv

   # En Windows
   venv\Scripts\activate

   # En macOS/Linux
   source venv/bin/activate
   ```
3. **Instalar dependencias**

   ```bash
   pip install -r requirements.txt
   ```
4. **Verificar que el archivo de datos esté presente**

   - Asegúrate de que el archivo `bd_congreso.csv` esté en el directorio raíz del proyecto
   - El archivo debe contener las columnas requeridas: Id, Nombres, Apellidos, Título, Eje, País, etc.

## 🚀 Ejecución

### Ejecutar la aplicación

```bash
streamlit run app.py
```

### Acceder al dashboard

1. Después de ejecutar el comando, se abrirá automáticamente tu navegador web
2. Si no se abre automáticamente, ve a: `http://localhost:8501`
3. El dashboard estará listo para usar

## 📊 Uso del Dashboard

### Navegación

El dashboard cuenta con 5 páginas principales accesibles desde el menú lateral:

1. **🏠 Página Principal**

   - Métricas generales del congreso (ponencias, países, instituciones)
   - Distribución por eje temático (E1-E7)
   - Top países e instituciones participantes
   - Estadísticas de presentación
   - **Evaluación y Rankings**:
     - Distribución de puntajes con histograma
     - Top 10 ponencias ordenadas por puntaje
     - Métricas de puntaje (promedio, máximo, mínimo)
2. **📈 Análisis por Eje**

   - Análisis detallado de cada eje temático (E1-E7)
   - Gráficos comparativos por eje
   - Estadísticas por eje seleccionado
   - Distribución de países e instituciones por eje
3. **👥 Gestión de Duplicados**

   - Detección automática de nombres duplicados
   - Análisis de duplicados por eje
   - Lista detallada con información completa
   - Visualización de registros duplicados
4. **📊 Visualizaciones**

   - Gráficos interactivos personalizables
   - Múltiples tipos: barras, pie, área
   - Exportación de gráficos en PNG
   - Visualizaciones por eje con colores distintivos
5. **🔍 Filtros y Búsqueda**

   - Filtros múltiples por Eje, País, Institución
   - Filtros por estado de Presentación (Presentó: SI/NO)
   - Filtros por tipo de Ponencia (Ponencia Oral: SI/NO)
   - **Nuevos filtros de evaluación**:
     - Rango de Puntaje (0.43 - 0.97)
     - Rango de Ranking/Resultado (1 - 22)
   - Búsqueda de texto libre
   - Exportación de datos filtrados

### Funcionalidades de Exportación

- **CSV**: Datos filtrados en formato CSV
- **Excel**: Reportes formateados en Excel
- **PNG**: Gráficos en alta resolución

## 📁 Estructura del Proyecto

```
dash_poster/
├── app.py                    # Aplicación principal de Streamlit
├── data_processor.py         # Módulo de procesamiento de datos
├── requirements.txt          # Dependencias del proyecto
├── bd_congreso.csv          # Base de datos del congreso
├── integrantes.xlsx         # Listado de integrantes de comisiones
├── README.md                # Este archivo
├── images/                  # Recursos visuales para el dashboard
│   ├── logo_convencion.png  # Logo del congreso
│   └── footer.png           # Pie de página para PDFs
├── Photos/                  # Galería de fotos del congreso
│   ├── foto1.png
│   ├── foto2.png
│   └── foto3.png
└── venv/                    # Entorno virtual de Python (no incluir en git)
```

## 🔧 Configuración

### Personalización de Colores

Los colores del dashboard están definidos en el archivo `app.py` para los 7 ejes temáticos:

- **E1**: Azul (#1f77b4)
- **E2**: Verde (#2ca02c)
- **E3**: Naranja (#ff7f0e)
- **E4**: Púrpura (#9467bd)
- **E5**: Rojo (#d62728)
- **E6**: Cian (#17becf)
- **E7**: Rosa (#e377c2)

### Modificar Fuente de Datos

Para usar un archivo CSV diferente, modifica la ruta en `data_processor.py`:

```python
processor = DataProcessor(csv_path="tu_archivo.csv")
```

## 📋 Formato de Datos Requerido

El archivo CSV debe contener las siguientes columnas:

| Columna       | Tipo   | Descripción                                  | Requerido |
| ------------- | ------ | --------------------------------------------- | --------- |
| Id            | int    | Identificador único                          | Sí       |
| Nombres       | string | Nombres del participante                      | Sí       |
| Apellidos     | string | Apellidos del participante                    | Sí       |
| Título       | string | Título de la ponencia                        | Sí       |
| Institución  | string | Institución de procedencia                   | Sí       |
| INST          | string | Abreviatura de la institución                | No        |
| Origen        | string | Ciudad/Región de origen                      | No        |
| País         | string | País de procedencia                          | Sí       |
| Eje           | string | Eje temático (E1-E7)                         | Sí       |
| Ponencia      | string | Ponencia oral (SI/NO)                         | No        |
| Presentó     | string | Estado de presentación (SI/NO)               | No        |
| Calificativo  | int    | Puntuación de 0-100                          | No*       |
| Puntaje       | float  | Calculado automáticamente (Calificativo/100) | No        |
| Resultado     | int    | Ranking calculado automáticamente            | No        |
| Observaciones | string | Notas adicionales                             | No        |

**Nota importante sobre columnas calculadas:**

- `Puntaje` se calcula automáticamente como `Calificativo / 100`
- `Resultado` se calcula automáticamente usando ranking denso (sin gaps) basado en `Puntaje`
- Estas columnas se actualizan dinámicamente cada vez que se carga el dashboard
- El mejor puntaje obtiene el ranking 1, el segundo mejor obtiene 2, etc.

## 🐛 Solución de Problemas

### Error: "No se encontró el archivo bd_congreso.csv"

- Verifica que el archivo CSV esté en el directorio raíz del proyecto
- Asegúrate de que el nombre del archivo sea exactamente `bd_congreso.csv`

### Error de dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Puerto ocupado

Si el puerto 8501 está ocupado, usa:

```bash
streamlit run app.py --server.port 8502
```

## 🏆 Sistema de Evaluación y Rankings

### Cálculo Automático

El dashboard incluye un sistema de evaluación automática que:

1. **Calcula el Puntaje** a partir del Calificativo:

   ```python
   Puntaje = Calificativo / 100
   ```

   - Rango: 0.00 a 1.00 (basado en calificativo de 0-100)
2. **Genera Rankings (Resultado)** basados en el Puntaje:

   - Utiliza el método de ranking "denso" (sin gaps)
   - El mejor puntaje recibe el ranking 1
   - En caso de empate, todos obtienen el mismo ranking
   - El siguiente ranking continúa secuencialmente (sin saltos)

### Ejemplo de Rankings

| Puntaje | Resultado | Explicación                      |
| ------- | --------- | --------------------------------- |
| 0.97    | 1         | Mejor puntaje                     |
| 0.96    | 2         | Segundo mejor (pueden ser varios) |
| 0.95    | 3         | Tercer mejor (pueden ser varios)  |
| 0.94    | 4         | Cuarto mejor                      |

### Actualización Dinámica

- Los rankings se recalculan automáticamente cada vez que se carga el dashboard
- Si modificas los valores de `Calificativo` en el CSV, los cambios se reflejan inmediatamente
- No es necesario ejecutar ningún script adicional

## 📈 Rendimiento

- El dashboard utiliza caché de Streamlit para optimizar la carga de datos
- Optimizado para el conjunto actual de 146 registros
- Soporta eficientemente archivos CSV de hasta 10,000 registros
- Los cálculos de Puntaje y Resultado se realizan en tiempo real al cargar los datos
- Para archivos más grandes, considera usar una base de datos

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:

- Crear un issue en el repositorio
- Contactar al equipo de desarrollo del INIA

## 📝 Changelog

### Versión 2.0 (Octubre 2024)

**Nuevas Características:**

- ✅ Soporte para 7 ejes temáticos (E1-E7) en lugar de 3
- ✅ Sistema de evaluación automática con cálculo de Puntaje y Resultado
- ✅ Sección de Rankings en la página principal con Top 10 ponencias
- ✅ Filtros por estado de Presentación (Presentó: SI/NO)
- ✅ Filtros por tipo de Ponencia Oral (SI/NO)
- ✅ Filtros por rango de Puntaje y Resultado
- ✅ Histograma de distribución de puntajes
- ✅ Actualización dinámica de rankings al modificar datos

**Mejoras:**

- 🔄 Cálculo automático de Puntaje a partir de Calificativo
- 🔄 Ranking denso sin gaps (1, 2, 3, 4...) en lugar de (1, 17, 18...)
- 🔄 Colores distintivos para los 7 ejes temáticos
- 🔄 Mejor visualización de estadísticas de presentación
- 🔄 Optimización del procesamiento de datos

### Versión 1.0 (Inicial)

- Implementación base del dashboard con 3 ejes temáticos
- Sistema de filtros básico
- Detección de duplicados
- Visualizaciones interactivas

---

**Desarrollado para la Convención de Suelos 2025 - INIA**
