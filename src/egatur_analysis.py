"""
EGATUR / INE — clean public tables and produce portfolio-ready charts + insights.
Source: https://www.ine.es (jaxiT3 csv_bdsc tables).
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIG = ROOT / "outputs" / "figures"
INSIGHTS = ROOT / "outputs" / "insights.md"

PROCESSED.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="talk", palette="deep")
plt.rcParams["figure.dpi"] = 140
plt.rcParams["savefig.bbox"] = "tight"
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11


def parse_total(series: pd.Series) -> pd.Series:
    s = (
        series.astype(str)
        .str.strip()
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"": np.nan, "nan": np.nan, "-": np.nan, "..": np.nan})
    )
    return pd.to_numeric(s, errors="coerce")


def parse_period(period: str) -> pd.Period | pd.NaT:
    period = str(period).strip()
    m = re.fullmatch(r"(\d{4})M(\d{2})", period)
    if m:
        return pd.Period(f"{m.group(1)}-{m.group(2)}", freq="M")
    m = re.fullmatch(r"(\d{4})", period)
    if m:
        return pd.Period(m.group(1), freq="Y")
    return pd.NaT


def load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", encoding="utf-8", dtype=str)
    df.columns = [c.strip().replace("  ", " ") for c in df.columns]
    return df


def tidy_common(df: pd.DataFrame, dim_col: str, table_id: str, table_name: str) -> pd.DataFrame:
    # normalize possible column names
    rename = {}
    for c in df.columns:
        cl = c.lower()
        if "tipo de dato" in cl:
            rename[c] = "tipo_dato"
        elif "periodo" in cl:
            rename[c] = "periodo"
        elif c.lower() == "total":
            rename[c] = "total"
        elif "gastos y duración" in cl or "gastos y duracion" in cl:
            rename[c] = "indicador"
    df = df.rename(columns=rename)
    if dim_col not in df.columns:
        # fuzzy find
        for c in df.columns:
            if dim_col.split()[0].lower() in c.lower() or dim_col.lower() in c.lower():
                df = df.rename(columns={c: dim_col})
                break
    out = df.copy()
    out["valor"] = parse_total(out["total"])
    out["periodo_parsed"] = out["periodo"].map(parse_period)
    out["table_id"] = table_id
    out["table_name"] = table_name
    out["dimension"] = dim_col
    out["dimension_value"] = out[dim_col].astype(str).str.strip()
    if "indicador" not in out.columns:
        out["indicador"] = "Gasto total"
    if "tipo_dato" not in out.columns:
        out["tipo_dato"] = "Dato base"
    keep = [
        "table_id",
        "table_name",
        "dimension",
        "dimension_value",
        "indicador",
        "tipo_dato",
        "periodo",
        "periodo_parsed",
        "valor",
    ]
    return out[keep].dropna(subset=["valor"])


def build_master() -> dict[str, pd.DataFrame]:
    specs = [
        ("10838.csv", "País de residencia", "10838", "Gasto por país de residencia"),
        ("10839.csv", "Comunidades autónomas", "10839", "Gasto por CCAA destino"),
        ("10828.csv", "Via de acceso", "10828", "Gasto por vía de acceso"),
        ("23995.csv", "Motivo del viaje", "23995", "Gasto por motivo del viaje"),
    ]
    tables = {}
    frames = []
    for file_name, dim, tid, tname in specs:
        raw = load_table(RAW / file_name)
        # fix CCAA column spacing
        if dim == "Comunidades autónomas" and "Comunidades autónomas" not in raw.columns:
            for c in raw.columns:
                if "Comunidades" in c:
                    raw = raw.rename(columns={c: "Comunidades autónomas"})
                    break
        if dim == "Via de acceso" and "Via de acceso" not in raw.columns:
            for c in raw.columns:
                if "acceso" in c.lower():
                    raw = raw.rename(columns={c: "Via de acceso"})
                    break
        tidy = tidy_common(raw, dim, tid, tname)
        # keep base totals indicator when present
        if tidy["indicador"].nunique() > 1:
            tidy = tidy[tidy["indicador"].str.contains("Gasto total", case=False, na=False)]
        tidy = tidy[tidy["tipo_dato"].str.contains("Dato base", case=False, na=True)]
        tables[tid] = tidy
        frames.append(tidy)

    # expenditure items (13938) — hierarchical; keep Nivel 1 rows for overview
    exp = load_table(RAW / "13938.csv")
    exp.columns = [c.strip() for c in exp.columns]
    exp["valor"] = parse_total(exp["Total"])
    exp["periodo_parsed"] = exp["Periodo"].map(parse_period)
    exp = exp[exp["Tipo de dato"].astype(str).str.contains("Dato base", case=False, na=True)]
    # Nivel 1 only for clean chart (Gasto total / main chapters)
    n1 = exp[exp["Partidas de gasto: Nivel 2"].isna() | (exp["Partidas de gasto: Nivel 2"].astype(str).str.strip() == "")].copy()
    n1["dimension_value"] = n1["Partidas de gasto: Nivel 1"].astype(str).str.strip()
    n1 = n1.assign(
        table_id="13938",
        table_name="Partidas de gasto",
        dimension="Partida nivel 1",
        indicador="Gasto",
        tipo_dato="Dato base",
        periodo=n1["Periodo"],
    )
    tables["13938"] = n1[
        ["table_id", "table_name", "dimension", "dimension_value", "indicador", "tipo_dato", "periodo", "periodo_parsed", "valor"]
    ].dropna(subset=["valor"])
    frames.append(tables["13938"])

    master = pd.concat(frames, ignore_index=True)
    master.to_csv(PROCESSED / "egatur_master_long.csv", index=False)
    return tables


def latest_month(df: pd.DataFrame) -> pd.Period:
    periods = df["periodo_parsed"].dropna()
    months = [p for p in periods if getattr(p, "freqstr", "") in ("M", "M-DEC") or str(p.freq).startswith("M")]
    if not months:
        # fallback: any
        return periods.max()
    return max(months)


def chart_trend_total(countries: pd.DataFrame) -> Path:
    d = countries[
        (countries["dimension_value"].str.lower() == "total")
        & (countries["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False))
    ].copy()
    d = d.sort_values("periodo_parsed")
    # last 36 months
    d = d.tail(36)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(d["periodo_parsed"].astype(str), d["valor"], marker="o", linewidth=2.2, markersize=4, color="#0B6E4F")
    ax.fill_between(range(len(d)), d["valor"], alpha=0.15, color="#0B6E4F")
    ax.set_title("EGATUR — Total tourist spending in Spain (last 36 months)")
    ax.set_xlabel("Period")
    ax.set_ylabel("Spending (million EUR)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.tick_params(axis="x", rotation=60, labelsize=8)
    for i, label in enumerate(ax.get_xticklabels()):
        if i % 3 != 0:
            label.set_visible(False)
    path = FIG / "01_total_spending_trend.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_top_countries(countries: pd.DataFrame) -> Path:
    d = countries.copy()
    d = d[d["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False)]
    latest = d["periodo_parsed"].max()
    snap = d[(d["periodo_parsed"] == latest) & (d["dimension_value"].str.lower() != "total")].nlargest(10, "valor")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=snap, y="dimension_value", x="valor", ax=ax, color="#1B4965")
    ax.set_title(f"Top 10 source countries by spending — {latest}")
    ax.set_xlabel("Spending (million EUR)")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    path = FIG / "02_top_countries.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_ccaa(ccaa: pd.DataFrame) -> Path:
    d = ccaa.copy()
    d = d[d["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False)]
    latest = d["periodo_parsed"].max()
    snap = d[(d["periodo_parsed"] == latest) & (d["dimension_value"].str.lower() != "total")].nlargest(12, "valor")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=snap, y="dimension_value", x="valor", ax=ax, color="#5FA8A3")
    ax.set_title(f"Tourist spending by destination CCAA — {latest}")
    ax.set_xlabel("Spending (million EUR)")
    ax.set_ylabel("")
    path = FIG / "03_spending_by_ccaa.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_access(access: pd.DataFrame) -> Path:
    d = access.copy()
    d = d[d["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False)]
    latest = d["periodo_parsed"].max()
    snap = d[(d["periodo_parsed"] == latest) & (d["dimension_value"].str.lower() != "total")].sort_values("valor", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = sns.color_palette("Set2", n_colors=len(snap))
    ax.pie(snap["valor"], labels=snap["dimension_value"], autopct="%1.1f%%", colors=colors, startangle=90)
    ax.set_title(f"Spending share by access mode — {latest}")
    path = FIG / "04_access_mode_share.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_motive(motive: pd.DataFrame) -> Path:
    d = motive.copy()
    # annual series
    d = d[d["periodo"].astype(str).str.fullmatch(r"\d{4}")]
    latest_year = d["periodo"].astype(int).max()
    snap = d[(d["periodo"].astype(int) == latest_year) & (d["dimension_value"].str.lower() != "total")].sort_values("valor", ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(snap["dimension_value"], snap["valor"], color="#E76F51")
    ax.set_title(f"Spending by trip purpose — {latest_year} (annual)")
    ax.set_xlabel("Spending (million EUR)")
    path = FIG / "05_trip_purpose.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_yoy(countries: pd.DataFrame) -> Path:
    d = countries[
        (countries["dimension_value"].str.lower() == "total")
        & (countries["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False))
    ].copy()
    d = d.sort_values("periodo_parsed")
    d["valor_lag12"] = d["valor"].shift(12)
    d["yoy_pct"] = (d["valor"] / d["valor_lag12"] - 1) * 100
    d = d.dropna(subset=["yoy_pct"]).tail(24)
    fig, ax = plt.subplots(figsize=(11, 5))
    colors = np.where(d["yoy_pct"] >= 0, "#2A9D8F", "#E76F51")
    ax.bar(d["periodo_parsed"].astype(str), d["yoy_pct"], color=colors)
    ax.axhline(0, color="#333", linewidth=1)
    ax.set_title("YoY % change in total tourist spending (24 months)")
    ax.set_ylabel("% vs same month previous year")
    ax.tick_params(axis="x", rotation=60, labelsize=8)
    for i, label in enumerate(ax.get_xticklabels()):
        if i % 2 != 0:
            label.set_visible(False)
    path = FIG / "06_yoy_change.png"
    fig.savefig(path)
    plt.close(fig)
    return path


def write_insights(tables: dict[str, pd.DataFrame]) -> None:
    c = tables["10838"]
    monthly = c[
        (c["dimension_value"].str.lower() == "total")
        & (c["periodo_parsed"].apply(lambda p: getattr(p, "freqstr", "").startswith("M") if pd.notna(p) else False))
    ].sort_values("periodo_parsed")
    latest = monthly.iloc[-1]
    prev = monthly.iloc[-13] if len(monthly) > 13 else None
    yoy = None
    if prev is not None and prev["valor"]:
        yoy = (latest["valor"] / prev["valor"] - 1) * 100

    top = c[
        (c["periodo_parsed"] == latest["periodo_parsed"]) & (c["dimension_value"].str.lower() != "total")
    ].nlargest(3, "valor")

    ccaa = tables["10839"]
    ccaa_latest = ccaa[
        (ccaa["periodo_parsed"] == latest["periodo_parsed"]) & (ccaa["dimension_value"].str.lower() != "total")
    ].nlargest(3, "valor")

    lines = [
        "# EGATUR / INE — Key insights",
        "",
        f"_Generated from public INE tables. Latest month in series: **{latest['periodo_parsed']}**._",
        "",
        "## Headline",
        f"- Total tourist spending: **{latest['valor']:,.1f} million EUR** ({latest['periodo']}).",
    ]
    if yoy is not None:
        lines.append(f"- YoY change vs {prev['periodo']}: **{yoy:+.1f}%**.")
    lines += [
        "",
        "## Top source markets (latest month)",
    ]
    for _, r in top.iterrows():
        lines.append(f"- {r['dimension_value']}: {r['valor']:,.1f} M€")
    lines += ["", "## Top destination regions (CCAA)"]
    for _, r in ccaa_latest.iterrows():
        lines.append(f"- {r['dimension_value']}: {r['valor']:,.1f} M€")
    lines += [
        "",
        "## Portfolio takeaway",
        "- Seasonality and source-market concentration are the two drivers to watch for ops and destination marketing.",
        "- Air access dominates spending share; CCAA ranking highlights where overnight tourism value concentrates.",
        "",
        "## Figures",
        "- `outputs/figures/01_total_spending_trend.png`",
        "- `outputs/figures/02_top_countries.png`",
        "- `outputs/figures/03_spending_by_ccaa.png`",
        "- `outputs/figures/04_access_mode_share.png`",
        "- `outputs/figures/05_trip_purpose.png`",
        "- `outputs/figures/06_yoy_change.png`",
    ]
    INSIGHTS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    tables = build_master()
    chart_trend_total(tables["10838"])
    chart_top_countries(tables["10838"])
    chart_ccaa(tables["10839"])
    chart_access(tables["10828"])
    chart_motive(tables["23995"])
    chart_yoy(tables["10838"])
    write_insights(tables)
    print("Done. Figures in", FIG)
    print("Master CSV:", PROCESSED / "egatur_master_long.csv")
    print("Insights:", INSIGHTS)


if __name__ == "__main__":
    main()
