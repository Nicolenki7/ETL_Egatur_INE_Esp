# 🧠 Evaluación del rendimiento regional y propuestas de mejora del sistema de datos del INE  

**Autor:** Nicolas  
**Última actualización:** noviembre 2025  

---

## 📘 Descripción general  

Este proyecto analiza la evolución del **gasto turístico en España** utilizando los datos abiertos del **Instituto Nacional de Estadística (INE)**, específicamente de la encuesta **Egatur (Encuesta de Gasto Turístico)**.  

El objetivo principal fue **evaluar el rendimiento económico regional**, detectar inconsistencias en los datos oficiales y proponer **mejoras en los procesos de ingeniería y automatización de datos** aplicables al propio sistema del INE.

---

## 🧩 Objetivos del proyecto  

1.  **Construir un pipeline ETL completo** desde la descarga de archivos CSV del INE hasta la visualización final en Power BI.  
2.  **Corregir y limpiar datos inconsistentes** en las variables de gasto y procedencia.  
3.  **Analizar la distribución regional del gasto turístico**, destacando las comunidades con mayor rendimiento económico.  
4.  **Desarrollar dashboards interactivos** para la toma de decisiones.  
5.  **Proponer soluciones técnicas y de negocio** que optimicen la recopilación y explotación de datos turísticos.

---

## 🗂️ Estructura del proyecto

ETL_Egatur_INE_Esp/ │ ├── data/ │ ├── egatur_original.csv │ ├── egatur_limpio.csv │ └── comunidades_coordenadas.csv │ ├── sql/ │ ├── crear_vistas.sql │ ├── egatur_gasto_por_comunidad.sql │ └── egatur_con_coordenadas.sql │ ├── notebooks/ │ ├── limpieza_egatur.ipynb │ ├── analisis_exploratorio.ipynb │ └── automatizacion_carga.ipynb │ ├── dashboard/ │ └── powerbi_dashboard.pbix │ └── README.md

---

## ⚙️ Proceso ETL

### 1️⃣ **Extracción**

Los archivos fueron descargados directamente del portal del **INE**, en formato CSV.  
Se incluyeron variables clave sobre:
* Comunidad autónoma de destino.  
* Tipo de turista (nacional o extranjero).  
* Gasto medio diario y total.  
* Periodo temporal (año, mes).  

### 2️⃣ **Transformación (Python & SQL)**

El procesamiento inicial se realizó en **Python (pandas, numpy)**:
* Eliminación de duplicados y valores nulos.  
* Normalización de nombres de comunidades autónomas.  
* Conversión de unidades de gasto a millones de euros.  

Posteriormente, se trabajó en **PostgreSQL** para reforzar la integridad de los datos.

#### 🔧 **Ejemplo de Creación de Vista en SQL**

```sql
CREATE VIEW egatur_con_coordenadas AS
SELECT
    e.periodo,
    e.comunidad_autonoma,
    e.gasto_total,
    c.latitud,
    c.longitud
FROM egatur_datos_maestros e
JOIN comunidades_coordenadas c
ON e.comunidad_autonoma_limpia = c.comunidad_autonoma;

```

⚠️ **Inconsistencia de Datos Corregida**

Durante la limpieza, se identificó que el campo `comunidad_autonoma` contenía valores **“Desconocido”**. Se observó que el orden de los registros seguía un patrón alfabético, lo que permitió **reasignar correctamente cada valor** a su comunidad correspondiente mediante lógica aplicada en SQL.

### 3️⃣ **Carga (Power BI)**

El modelo final fue conectado directamente a la base de datos **PostgreSQL**.  
**Power BI** permitió:
* Crear un mapa interactivo con coordenadas.
* Generar gráficos de barras y tendencias temporales.
* Añadir filtros dinámicos por año y región.

---

## 📊 Visualizaciones clave

| Visualización | Descripción | Objetivo |
| :--- | :--- | :--- |
| **Mapa de gasto turístico** | Representa el gasto total por comunidad autónoma. | Mostrar la distribución geográfica del impacto económico. |
| **Tendencia temporal** | Gráfico de líneas del gasto turístico total entre los últimos años. | Analizar la evolución y recuperación post-pandemia. |
| **Ranking regional** | Tabla y gráfico de barras ordenado del gasto por CCAA. | Identificar el peso económico y las regiones líderes. |

---

## 🔍 Insights principales

* El **mercado nacional** representa el mayor gasto turístico total en España, superando al extranjero.
* Las comunidades con mayor rendimiento económico son **Cataluña, Andalucía, Canarias y la Comunidad Valenciana**.
* Una porción significativa del gasto aparece como **“procedencia desconocida”**, lo que reduce la precisión estadística y dificulta el análisis territorial.
* La evolución muestra una **recuperación sostenida del gasto** tras la pandemia, con un crecimiento anual constante.

---

## 💡 Propuestas de mejora al INE

| Área | Propuesta | Beneficio |
| :--- | :--- | :--- |
| **Flujo de Datos** | Automatizar procesos ETL internos (e.g., con **n8n** o **Airflow**). | Reducir errores humanos y garantizar la puntualidad de los datos. |
| **Calidad de Datos** | Implementar validación geográfica automatizada (lat/long). | Minimizar registros “desconocidos” y mejorar la precisión territorial. |
| **Estandarización** | Definir taxonomías fijas para comunidades y tipos de turista. | Simplificar la limpieza de datos y la interoperabilidad. |
| **Monitoreo** | Generar **Data Quality Reports** automáticos. | Identificar inconsistencias y duplicados en tiempo real. |
| **BI** | Fomentar la publicación de **dashboards abiertos** y actualizables. | Mejorar la transparencia y la inteligencia de negocio colaborativa. |

---

## 🧮 Stack tecnológico

| Categoría | Herramienta | Uso Principal |
| :--- | :--- | :--- |
| **Lenguaje** | Python (Pandas, Numpy) | Transformación, Limpieza de datos. |
| **Base de datos** | PostgreSQL | Almacenamiento, Integridad y Vistas. |
| **Visualización** | Power BI | Desarrollo de dashboards interactivos. |
| **Control de versiones** | Git / GitHub | Gestión de código fuente del proyecto. |
| **Automatización (Propuesta)** | n8n, Airflow | Optimización del pipeline ETL. |

---

## 🚀 Impacto y aplicabilidad

El proyecto demuestra cómo un pipeline de ingeniería de datos bien estructurado puede transformar un conjunto de datos desordenado en **información estratégica** para la planificación turística.

La combinación de análisis técnico y visión de negocio permite ofrecer **recomendaciones orientadas al crecimiento del turismo** nacional e internacional y a la optimización del gasto público destinado a promoción turística.

---

## 📁 Repositorio y recursos

* 🔗 **Repositorio GitHub:** `ETL_Egatur_INE_Esp`
* 📊 **Dashboard Power BI:** Incluido en la carpeta `/dashboard/powerbi_dashboard.pbix`
* 🧾 **Informe completo:** “Evaluación del rendimiento regional y propuestas de mejora del sistema de datos del INE”

---

## 🏁 Conclusión

El análisis no solo evidencia la **fortaleza del turismo nacional** como motor económico, sino también la necesidad de una gestión más precisa y automatizada de los datos oficiales.

A través del uso de Python, SQL y Power BI, este proyecto ofrece una **hoja de ruta** para fortalecer el ecosistema informativo del turismo en España, combinando técnica, inteligencia de negocio e innovación.
