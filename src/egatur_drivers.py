"""Egatur: quién gasta, dónde y cómo llega.

Datos: data/processed/egatur_master_long.csv (5 tablas del INE en formato largo).
Las tablas no son homogéneas: cuatro son mensuales y la de motivo del viaje es
anual, así que nunca se suman entre sí ni se mezclan granularidades.

Uso: python src/egatur_drivers.py
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from svg_chart import AZUL, ROJO, barras

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "processed" / "egatur_master_long.csv"
IMG, OUT = ROOT / "docs" / "img", ROOT / "outputs"
IMG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

d = pd.read_csv(RAW)
d["mensual"] = d["periodo"].astype(str).str.fullmatch(r"\d{4}M\d{2}")
d["fecha"] = pd.to_datetime(d["periodo_parsed"], format="%Y-%m", errors="coerce")
print(f"1. cargado: {len(d):,} filas · {d.table_id.nunique()} tablas del INE")
print(f"   mensuales: {int(d.mensual.sum()):,} · anuales: {int((~d.mensual).sum()):,}")

fin = d[d.mensual].fecha.max()
ini = fin - pd.DateOffset(months=11)
ventana = f"{ini:%Y-%m} → {fin:%Y-%m}"
print(f"2. ventana de 12 meses: {ventana}")


def cuotas(table_id):
    g = d[(d.table_id == table_id) & d.mensual
          & d.dimension_value.ne("Total") & d.fecha.between(ini, fin)]
    s = g.groupby("dimension_value")["valor"].sum().sort_values(ascending=False)
    return s / s.sum() * 100


ETIQUETA_CCAA = {"09 Cataluña": "Cataluña", "05 Canarias": "Canarias",
                 "04 Balears, Illes": "Baleares", "01 Andalucía": "Andalucía",
                 "13 Madrid, Comunidad de": "Madrid",
                 "10 Comunitat Valenciana": "C. Valenciana",
                 "Otras Comunidades Autónomas": "Otras"}

ccaa = cuotas(10839)
print("\n3. cuota por CCAA:")
print(ccaa.round(1).to_string())
barras(
    [(ETIQUETA_CCAA.get(i, i), v, AZUL) for i, v in ccaa.items()],
    "El gasto turístico está repartido, no concentrado",
    IMG / "egatur-ccaa.svg",
    subtitulo=f"% del gasto por comunidad autónoma · {ventana}",
    formato="{:.1f}", sufijo="%")

pais = cuotas(10838)
print("\n4. cuota por país de residencia:")
print(pais.round(1).to_string())
barras(
    [(i, v, ROJO if v > 50 else AZUL) for i, v in pais.items()],
    "La mitad del gasto no es de los cuatro mercados clásicos",
    IMG / "egatur-pais.svg",
    subtitulo=f"% del gasto por país de residencia · {ventana}",
    formato="{:.1f}", sufijo="%")

via = cuotas(10828)
print("\n5. cuota por vía de acceso:")
print(via.round(1).to_string())
barras(
    [(i, v, ROJO if v > 50 else AZUL) for i, v in via.items()],
    "Nueve de cada diez euros entran por avión",
    IMG / "egatur-via.svg",
    subtitulo=f"% del gasto por vía de acceso · {ventana}",
    formato="{:.1f}", sufijo="%")

# ---------- tendencia y motivo ----------
t = d[(d.table_id == 10838) & (d.dimension_value == "Total") & d.mensual]
en25 = t[(t.fecha.dt.year == 2025) & (t.fecha.dt.month <= 7)]["valor"].sum()
en26 = t[t.fecha.dt.year == 2026]["valor"].sum()
print(f"\n6. ene-jul 2025 = {en25:,.0f} · ene-jul 2026 = {en26:,.0f} · "
      f"variación {(en26 / en25 - 1) * 100:+.1f}%")

mot = d[(d.table_id == 23995) & (d.periodo.astype(str) == "2025")
        & d.dimension_value.ne("Total")]
mot = mot.groupby("dimension_value")["valor"].sum().sort_values(ascending=False)
print("\n7. motivo del viaje 2025 (% del gasto):")
print((mot / mot.sum() * 100).round(1).head(6).to_string())

pd.DataFrame({"ccaa": ccaa, "pais": pais}).to_csv(OUT / "share_by_geo.csv")
(mot / mot.sum() * 100).round(2).to_csv(OUT / "share_by_motive_2025.csv")
