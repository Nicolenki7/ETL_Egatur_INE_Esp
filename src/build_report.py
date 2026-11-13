"""Construye docs/report.html de Egatur a partir del master en formato largo.

Uso: python src/build_report.py
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from report import escribir, num

ROOT = pathlib.Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT / "data" / "processed" / "egatur_master_long.csv")
d["mensual"] = d["periodo"].astype(str).str.fullmatch(r"\d{4}M\d{2}")
d["fecha"] = pd.to_datetime(d["periodo_parsed"], format="%Y-%m", errors="coerce")

fin = d[d.mensual].fecha.max()
ini = fin - pd.DateOffset(months=11)
v = d[d.mensual & d.dimension_value.ne("Total") & d.fecha.between(ini, fin)].copy()
v["trim"] = v.fecha.dt.to_period("Q").astype(str)

ETIQUETA = {"09 Cataluña": "Cataluña", "05 Canarias": "Canarias", "04 Balears, Illes": "Baleares",
            "01 Andalucía": "Andalucía", "13 Madrid, Comunidad de": "Madrid",
            "10 Comunitat Valenciana": "C. Valenciana", "Otras Comunidades Autónomas": "Otras"}

filas = []
for tabla, grupo, etiqueta in ((10839, "ccaa", ETIQUETA), (10838, "pais", {}), (10828, "via", {})):
    g = v[v.table_id == tabla]
    for (t, k), sub in g.groupby(["trim", "dimension_value"]):
        total = g[g.trim == t]["valor"].sum()
        filas.append({"a": t, "g": grupo, "k": etiqueta.get(k, k),
                      "v": round(float(sub["valor"].sum() / total * 100), 1), "u": "%"})


def cuota(tabla, etiqueta=None):
    g = v[v.table_id == tabla]
    s = g.groupby("dimension_value")["valor"].sum().sort_values(ascending=False)
    return (s / s.sum() * 100).rename(index=lambda i: (etiqueta or {}).get(i, i))


ccaa = cuota(10839, ETIQUETA)
tabla_ccaa = [[k, f"{num(x, 1)} %"] for k, x in ccaa.items()]
via = cuota(10828)

escribir(
    ROOT / "docs" / "report.html",
    eyebrow="Turismo · Egatur (INE)",
    titulo="Egatur: dónde se queda el gasto turístico",
    pregunta=("España recibe turismo de muchos mercados y no todos dejan el mismo dinero ni llegan "
              "por la misma puerta. La pregunta es de dónde viene el gasto, dónde se queda y por "
              "dónde entra, porque cada respuesta apunta a una decisión distinta."),
    kpis=[("Ventana", f"{ini:%Y-%m} → {fin:%Y-%m}", "12 meses"),
          ("Comunidades con datos", num(d[d.table_id == 10839].dimension_value.nunique()), "tabla 10839"),
          ("Cuota del aeropuerto", f"{num(via.get('Aeropuerto', 0), 1)} %", "vía de acceso"),
          ("Cuota de Cataluña", f"{num(ccaa.iloc[0], 1)} %", "mayor comunidad")],
    filtros=["todos"] + sorted(v.trim.unique()),
    filtro_etiqueta="Trimestre",
    graficos=[
        {"id": "ccaa", "grupo": "ccaa", "titulo": "Cuota por comunidad autónoma",
         "subtitulo": "% del gasto de la tabla en la ventana de 12 meses", "unidad": "%"},
        {"id": "pais", "grupo": "pais", "titulo": "Cuota por país de residencia",
         "subtitulo": "más de la mitad del gasto queda agrupado en «Resto del Mundo»", "unidad": "%"},
        {"id": "via", "grupo": "via", "titulo": "Cuota por vía de acceso",
         "subtitulo": "nueve de cada diez euros entran por avión", "unidad": "%"},
    ],
    filas=filas,
    tabla={"titulo": "Gasto por comunidad autónoma", "subtitulo": "ventana completa de 12 meses",
           "cabeceras": ["Comunidad", "Cuota"], "filas": tabla_ccaa},
    metodo=["Se usan solo las tablas mensuales y una ventana de 12 meses cerrada en el último mes disponible.",
            "Cuota = gasto del grupo / gasto total de esa misma tabla; nunca se suman tablas distintas entre sí.",
            "La tabla de motivo del viaje es anual (23995) y se lee aparte: sumarla con las mensuales duplicaría el gasto.",
            "El CSV no declara unidades, así que se trabaja con cuotas y no con importes."],
    limitaciones=["La ventana llega hasta 2026-07, el último periodo de la extracción, no necesariamente el último del INE.",
                  "«Resto del Mundo» agrupa más de la mitad del gasto: sin desagregar, no se sabe qué mercados crecen.",
                  "El motivo del viaje solo existe por año, así que no se puede cruzar con el trimestre.",
                  "Los trimestres de los extremos de la ventana están incompletos (2025Q3 solo tiene agosto y septiembre).",
                  "Sin unidades verificables en el archivo no hay importes, solo porcentajes."],
    fuente="data/processed/egatur_master_long.csv (2.881 filas, 5 tablas del INE)",
    metodo_sub="Una fila por dimensión y periodo; cada corte filtra por granularidad antes de agregar.",
    lim_sub="Lo que el INE no permite afirmar con estas cinco tablas.")
print("docs/report.html:", (ROOT / "docs" / "report.html").stat().st_size, "bytes")
