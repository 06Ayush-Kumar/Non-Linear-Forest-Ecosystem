# TEST REALITY & DATA PROVENANCE AUDIT (TEST_REALITY_AUDIT.md)

**System:** Real India Forest Ecosystem Decision-Support System  
**Audit Purpose:** Strict verification of test fidelity, distinguishing real native execution, real API queries, curated literature data, mathematical formulations, and spatial cellular automata approximations across the 3 fundamental system layers.

---

## 0. THE THREE DISTINCT SCIENTIFIC LAYERS

The platform architecture strictly separates and never conflates the three computational layers:

```
+-----------------------------------------------------------------------------------+
| LAYER 1: REAL LANDIS-II ENGINE                                                   |
| - Actual compiled binary: build_landis/bin/Landis.Console.exe (.NET Framework 4.8)|
| - Official extensions: Biomass Succession v7.2 + Output Biomass v4.1 (GDAL Native)|
| - Spatial domain: 9,801 landscape cells (100m res, 1 ha/cell)                    |
| - Outputs: 108 GeoTIFF rasters + Biomass-succession-log.csv + spp-biomass-log.csv|
| - Official Provenance Label: LANDIS-II OUTPUT                                     |
+-----------------------------------------------------------------------------------+
                                          | (Stratum Aggregation: x, y, z)
                                          v
+-----------------------------------------------------------------------------------+
| LAYER 2: OUR REDUCED-ORDER ECOLOGICAL MODEL                                       |
| - Coupled 3-state nonlinear ODEs for Canopy (x), Understory (y), Invasive (z)     |
| - Analytical Continuous Jacobian J_F = [df_i/dx_j]                                |
| - Discrete Linearized Map J_map = I + dt * J_F                                    |
| - Continuous & Discrete Eigenvalues + Spectral Radius rho(J_map) = max |lambda_i| |
| - Central Finite-Difference Cross-Check Verification (< 10^-8 error)              |
| - Official Provenance Label: SCIENTIFIC MODEL OUTPUT                              |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| LAYER 3: OUR REDUCED-ORDER SPATIAL REACTION-DIFFUSION MODEL                       |
| - 30x30 Cellular Automaton (900 ha domain)                                        |
| - Local Kinetics: 4th-Order Runge-Kutta (RK4) ODE numerical integration           |
| - Spatial Seed Dispersal / Spread: 5-Point Laplacian Diffusion D_z * Lap(z)       |
| - Multi-factor Gaussian abiotic suitability gradient S(r,c)                       |
| - Official Provenance Label: REDUCED-ORDER SPATIAL MODEL OUTPUT                   |
+-----------------------------------------------------------------------------------+
```

---

## 1. Test Reality Verification Table

