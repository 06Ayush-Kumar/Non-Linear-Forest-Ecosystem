# SYSTEM ARCHITECTURE & INTEGRATION SPECIFICATION (SYSTEM_ARCHITECTURE.md)

## 1. High-Level Architecture

The platform employs a decoupled, multi-tier scientific computing architecture:

`plaintext
+-----------------------------------------------------------------------------------+
|                            TIER 1: DATA INGESTION & APIS                          |
|  - Open-Meteo ERA5 Reanalysis API (Daily Tmean, Tmin, Tmax, Precip, Solar Rad)   |
|  - NASA/USGS SRTM 90m DEM API (Open-Elevation Bilinear Interpolation)            |
|  - Global Biodiversity Information Facility (GBIF Species Occurrence API)        |
|  - Forest Survey of India (FSI ISFR 2021 Biomass & Carbon Stock Pool Baselines)  |
|  - Curated Indian Botanical & Silvicultural Trait Database (40+ Species Records) |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        TIER 2: LANDIS-II SIMULATION ENGINE                        |
|  - Landis.Console.exe (.NET Framework 4.8 / Roslyn C# Native Release Binary)     |
|  - Biomass Succession Extension v7.2 (Cohort establishment, growth, mortality)    |
|  - Output Biomass Extension v4.1 (Native GDAL 2.0.2 GeoTIFF raster generator)     |
|  - Scenario Configuration: 9,801 landscape cells (100m res, 1 ha/cell)           |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        TIER 3: OUTPUT PARSER & COUPLING ADAPTER                   |
|  - Parses Biomass-succession-log.csv & spp-biomass-log.csv                        |
|  - GeoTIFF Raster Inventory (108 output files across succession years)            |
|  - Explicit 3-State Stratum Aggregation:                                          |
|      x(t) = sum(Native Climax Canopy Cohort Biomass) [Mg/ha]                      |
|      y(t) = sum(Understory & Subordinate Shrub Biomass) [Mg/ha]                   |
|      z(t) = sum(Invasive Alien Plant Biomass) [Mg/ha]                             |
|  - Aboveground Carbon pool: C(t) = (x + y + z) * 0.47 (IPCC 2006 / FSI method)    |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                 TIER 4: OUR SCIENTIFIC MATHEMATICAL & STABILITY LAYER             |
|  - Coupled Nonlinear 3-State Population Kinetics (RK4 Numerical Integration)     |
|  - Analytical Continuous 3x3 Jacobian Matrix: J_F = [df_i/dx_j]                   |
|  - Discrete-Time Map Matrix: J_map = I + dt * J_F                                 |
|  - Continuous & Discrete Eigenvalue Decomposition (np.linalg.eigvals)             |
|  - Spectral Radius: rho(J_map) = max |lambda_i|                                   |
|  - Numerical Central Finite-Difference Cross-Verification (< 10^-8 error)         |
|  - 10 Parametric Management Scenarios (EDRR, Containment, CRD, Restoration, etc.) |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                 TIER 5: DECISION SUPPORT & PROVENANCE WORKSTATION UI              |
|  - WebGL / Three.js 3D Forest Landscape Visualizer                                |
|  - Leaflet 2D GIS Protected Area Interactive Map                                  |
|  - 12-Step Candidate Introduction Ecological Risk Evaluator (IIS 0-100)           |
|  - Rule #3 Provenance Schema (11 metadata traceability tags per variable)         |
|  - Automated Scientific Decision Report Compiler (Markdown, JSON, Print ready)    |
|  - System Reality & Verification Status Dashboard                                 |
+-----------------------------------------------------------------------------------+
`

---

## 2. Component Coupling & Data Flow

`plaintext
User Selects Protected Area (e.g. Mudumalai / Kanha)
       |
       +---> API Adapters Fetch ERA5 Climate + SRTM DEM + GBIF Records
       |
       +---> Forest Baseline Layer derives initial strata [x0, y0, z0] & Carbon
       |
       +---> LANDIS-II Execution Service runs Landis.Console.exe scenario.txt
       |        |
       |        +---> Produces GeoTIFF maps & CSV logs
       |
       +---> Output Parser extracts 50-year state trajectory
       |
       +---> Stability Layer computes Analytical Jacobian, Eigenvalues & rho(J_map)
       |
       +---> Finite-Difference Solver confirms partial derivatives within tolerance
       |
       +---> 10 Scenarios Engine ranks management options via Invasive Impact Score
       |
       +---> Decision Report Exporter compiles reproducible scientific report
`

---

## 3. Directory & Module Responsibilities

- **pi/routes.py**: REST API endpoints for GIS, Baselines, APIs, LANDIS-II, Stability, Scenarios, Provenance, and Reports.
- **core_engine/landis_executor.py**: Subprocess orchestrator for Landis.Console.exe with timeout, exit code, stdout/stderr logging.
- **core_engine/landis_parser.py**: Ingests and parses Biomass-succession-log.csv, spp-biomass-log.csv, and GeoTIFFs.
- **core_engine/landis_coupling.py**: End-to-end execution pipeline connecting LANDIS-II outputs to stability analysis.
- **core_engine/model.py**: 3-state governing ODEs and environmental parameter modulation.
- **core_engine/jacobian.py**: Exact analytical partial derivatives and central finite-difference verification solver.
- **core_engine/stability.py**: Continuous/discrete eigenvalue calculation, spectral radius, and equilibria finder.
- **core_engine/spatial.py**: 2D cellular automata with spatial diffusion  
abla^2 z$ and RK4 kinetics.
- **core_engine/scenarios.py**: 10 standardized policy scenarios evaluated from identical baselines.
- **data_layer/external_adapters.py**: Open-Meteo, Open-Elevation, and GBIF adapters with caching and audit logging.
- **data_layer/forest_baseline.py**: Authentic baseline constructor for Indian Tiger Reserves and National Parks.
- **data_layer/trait_database.py**: Curated traits for 40+ species with zero synthetic confidence scores.
- **data_layer/taxonomy.py**: Canonical synonym resolution engine.
- **decision_support/candidate_evaluator.py**: 12-step invasive risk assessment and IIS scoring.
- **decision_support/report_generator.py**: Academic markdown decision report generator.
- **rontend/**: Interactive scientific workstation UI (Leaflet GIS, Three.js 3D, Chart.js, KaTeX math).
