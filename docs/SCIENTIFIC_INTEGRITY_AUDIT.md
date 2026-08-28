# SCIENTIFIC INTEGRITY & DATA PROVENANCE AUDIT

**Classification Scheme:**  
* `REAL / OBSERVED`: Authenticated field inventory or published forestry management plan records.  
* `EXTERNAL_DATA`: Live data fetched from authenticated public APIs (Open-Meteo, GBIF).  
* `DERIVED`: Computed via peer-reviewed equations (e.g. IPCC carbon fraction).  
* `MODELLED`: Calculated via our 3-state nonlinear ODE system or spatial diffusion solver.  
* `SIMULATED`: Generated through numerical spatial cellular automata iterations.  
* `ASSUMED / CALIBRATED`: Estimated from regional forestry literature with explicitly documented ranges.  
* `DEMO_SYNTHETIC`: Curated demonstration data for offline testing (never disguised as real).  
* `UNAVAILABLE`: Explicitly reported when empirical observations are missing.  

---

## 1. Classification of All Platform Variables & Components

| Variable / Component | Current Source / Implementation | Scientific Classification | Confidence Level | Integrity Note |
| :--- | :--- | :--- | :--- | :--- |
| **State & Protected Area GIS** | `data_layer/india_gis.py` | `REAL / OBSERVED` | **HIGH** | Coordinates, area extents, and forest types match official Forest Department records. |
| **Forest Baseline Biomass** | `data_layer/forest_baseline.py` | `ASSUMED / CALIBRATED` | **MEDIUM** | Regional growing stock averages from FSI ISFR 2021; not direct point-plot samples. |
| **Species Taxonomy** | `data_layer/taxonomy.py` | `REAL / DERIVED` | **HIGH** | Botanical binomials and synonyms cross-checked with BSI and IPNI/POWO. |
| **Species Biological Traits** | `data_layer/trait_database.py` | `ASSUMED / CALIBRATED` | **MEDIUM** | Trait ranges extracted from published literature (TRY, KFRI, Babu 2009). |
| **Abiotic Suitability ($S_{abiotic}$)** | `core_engine/suitability.py` | `MODELLED` | **HIGH** | Calculated dynamically from Gaussian niche equations ($S_T, S_E, S_M, S_S$). |
| **Nonlinear ODE Trajectories** | `core_engine/model.py` | `MODELLED` | **HIGH** | Computed via Runge-Kutta (RK4) numerical integration of 3-state equations. |
| **Continuous Jacobian Matrix $\mathbf{J}_F$** | `core_engine/jacobian.py` | `DERIVED` | **HIGH** | Exact analytical derivation, verified against central finite-differences ($< 10^{-4}$ error). |
| **Spectral Radius $\rho(\mathbf{J}_{map})$** | `core_engine/stability.py` | `DERIVED` | **HIGH** | Computed dynamically from eigenvalues of discrete map $\mathbf{J}_{map} = \mathbf{I} + \Delta t \mathbf{J}_F$. |
| **Spatial 2D Grid Cells** | `core_engine/spatial.py` | `DEMO_SYNTHETIC` | **LOW** | Synthetic $30 \times 30$ cellular automata grid; not real satellite raster data. |
| **3D WebGL Forest Mesh** | `frontend/app.js` | `DEMO_SYNTHETIC` | **LOW** | Procedural Three.js geometry; visualization only. |
| **Management Prescriptions** | `decision_support/management_engine.py` | `ASSUMED / CALIBRATED` | **MEDIUM** | Qualitative recommendations based on MoEFCC / KFRI published protocols. |
| **API Request Logs** | `data_layer/audit_logger.py` | `REAL / LOCAL` | **HIGH** | Accurately records local API requests; displays offline/cache state when not connected. |
| **FSI Validation Metric** | `frontend/app.js` (former "94%") | **FALSE CLAIM (REMOVED)** | **N/A** | Hard-coded scalar removed. Replaced by `FSI BASELINE: LITERATURE CURATED`. |

---

## 2. Integrity Mandates Enforced

1. **No False Validation Badges:** Removed all hard-coded percentage validation claims.
2. **Transparent Spatial Scale:** Explicitly separated the $30 \times 30$ grid ($900\text{ ha}$) from the total protected area extent (e.g. $32,100\text{ ha}$).
3. **Distinction of Stability vs Resilience:** Mathematical stability ($\rho < 1$) is clearly labeled as local discrete model stability, not empirical ecosystem resilience.
4. **Offline / Cache Transparency:** If external APIs are not queried during a session, the system explicitly displays `LOCAL CACHE / OFFLINE MODE ACTIVE`.