| Test Name | Real or Mock | Data Source | Actual LANDIS-II Execution | What It Proves | Known Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `test_landis_engine_installed` | **REAL EXECUTION** | Local filesystem (`build_landis/bin/`) | No (Filesystem Verification) | Verifies that compiled `Landis.Console.exe`, `Landis.Core.dll`, and extension DLLs (`Biomass Succession v7.2`, `Output Biomass v4.1`) exist and are valid .NET assemblies. | Does not invoke the simulation in this specific test. |
| `test_landis_output_parsing` | **REAL LANDIS-II OUTPUT** | `runs/test_run_biomass_v7/` | No (Parses Output Files) | Proves parser accurately reads `Biomass-succession-log.csv`, `spp-biomass-log.csv`, GeoTIFF rasters, extracts strata [x, y, z], and applies IPCC 2006 carbon multiplier (0.47). | Relies on existing run outputs on disk in this specific test. |
| `test_open_meteo_climate_adapter` | **REAL API REQUEST** | Open-Meteo ERA5 Reanalysis API (`archive-api.open-meteo.com`) | No | Proves live HTTP network query to ECMWF ERA5 reanalysis, calculation of mean/min/max temperature, precipitation sums, and disk caching with fallback. | 0.1° (~11 km) gridded reanalysis, not an in-situ weather station. |
| `test_open_elevation_dem_adapter` | **REAL API REQUEST** | NASA/USGS SRTM 90m DEM (`api.open-elevation.com`) | No | Proves live query and bilinear interpolation of digital elevation model for exact geographical coordinates. | Centroid elevation point rather than continuous elevation raster. |
| `test_gbif_species_occurrences_adapter` | **REAL API REQUEST** | Global Biodiversity Information Facility (`api.gbif.org`) | No | Proves live query for verified point occurrences in India with synonym handling and institution herbarium logging. | Limited to public georeferenced records uploaded to GBIF. |
| `test_species_trait_database_provenance` | **REAL / LITERATURE CURATED** | Silvicultural Monographs (Troup 1921, Champion & Seth 1968, KFRI 2018, Babu et al. 2009) | No | Proves curated botanical database contains physiological traits, growth forms, shade/fire tolerances, and peer-reviewed citations with zero synthetic confidence scores. | Trait parameters are literature-based regional constants. |
| `test_api_reality_endpoints` | **REAL EXECUTION** | Flask In-Memory App Client | No | Proves RESTful API endpoints correctly serialize GIS catalogs, forest baselines, reality status dashboards, and stability calculations. | In-memory HTTP test client rather than external network request. |
| `test_complete_end_to_end_pipeline` | **REAL EXECUTION & REAL LANDIS-II** | Real Datasets + Native `Landis.Console.exe` Subprocess + Model Layer | **YES (GENUINE SUBPROCESS IN FRESH WORKSPACE)** | **Complete End-to-End Verification in Clean Directory:** Prepares clean directory with zero prior outputs, launches `Landis.Console.exe`, executes 50-year succession scenario, writes new GeoTIFFs, parses outputs into strata [x,y,z], computes analytical Jacobian, passes finite-difference cross-check (<10^-8 error), calculates discrete eigenvalues & spectral radius, evaluates 10 management scenarios, and compiles full 26-section scientific report. | Takes ~60 seconds to run full landscape simulation of 9,801 cells. |

---

## 2. In-Depth Audit of `test_complete_end_to_end_pipeline`

Here is the exact step-by-step trace of what happens when `test_complete_end_to_end_pipeline` executes:

1. **Creates Fresh Isolated Scenario Workspace:**  
   `create_fresh_scenario_directory("runs/test_run_biomass_v7", "runs/test_fresh_verification_run")` copies only scenario input files (`*.txt`, `*.tif`, `*.csv`).  
   **Asserts that `Biomass-succession-log.csv` and `spp-biomass-log.csv` DO NOT exist prior to execution.**
2. **Starts Real LANDIS-II Engine via Subprocess:**  
   `execute_landis_simulation()` spawns `build_landis/bin/Landis.Console.exe scenario.txt` inside `runs/test_fresh_verification_run`.
3. **Executes Actual LANDIS-II Scenario:**  
   `Landis.Console.exe` executes Biomass Succession v7.2 and Output Biomass v4.1 over 9,801 cells across 50 simulation years and returns exit code `0`.
4. **Produces Brand New LANDIS-II Output Files:**  
   Asserts that `Biomass-succession-log.csv`, `spp-biomass-log.csv`, and GeoTIFF rasters are freshly created with current timestamps.
5. **Parses Newly Generated Files:**  
   `parse_landis_output_directory()` reads the freshly created CSV tables, converts $g/m^2$ to $Mg/ha$ ($\times 0.01$), and aggregates 15 species cohorts into 3 functional strata: Native Climax Canopy ($x$), Understory ($y$), and Invasive ($z$).
6. **Passes Outputs into Scientific Model (Layer 2):**  
   Feeds extracted trajectory points into `build_calibrated_parameters()` and `calculate_stability_metrics()`.
7. **Calculates Jacobian from Runtime Values:**  
   Evaluates $\mathbf{J}_F(x,y,z) = [\partial f_i / \partial x_j]$ at runtime state $[x(t), y(t), z(t)]$.
8. **Validates Jacobian Numerically:**  
   Confirms numerical finite difference matches analytical Jacobian with maximum absolute error $< 10^{-8}$ (tolerance $10^{-4}$).
