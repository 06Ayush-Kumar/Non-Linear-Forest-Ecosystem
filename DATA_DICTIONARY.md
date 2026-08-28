# COMPREHENSIVE DATA DICTIONARY (DATA_DICTIONARY.md)

This data dictionary defines all state variables, physical units, parameter definitions, and provenance metadata schemas used across the platform.

---

## 1. Primary Model State Variables

| Variable Symbol | Full Name | Physical Unit | Physical Definition | Range | Primary Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| x | Native Climax Canopy Biomass | Mg/ha | Total dry standing biomass of mature dominant timber canopy species (Tectona, Shorea, Dalbergia, etc.) | [0.0, 300.0] | LANDIS-II output or FSI ISFR 2021 |
| y | Understory / Shrub Biomass | Mg/ha | Total dry standing biomass of sub-canopy vegetation, bamboos, and native subordinate shrubs | [0.0, 100.0] | LANDIS-II output or Long-term Plot Regressions |
| z | Invasive Alien Plant Biomass | Mg/ha | Total dry standing biomass of candidate or established invasive species (Lantana, Senna, Prosopis) | [0.0, 120.0] | Ground Quadrats / LANDIS-II |
| B_tot | Total Aboveground Biomass | Mg/ha | Sum of all dry vegetation strata: B_tot = x + y + z | [0.0, 520.0] | Derived (x + y + z) |
| C_agb | Aboveground Carbon Stock | Mg C/ha | Aboveground elemental carbon density: C_agb = B_tot * 0.47 | [0.0, 244.4] | Derived (IPCC 2006 Good Practice Guidance) |
| C_tot | Total Site Carbon Pool | kt C | Total sequestered carbon across entire protected area: C_tot = C_agb * Area (ha) / 1000 | [0.0, 5000.0] | Derived |

---

## 2. Kinetic & Ecological Parameters

| Parameter | Symbol | Unit | Default Range | Biological / Mathematical Meaning | Provenance & Calibration |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Intrinsic Growth Rate (Canopy) | r1 | yr^-1 | 0.20 - 0.60 | Base annual intrinsic growth rate of native timber trees | Calibrated from diameter increment curves (Troup 1921) |
| Intrinsic Growth Rate (Understory) | r2 | yr^-1 | 0.40 - 0.90 | Base annual intrinsic growth rate of subordinate shrubs & bamboos | Published silvicultural growth rates |
| Intrinsic Growth Rate (Invasive) | r3 | yr^-1 | 0.60 - 1.40 | Base annual growth rate of invasive weed thicket | Field regeneration trials (Babu et al. 2009) |
| Carrying Capacity (Canopy) | K1 | Mg/ha | 150.0 - 250.0 | Maximum asymptotic canopy biomass density supported at climax | FSI ISFR 2021 Growing Stock Tables |
| Carrying Capacity (Understory) | K2 | Mg/ha | 35.0 - 70.0 | Maximum understory biomass density | Literature allometry |
| Carrying Capacity (Invasive) | K3 | Mg/ha | 45.0 - 90.0 | Maximum monospecific invasive thicket biomass density | Tiger reserve invasive monitoring plots |
| Competition Coefficients | a_ij | Dimensionless | 0.10 - 0.80 | Per-unit competitive suppression of species j on species i | Field competition studies (Ramaswami & Sukumar 2011) |
| Spatial Diffusion Coefficient | D_z | ha/yr | 0.01 - 0.10 | Propagule dispersal and front expansion rate | Dispersal kernels (Endozoochory / Anemochory) |
| Abiotic Suitability | S_abiotic | [0.0, 1.0] | 0.05 - 1.0 | Multi-factor Gaussian environmental envelope | Sourced from Open-Meteo ERA5 & SRTM DEM |
| Environmental Stress | D_i | [0.0, 1.0] | 0.0 - 0.95 | Canopy disturbance fraction (wildfire, drought, cutting) | Working plan disturbance history |

---

## 3. Stability & Jacobian Variables

| Metric Symbol | Mathematical Definition | Range | Scientific Interpretation |
| :--- | :--- | :--- | :--- |
| J_F | Continuous Jacobian matrix [df_i / dx_j] | 3x3 matrix | Local rate of change of ODE flow near current landscape state. |
| J_map | Discrete-time Jacobian map: I + dt * J_F | 3x3 matrix | Local linearization of the discrete annual update map. |
| lambda_i | Eigenvalues: det(J - lambda * I) = 0 | Complex numbers | Real parts describe contraction/expansion along principal axes. |
| rho(J_map) | Spectral Radius: max |lambda_i(J_map)| | [0.0, inf) | rho < 1.0: Locally asymptotically stable. rho > 1.0: Locally unstable. |
| eps_FD | Finite-Difference Maximum Absolute Error | [0.0, 1.0] | Numerical validation: max |J_analytical - J_numerical|. Must be < 10^-4. |

---

## 4. Rule #3 Scientific Provenance Schema

Every variable reported across the API and UI implements the 11 metadata attributes:
1. `variable_name`: Exact physical/biological parameter name.
2. `value`: Numeric scalar, matrix, or 'DATA UNAVAILABLE'.
3. `unit`: Explicit SI or forestry unit (Mg/ha, m ASL, mm/yr, °C).
4. `data_status`: One of OBSERVED, EXTERNAL_API, DERIVED, MODELLED, CALIBRATED, DATA_UNAVAILABLE.
5. `source_agency`: Originating research institute or government body.
6. `dataset_name`: Authoritative dataset name or published title.
7. `dataset_version_date`: Version number or release year.
8. `source_url`: Verifiable HTTP URL or archival reference.
9. `retrieval_date`: ISO 8601 timestamp of live query or curation.
10. `spatial_resolution`: Geographic grain (100m raster cell, point, cadastral polygon).
11. `calculation_method`: Explicit equation or algorithmic step applied.
