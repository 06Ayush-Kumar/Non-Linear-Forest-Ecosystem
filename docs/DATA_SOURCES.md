# Authoritative Data Sources, Provenance & Scientific Integrity

## 1. Classification Standards

Every ecological variable, species record, and spatial measurement in this platform is assigned one of the following authoritative provenance tags:

| Tag | Definition | Usage Rule |
| :--- | :--- | :--- |
| `OBSERVED` | Directly recorded in published forestry field inventories or official Tiger Conservation Plans. | Never applied to estimated or synthetic values. |
| `EXTERNAL DATA` | Retrieved from authenticated public scientific APIs (Open-Meteo, GBIF). | Must record endpoint, retrieval date, and latency. |
| `DERIVED` | Calculated via peer-reviewed allometric equations (e.g. IPCC carbon fraction 0.47). | Must cite parent observation and formula. |
| `MODELLED` | Computed by our 3-state nonlinear ODE solver or spatial diffusion equation. | Must display solver parameters and equations. |
| `CALIBRATED` | Estimated from peer-reviewed regional forestry literature with confidence bounds. | Must expose parameter ranges [min, max]. |
| `DEMO / SYNTHETIC` | Explicitly curated demonstration data for offline evaluation. | Must never be disguised as empirical field data. |
| `UNAVAILABLE` | Explicitly reported when empirical data are missing from forestry records. | Must never be filled with arbitrary numbers. |

---

## 2. Authoritative Repositories

### Indian Forestry & GIS
* **Forest Survey of India (FSI):** India State of Forest Reports (ISFR 2021 & 2023) - Growing stock tables, forest canopy density strata (VDF, MDF, OF), and aboveground carbon pools.
* **Champion & Seth (1968, revised 2020 by FSI):** *A Revised Survey of the Forest Types of India* - Canonical forest type classification.
* **National Tiger Conservation Authority (NTCA) & State Forest Departments:** Official Management Plans and Tiger Conservation Plans (Mudumalai, Bandipur, Kanha, Corbett, Kaziranga, Gir, Wayanad, Silent Valley).

### Biodiversity & Taxonomy
* **Global Biodiversity Information Facility (GBIF):** Occurrence backbone taxonomy and geographic records.
* **Botanical Survey of India (BSI) & Plants of the World Online (POWO / IPNI):** Canonical botanical nomenclature, authority citations, and synonym normalization.

### Species Traits & Invasive Literature
* **IUCN Global Invasive Species Database (GISD) & EICAT Evidence Dossiers.**
* **Kerala Forest Research Institute (KFRI) & Wildlife Institute of India (WII):** Published research monographs on invasive alien flora (*Lantana camara*, *Senna spectabilis*, *Prosopis juliflora*, *Parthenium hysterophorus*).
* **TRY Plant Trait Database:** Functional traits (maximum height, specific leaf area, shade/fire tolerances).

### Climatology & Environment
* **Open-Meteo Archive API:** ERA5-Land reanalysis historical temperature normals and precipitation grids.
* **India Meteorological Department (IMD):** 30-year gridded climate normals fallback.