9. **Calculates Eigenvalues & Spectral Radius:**  
   Computes continuous spectrum $\lambda_i(\mathbf{J}_F)$, discrete linearized eigenvalues $\mu_i(\mathbf{J}_{map})$, and discrete spectral radius $\rho(\mathbf{J}_{map}) = \max |\mu_i|$.
10. **Evaluates 10 Management Scenarios:**  
    Executes 10 dynamic parameter variation simulations in `core_engine/scenarios.py`, computing dynamic trajectories, spectral radius, and Invasive Impact Scores (IIS).
11. **Produces 26-Section Report from Runtime Results:**  
    `generate_scientific_markdown_report()` compiles all runtime baseline, stability, and scenario values into a comprehensive scientific Markdown document.

---

## 3. UI Dashboard Metric Traceability & Categorical Provenance

| Dashboard Metric | Displayed Value (Example) | Underlying Source | Exact Calculation / Derivation | Provenance Chain & Literature Citation | Standard Provenance Category |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Native Standing Biomass** | `158.4 Mg/ha` | `data_layer/forest_baseline.py` | Mean growing stock for Tropical Moist/Dry Deciduous Forest in Nilgiris | FSI ISFR (2021) Growing Stock Tables & Volume Equations | **`DERIVED DATA`** |
| **Aboveground Carbon Density** | `89.96 Mg C/ha` | `data_layer/forest_baseline.py` | $\text{Total AGB} \times 0.47$ | IPCC (2006) Good Practice Guidance Carbon Fraction | **`DERIVED DATA`** |
| **Total Site Carbon Pool** | `28.9 kt C` | `data_layer/forest_baseline.py` | $\text{Carbon Density} \times \text{Area (ha)} / 1000$ | Cadastral Boundary Polygon Integration | **`DERIVED DATA`** |
| **Invasive Impact Score (IIS)** | `48.6 / 100` | `core_engine/invasive_model.py` | $100 \times (0.25 f_{cov} + 0.20 f_{bio} + 0.25 f_{disp} + 0.15 f_{sprd} + 0.15 f_{div})$ | Dynamic multi-criteria risk model (IUCN EICAT adapted) | **`MODELLED`** |
| **Continuous Jacobian $\mathbf{J}_F$** | 3x3 Matrix | `core_engine/jacobian.py` | $\mathbf{J}_F = [\partial f_i / \partial x_j]$ | Exact analytical partial derivatives cross-checked with central finite differences | **`SCIENTIFIC MODEL OUTPUT`** |
| **Discrete Spectral Radius $\rho$** | `0.9850` | `core_engine/stability.py` | $\rho(\mathbf{J}_{map}) = \max |\lambda_i|$ from $\mathbf{J}_{map} = \mathbf{I} + \Delta t \mathbf{J}_F$ | Discrete linearized map eigenvalue decomposition | **`SCIENTIFIC MODEL OUTPUT`** |
| **LANDIS-II Spatial Rasters** | 108 GeoTIFF files | `runs/test_run_biomass_v7/outputs/biomass/` | Native GDAL 2.0.2 raster output from Biomass Succession v7.2 | Executed via compiled binary `Landis.Console.exe` | **`LANDIS-II OUTPUT`** |
| **Species Provenance Badges** | `CURATED TAXON RECORD` | `data_layer/trait_database.py` | Categorical provenance attribution (94%/98% removed) | Troup (1921), Champion & Seth (1968), KFRI (2018), Babu et al. (2009) | **`REAL / OBSERVED DATA`** |
| **10 Management Scenarios** | 10 Ranked Policies | `core_engine/scenarios.py` | Parametric variations ($D_i, \text{removal rate}, \text{pressure}$) simulated over 30 years | Dynamically ranked by computed IIS score and spectral radius $\rho$ | **`MODELLED`** |
| **2D Spatial Simulation Grid** | 30x30 Raster Grid | `core_engine/spatial.py` | RK4 integration + spatial diffusion $D_z \nabla^2 z$ ($D_z = 0.045\text{ ha/yr}$) | Process-based reaction-diffusion cellular automaton | **`REDUCED-ORDER SPATIAL MODEL OUTPUT`** |
