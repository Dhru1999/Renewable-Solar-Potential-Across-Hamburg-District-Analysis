"""Tests on tiny synthetic geometries - the real dataset is not needed."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from solar_analysis import pipeline

VERY_HIGH = "Eignung 1 (geeignet, sehr hohe Einstrahlung)"
LOW = "Eignung 6 (geringe Einstrahlung / weniger geeignet / vor Ort zu prüfen)"
NO_BUILDING = "Eignung 8 (kein Gebäude erkannt (Boden))"

# Two districts side by side: West = [0,10]x[0,10], East = [10,20]x[0,10]
DISTRICTS = gpd.GeoDataFrame(
    {"Stadtteil": ["West", "East"], "geometry": [box(0, 0, 10, 10), box(10, 0, 20, 10)]},
    crs="EPSG:4326",
)


def buildings(rows):
    df = pd.DataFrame(rows, columns=["building_id", "suitability", "solar_power_kwp", "solar_pvarea_m2", "geometry"])
    return pipeline.prepare_buildings(df, crs="EPSG:4326")


@pytest.fixture
def sample():
    return buildings([
        (1, VERY_HIGH, 10.0, 100.0, box(1, 1, 2, 2).wkt),      # West
        (2, LOW, 2.0, 20.0, box(3, 3, 4, 4).wkt),              # West
        (3, NO_BUILDING, 0.0, 0.0, box(5, 5, 6, 6).wkt),       # West, not a rooftop
        (4, LOW, 4.0, 40.0, box(12, 1, 13, 2).wkt),            # East
        (5, VERY_HIGH, 50.0, 500.0, box(9.5, 1, 10.5, 2).wkt), # crosses the border
    ])


def districts():
    return DISTRICTS.rename(columns={"Stadtteil": "district"})


def test_wkt_text_becomes_geometry(sample):
    assert sample.geometry.iloc[0].equals(box(1, 1, 2, 2))
    assert sample.crs == "EPSG:4326"


def test_labels_are_translated(sample):
    assert list(sample["suitability"]) == ["Very High", "Low", "No Building", "Low", "Very High"]


def test_unknown_label_is_an_error():
    with pytest.raises(ValueError, match="Unknown suitability"):
        buildings([(1, "Eignung 9 (neu)", 1.0, 1.0, box(1, 1, 2, 2).wkt)])


def test_border_building_is_reported_not_dropped(sample):
    assigned, unassigned = pipeline.assign_districts(sample, districts())
    assert list(unassigned["building_id"]) == [5]
    assert sorted(assigned["building_id"]) == [1, 2, 3, 4]
    assert dict(zip(assigned["building_id"], assigned["district"])) == {1: "West", 2: "West", 3: "West", 4: "East"}


def test_districts_are_reprojected_to_building_crs(sample):
    projected = districts().to_crs("EPSG:3857")
    assigned, _ = pipeline.assign_districts(sample, projected)
    assert sorted(assigned["building_id"]) == [1, 2, 3, 4]


def test_summary_excludes_non_rooftops_by_default(sample):
    assigned, _ = pipeline.assign_districts(sample, districts())
    s = pipeline.summarize_districts(assigned).set_index("district")
    assert s.loc["West", "number_of_buildings"] == 2
    assert s.loc["West", "total_solar_power_kwp"] == 12.0
    assert s.loc["West", "suitability_percentage"] == 50.0


def test_notebook_mode_counts_every_record(sample):
    assigned, _ = pipeline.assign_districts(sample, districts())
    s = pipeline.summarize_districts(assigned, exclude_non_rooftops=False).set_index("district")
    assert s.loc["West", "number_of_buildings"] == 3
    assert s.loc["West", "suitability_percentage"] == pytest.approx(33.33)


def test_district_without_solar_ready_buildings_keeps_zero_percent(sample):
    assigned, _ = pipeline.assign_districts(sample, districts())
    s = pipeline.summarize_districts(assigned).set_index("district")
    assert s.loc["East", "suitable_buildings"] == 0
    assert s.loc["East", "suitability_percentage"] == 0.0


def test_summary_is_sorted_by_total_power(sample):
    assigned, _ = pipeline.assign_districts(sample, districts())
    assert list(pipeline.summarize_districts(assigned)["district"]) == ["West", "East"]


def test_end_to_end_from_files(tmp_path, sample):
    csv = tmp_path / "solar.csv"
    raw = pd.DataFrame({
        "_fid": range(5), "address": "", "eignung": "", "calcurl_pv": "", "calcurl_st": "",
        "buildingid": [1, 2, 3, 4, 5],
        "eignung_t": [VERY_HIGH, LOW, NO_BUILDING, LOW, VERY_HIGH],
        "power": [10.0, 2.0, 0.0, 4.0, 50.0], "pvarea": [100.0, 20.0, 0.0, 40.0, 500.0],
        "geom": [g.wkt for g in sample.geometry], "coordinate_reference_system": "EPSG:4326",
    })
    raw.to_csv(csv, sep=";", index=False)
    geojson = tmp_path / "districts.geojson"
    DISTRICTS.to_file(geojson, driver="GeoJSON")
    out = tmp_path / "metrics.csv"

    assert pipeline.main([str(csv), str(geojson), str(out)]) == 0
    result = pd.read_csv(out)
    assert set(result["district"]) == {"West", "East"}
    assert result.loc[result["district"] == "West", "number_of_buildings"].item() == 2


def test_missing_columns_are_reported(tmp_path):
    csv = tmp_path / "bad.csv"
    pd.DataFrame({"buildingid": [1]}).to_csv(csv, sep=";", index=False)
    with pytest.raises(ValueError, match="missing columns"):
        pipeline.load_buildings(csv)
