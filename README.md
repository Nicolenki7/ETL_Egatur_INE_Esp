# 📊 ETL Egatur INE España

**Data Pipeline (ETL) | Encuesta de Gasto Turístico | Python/Pandas | Airflow + Docker + PostgreSQL**

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas)](https://pandas.pydata.org/)
[![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apacheairflow)](https://airflow.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Overview

Data Pipeline (ETL) para la **Encuesta de Gasto Turístico (EGATUR)** del Instituto Nacional de Estadística (INE) de España. Unifica, limpia y transforma los datos históricos de gasto turístico utilizando Python/Pandas.

Proyecto base para una pipeline completa con **Airflow, Docker y PostgreSQL** para un dashboard en Power BI.

---

## 💼 Business Impact

- **Data Unification**: Consolidates historical tourist spending data from multiple sources
- **Data Quality**: Cleans and validates INE survey data
- **Analytics Ready**: Transforms raw data for BI dashboard consumption
- **Automation Foundation**: Base for orchestrated ETL with Airflow

---

## 🛠️ Technical Stack

| Category | Technologies |
| :--- | :--- |
| **Language** | Python |
| **Data Processing** | Pandas, NumPy |
| **Orchestration** | Apache Airflow (planned) |
| **Containerization** | Docker |
| **Database** | PostgreSQL |
| **BI** | Power BI (planned) |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  EGATUR ETL PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SOURCE: INE Spain                                          │
│  └─→ EGATUR survey data (Excel/CSV files)                   │
│      - Tourist spending by country, purpose, region         │
│                                                              │
│  EXTRACT                                                    │
│  └─→ Download historical data from INE                      │
│                                                              │
│  TRANSFORM (Python/Pandas)                                  │
│  └─→ Unify formats, clean data, validate                    │
│      - Null handling, type correction                       │
│      - Currency normalization (EUR)                         │
│      - Date standardization                                 │
│                                                              │
│  LOAD                                                       │
│  └─→ PostgreSQL database                                    │
│      - Structured tables for BI consumption                 │
│                                                              │
│  ORCHESTRATION (Airflow - planned)                          │
│  └─→ Scheduled ETL jobs, monitoring, alerts                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Key Features

### Data Unification
- Multiple historical files consolidated
- Consistent schema across time periods

### Data Cleaning
- Null value handling
- Type correction and validation
- Currency normalization (EUR)

### Pipeline Architecture
- Modular ETL design
- Docker containerization ready
- Airflow DAG structure (planned)

---

## 🔧 Setup & Installation

```bash
# Clone the repository
git clone https://github.com/Nicolenki7/ETL_Egatur_INE_Esp.git
cd ETL_Egatur_INE_Esp

# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline
python src/etl_pipeline.py

# (Optional) Run with Docker
docker-compose up
```

---

## 🔗 Links

| Resource | URL |
| :--- | :--- |
| **Repository** | https://github.com/Nicolenki7/ETL_Egatur_INE_Esp |
| **Data Source** | [INE - EGATUR](https://www.ine.es/dyngs/INEbase/es/categoria.htm?c=Estadistica_P&cid=1254734710106) |

---

## 📝 Resumen en Español

Pipeline ETL para la Encuesta de Gasto Turístico (EGATUR) del INE. Unifica, limpia y transforma datos históricos de gasto turístico en España usando Python/Pandas. Proyecto base para pipeline completa con Airflow, Docker y PostgreSQL para dashboard en Power BI.

---

## 📄 License

MIT License

---

## 👤 Author

**Nicolás Zalazar** | Senior Data Engineer

- GitHub: [@Nicolenki7](https://github.com/Nicolenki7)
- LinkedIn: [nicolas-zalazar-63340923a](https://www.linkedin.com/in/nicolas-zalazar-63340923a)

---

*Last Updated: March 2026*
