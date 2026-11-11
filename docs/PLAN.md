# Plan de ejecucion

## Estado actual
- 5 tablas del INE (separador punto y coma + BOM) normalizadas a data/processed/egatur_master_long.csv (2.881 filas).
- CI de contrato de datos, notebook de analisis, Power BI (.pbix) e informe regional.
- Workflow de ingesta con validacion de esquema en automation/n8n/.

## Proximos pasos
1. Extraer el ETL del notebook a src/etl.py con CLI e idempotencia (mismo input, mismo hash).
2. Filtrar por tipo_dato antes de agregar: hoy el analisis mezcla Dato base con variaciones.
3. Mover .pbix y .docx a docs/ y dejar la raiz limpia.
4. Test de idempotencia: dos ejecuciones consecutivas deben producir el mismo resultado.

## Criterio de aceptacion
- python -m src.etl regenera el master y el hash no cambia.

## Riesgos
- El INE cambia nombres de tabla y formato sin avisar: el workflow falla a proposito en ese caso.
