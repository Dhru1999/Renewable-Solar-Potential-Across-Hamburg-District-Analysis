"""
District-level rooftop solar metrics for Hamburg, as a reusable script.

This module repackages the workflow from the team notebook
(Redi_School_Spring_2026___Final_Project.py.ipynb) into tested functions:

    building CSV  ->  GeoDataFrame  ->  spatial join to districts  ->  district table

Differences from the notebook, chosen deliberately:

* Records the source classifies as "no building detected" (Eignung 8) or
  "insufficient data quality" (Eignung 0) are excluded from building counts and
  the solar-readiness denominator by default, as the notebook's own text says
  they should be. Pass ``exclude_non_rooftops=False`` to reproduce the notebook
  and dashboard numbers exactly.
* Districts with no solar-ready building keep a 0 % readiness instead of being
  dropped by an inner merge.
* The coordinate reference system is read from the data instead of assumed,
  and districts are reprojected to match the buildings.
* Unknown suitability labels raise an error instead of silently becoming NaN.

Usage:
    python -m solar_analysis.pipeline solar.csv hamburg_city_districts.geojson out.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkt

# Source labels (German) -> short English categories.
SUITABILITY_MAP = {
    "Eignung 1 (geeignet, sehr hohe Einstrahlung)": "Very High",
    "Eignung 2 (geeignet, hohe Einstrahlung)": "High",
    "Eignung 3 (geeignet, mittlere Einstrahlung)": "Moderate",
    "Eignung 6 (geringe Einstrahlung / weniger geeignet / vor Ort zu prüfen)": "Low",
    "Eignung 8 (kein Gebäude erkannt (Boden))": "No Building",
    "Eignung 0 (Datenqualität unzureichend)": "Insufficient Data",
}
SOLAR_READY = frozenset({"Very High", "High", "Moderate"})
NOT_A_ROOFTOP = frozenset({"No Building", "Insufficient Data"})

SOURCE_COLUMNS = {
    "buildingid": "building_id",
    "eignung_t": "suitability",
    "power": "solar_power_kwp",
    "pvarea": "solar_pvarea_m2",
    "geom": "geometry",
}


def load_buildings(csv_path: str | Path) -> gpd.GeoDataFrame:
    """Read the semicolon-separated export of the 'Solarpotenzialflächen Hamburg' dataset."""
    df = pd.read_csv(csv_path, sep=";")
    missing = [c for c in [*SOURCE_COLUMNS, "coordinate_reference_system"] if c not in df.columns]
    if missing:
        raise ValueError(f"Building file is missing columns: {', '.join(missing)}")

    crs_values = df["coordinate_reference_system"].dropna().unique()
    if len(crs_values) != 1:
        raise ValueError(f"Expected exactly one CRS in the building file, found {list(crs_values)}")

    df = df[list(SOURCE_COLUMNS)].rename(columns=SOURCE_COLUMNS)
    return prepare_buildings(df, crs=str(crs_values[0]))


def prepare_buildings(df: pd.DataFrame, crs: str) -> gpd.GeoDataFrame:
    """Translate suitability labels and turn WKT text into geometries."""
    unknown = sorted(set(df["suitability"].dropna()) - set(SUITABILITY_MAP))
    if unknown:
        raise ValueError(f"Unknown suitability labels: {unknown}")

    out = df.copy()
    out["suitability"] = out["suitability"].map(SUITABILITY_MAP)
    if out["geometry"].map(type).eq(str).any():
        out["geometry"] = out["geometry"].map(wkt.loads)
    return gpd.GeoDataFrame(out, geometry="geometry", crs=crs)


def load_districts(geojson_path: str | Path) -> gpd.GeoDataFrame:
    """Read the district boundaries; the source names the column 'Stadtteil'."""
    districts = gpd.read_file(geojson_path)
    if "Stadtteil" in districts.columns:
        districts = districts.rename(columns={"Stadtteil": "district"})
    if "district" not in districts.columns:
        raise ValueError("District file needs a 'Stadtteil' or 'district' column")
    return districts[["district", "geometry"]]


def assign_districts(buildings: gpd.GeoDataFrame, districts: gpd.GeoDataFrame
                     ) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Spatially join each building polygon to the district that fully contains it.

    Returns (assigned, unassigned). Buildings crossing a district border or
    lying outside every polygon are returned as unassigned rather than dropped
    silently, so the caller can report the coverage.
    """
    if districts.crs != buildings.crs:
        districts = districts.to_crs(buildings.crs)
    joined = gpd.sjoin(buildings, districts, how="left", predicate="within")
    joined = joined[~joined.index.duplicated(keep="first")]  # guard against overlapping districts
    assigned = joined[joined["district"].notna()].drop(columns="index_right")
    unassigned = buildings.loc[joined.index[joined["district"].isna()]]
    return assigned, unassigned


def summarize_districts(assigned: pd.DataFrame, exclude_non_rooftops: bool = True) -> pd.DataFrame:
    """District table: counts, total/average kWp and PV area, solar readiness %."""
    data = assigned
    if exclude_non_rooftops:
        data = data[~data["suitability"].isin(NOT_A_ROOFTOP)]

    summary = (
        data.groupby("district")
        .agg(
            number_of_buildings=("building_id", "count"),
            total_solar_power_kwp=("solar_power_kwp", "sum"),
            avg_solar_power_kwp=("solar_power_kwp", "mean"),
            total_solar_pvarea_m2=("solar_pvarea_m2", "sum"),
            avg_pv_area=("solar_pvarea_m2", "mean"),
            suitable_buildings=("suitability", lambda s: int(s.isin(SOLAR_READY).sum())),
        )
        .reset_index()
    )
    summary["suitable_buildings"] = summary["suitable_buildings"].astype(int)
    summary["suitability_percentage"] = (
        summary["suitable_buildings"] / summary["number_of_buildings"] * 100
    ).round(2)
    return summary.sort_values("total_solar_power_kwp", ascending=False, ignore_index=True)


def run(csv_path: str | Path, districts_path: str | Path, out_path: str | Path,
        exclude_non_rooftops: bool = True) -> pd.DataFrame:
    buildings = load_buildings(csv_path)
    districts = load_districts(districts_path)
    assigned, unassigned = assign_districts(buildings, districts)
    summary = summarize_districts(assigned, exclude_non_rooftops=exclude_non_rooftops)
    summary.to_csv(out_path, index=False)

    covered = set(summary["district"])
    print(f"Buildings read:          {len(buildings):,}")
    print(f"Assigned to a district:  {len(assigned):,} ({len(assigned) / len(buildings):.2%})")
    print(f"Not assigned:            {len(unassigned):,}")
    print(f"Districts with data:     {len(covered)} of {districts['district'].nunique()}")
    print(f"Wrote {out_path}")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("buildings_csv")
    parser.add_argument("districts_geojson")
    parser.add_argument("output_csv")
    parser.add_argument("--include-non-rooftops", action="store_true",
                        help="count 'No Building' and 'Insufficient Data' records like the notebook did")
    args = parser.parse_args(argv)
    run(args.buildings_csv, args.districts_geojson, args.output_csv,
        exclude_non_rooftops=not args.include_non_rooftops)
    return 0


if __name__ == "__main__":
    sys.exit(main())
