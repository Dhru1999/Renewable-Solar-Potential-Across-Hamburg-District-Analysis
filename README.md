# ☀️ Renewable Energy Potential Across Hamburg Districts

## Spatial Analysis of Rooftop Solar Potential Using GeoPandas & Looker Studio

![Python](https://img.shields.io/badge/Python-3.11-blue)
![GeoPandas](https://img.shields.io/badge/GeoPandas-Geospatial-green)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-orange)
![Looker Studio](https://img.shields.io/badge/Looker%20Studio-Dashboard-yellow)
![Project](https://img.shields.io/badge/Status-Completed-success)

---

## 📖 Project Overview

Hamburg has committed to becoming climate-neutral by **2045**, making renewable energy expansion a critical priority.

Although rooftops cover only about **10% of Hamburg's land area**, studies suggest they could provide more than **80% of the city's potential solar electricity supply**. However, solar potential is not distributed equally across districts due to differences in:

* Rooftop availability
* Building characteristics
* Solar suitability
* Urban density

This project performs a **building-level geospatial analysis** to identify which Hamburg districts offer the greatest opportunities for rooftop solar expansion.

---

## 🎯 Project Objectives

The primary objective of this project is to:

> Identify and rank Hamburg districts based on their rooftop solar potential using spatial analysis and geospatial data processing.

Specific goals:

* Analyze solar potential across more than 384,000 buildings.
* Aggregate building-level solar metrics at district level.
* Identify districts with the highest solar generation potential.
* Evaluate solar readiness and rooftop availability.
* Create interactive visualizations and dashboards for decision-making.

---

## 👥 Team Members

| Name              | Country | Background                            | Role                                                      |
| ----------------- | ------- | ------------------------------------- | --------------------------------------------------------- |
| Bahareh Fatemi    | Iran    | Electronic Communications Engineering | Geospatial Analysis & Python Development                  |
| Dhrupti Pambhar   | India   | Software Engineer                     | Project Planning, Dashboard & Insights Generation         |
| Zainab Olukoga O. | Nigeria | Mathematical Sciences                 | Renewable Energy Research, Dashboard & Python Development |

---

# 🗂 Dataset Information

## 1. Building-Level Solar Dataset

Contains rooftop solar potential information for approximately **384,525–384,908 buildings** across Hamburg.
 # https://suche.transparenz.hamburg.de/dataset/solarpotenzialflaechen-hamburg9?utm

### Features

| Column          | Description                         |
| --------------- | ----------------------------------- |
| building_id     | Unique building identifier          |
| suitability     | Solar PV suitability classification |
| solar_power_kwp | Estimated peak solar output         |
| solar_pvarea    | Usable rooftop solar area (m²)      |
| geometry        | Building footprint geometry         |

---

## 2. Hamburg District Boundaries Dataset

Administrative boundary polygons representing Hamburg's districts.
# https://gist.github.com/Kilie/179dca3a1dfd103be692357160a7c8be?utm


### Features

| Column   | Description               |
| -------- | ------------------------- |
| district | District name             |
| geometry | District polygon boundary |

Coverage:

* 104 Hamburg districts/quarters

---

# 🛠 Technologies Used

## Programming

* Python
* Jupyter Notebook

## Libraries

* Pandas
* GeoPandas
* NumPy
* Matplotlib

## Visualization

* Looker Studio
* Choropleth Mapping
* Geospatial Visualizations

---

# 🔄 Methodology

## Step 1: Data Collection

Collected:

* Hamburg Solar Potential Dataset
* Hamburg District Boundary GeoJSON

---

## Step 2: Data Cleaning

Performed:

* Missing value checks
* Geometry validation
* Coordinate system standardization
* Data consistency verification

---

## Step 3: Geospatial Processing

Converted datasets into GeoDataFrames and executed spatial operations.

### Spatial Join

Each building was assigned to its corresponding Hamburg district using:

```python
joined = gpd.sjoin(
    solar_gdf,
    districts_clean,
    how="inner",
    predicate="within"
)
```

This enabled district-level aggregation of solar metrics.

---

## Step 4: Aggregation & Feature Engineering

Calculated:

* Total solar power potential
* Total usable PV area
* Average rooftop PV area
* Solar readiness percentage
* District-level rankings

---

## Step 5: Visualization & Dashboarding

Created:

* District solar potential maps
* Top district rankings
* Solar readiness comparisons
* Interactive Looker Studio dashboard

---

# 📊 Key Results

## Hamburg-Wide Summary

| Metric                | Value            |
| --------------------- | ---------------- |
| Buildings Analyzed    | 385,000+         |
| Total Solar Potential | 4.58 Million kWp |
| Total Usable PV Area  | 41.3 Million m²  |
| Solar Ready Buildings | 72.3%            |

---

# 🏆 Top 10 Districts by Solar Power Potential

| Rank | District     | Solar Potential (kWp) |
| ---- | ------------ | --------------------- |
| 1    | Wilhelmsburg | 206,853               |
| 2    | Rahlstedt    | 196,781               |
| 3    | Bramfeld     | 117,400               |
| 4    | Billstedt    | 116,300               |
| 5    | Billbrook    | 112,000               |
| 6    | Langenhorn   | 111,500               |
| 7    | Bahrenfeld   | 107,200               |
| 8    | Niendorf     | 105,000               |
| 9    | Bergedorf    | 95,000                |
| 10   | Wandsbek     | 84,900                |

### Key Observation

Wilhelmsburg and Rahlstedt outperform all other districts by a significant margin.

---

# 🌞 Top Districts by Solar Readiness

Districts with the highest percentage of buildings suitable for solar installation:

1. Neuenfelde (86.1%)
2. Harvestehude (86.0%)
3. Cranz (85.5%)
4. Langenbek (84.5%)
5. Francop (84.4%)
6. Hoheluft-West (84.0%)
7. Eimsbüttel (83.1%)
8. Hoheluft-Ost (82.8%)
9. Borgfelde (82.6%)
10. Altona-Altstadt (81.9%)

### Insight

High solar readiness does not necessarily imply high total solar capacity.

---

# 🏗 Top Districts by Rooftop Solar Area

Districts offering the largest usable rooftop area:

* Wilhelmsburg
* Rahlstedt
* Billbrook
* Bahrenfeld
* Billstedt
* Bramfeld
* Langenhorn
* Niendorf
* Bergedorf
* Wandsbek

These districts represent strong candidates for large-scale solar deployment.

---

# 🏭 Districts with Largest Average Rooftops

Large rooftop structures are particularly attractive for commercial-scale installations.

Top districts include:

* Altenwerder
* Kleiner Grasbrook
* Waltershof
* Billbrook
* Steinwerder
* Veddel
* HafenCity
* Hammerbrook
* Allermöhe
* Dulsberg

---

# 📈 Future Solar Expansion Opportunities

To support future planning, a composite expansion indicator was explored by combining:

* Solar capacity
* Rooftop availability
* Solar suitability
* District readiness

This approach helps prioritize districts that offer the best balance between technical potential and deployment feasibility.

---

# 📊 Dashboard

The project includes an interactive dashboard providing:

✅ Solar Potential by District

✅ Solar Readiness Analysis

✅ Rooftop Area Rankings

✅ District-Level Comparisons

✅ Geographic Visualization of Solar Opportunities

---

# ⚠ Challenges Encountered

## Data Challenges

* Processing 384k+ building records
* Large geospatial datasets
* CSV and GeoJSON loading inconsistencies
* Geometry conversion issues

---

## Spatial Challenges

* District assignment validation
* Spatial join performance optimization
* Coordinate reference system alignment

---

# 💡 Solutions Implemented

* Dataset standardization
* Geometry cleaning
* GeoDataFrame conversion
* Spatial joins using GeoPandas
* Quality assurance checks
* Validation of district coverage

---

# 📚 Lessons Learned

Through this project, we gained practical experience in:

### Geospatial Data Science

* Spatial joins
* Geospatial visualization
* GeoJSON processing

### Data Engineering

* Large-scale dataset handling
* Data cleaning
* Data validation

### Analytics & Reporting

* Insight generation
* Dashboard design
* Decision-support visualization

---

# 🔍 Key Insights

✅ Hamburg possesses significant rooftop solar capacity.

✅ More than 72% of analyzed buildings are technically suitable for solar PV installation.

✅ Wilhelmsburg and Rahlstedt emerge as the highest-priority districts for future solar investments.

✅ Solar readiness and solar capacity are not always aligned.

✅ District-level spatial analysis provides actionable insights for renewable energy planning.

---

# 🚀 Future Improvements

* Include energy consumption data.
* Add economic feasibility analysis.
* Incorporate battery storage potential.
* Develop fully interactive GIS-based web maps.
* Expand dashboard with sustainability indicators.
* Build predictive models for future solar adoption.

# 🌍 Impact

This project demonstrates how geospatial analytics can support renewable energy planning by identifying where solar investments can generate the greatest impact.

The methodology can be replicated for other cities and regions seeking data-driven pathways toward climate neutrality and sustainable urban development.

---

## 🙏 Acknowledgements

* Hamburg Open Data Portal
* Hamburg Solar Potential Dataset
* Hamburg District GeoJSON Dataset
* ReDI School of Digital Integration
* GeoPandas Community
* Looker Studio

---

### ⭐ If you found this project useful, consider giving the repository a star!
