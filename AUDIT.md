# TECHNICAL & SCIENTIFIC AUDIT REPORT

**Project:** LANDIS-II Coupled India Forest Decision Support & Ecological Intelligence Platform  
**Audit Date:** 2026-08-27  
**Standard of Integrity:** Zero False Scientific Claims, Transparent Provenance, Honest Functional Status.

---

## 1. Executive Summary of Audit Findings

The platform contains a functioning, mathematically verified Python reduced-order continuous/discrete ecological engine ($dx/dt, dy/dt, dz/dt$), analytical Jacobian calculations cross-verified with numerical finite-differences ($< 10^{-4}$ error), and an extensive curated botanical database for Indian forest ecosystems.

However, a rigorous inspection of the source code reveals **critical scientific discrepancies, unverified claims, and disconnected pipelines**:

1. **LANDIS-II Execution Disconnect:** The cloned LANDIS-II C# core and extensions are present on disk, but the web UI "Simulate" button currently runs a standalone 2D Python cellular automaton (`core_engine/spatial.py`), **not the compiled LANDIS-II .NET executable**.
2. **Fabricated Validation Claims:** The top header badge `"94% (FSI Validated)"` was derived from a hard-coded scalar `data_confidence = 0.94` in `india_gis.py`, with no statistical validation procedure or real ground-truth confusion matrix.
3. **Hard-Coded Species Confidence:** Values such as `98%`, `96%`, `95%` in `trait_database.py` were manually assigned constants with no statistical calculation.
4. **Misleading "Observed Field Data" Badges:** Forest baselines (e.g. `158.4 Mg/ha` in `forest_baseline.py`) are regional literature approximations, not direct empirical plot measurements.
5. **Procedural 3D Forest:** The Three.js 3D visualizer uses procedural sine waves and random geometry, rather than rendering actual spatial simulation cell states or LANDIS-II output rasters.
6. **Broken Mathematical LaTeX Rendering:** Equations in the decision report rendered as raw unformatted LaTeX text strings (`$$\frac{dx}{dt}$$`) due to lack of a MathJax/KaTeX parser.
7. **Spatial Grid Homogeneity:** The 30×30 grid starts with identical uniform values across all cells with a single center point disturbance, failing to reflect spatial landscape heterogeneity (elevation, slope, soils).

---

## 2. Comprehensive Component Audit Table

| Component | Status | Source Code Evidence | Problem / Discrepancy | Required Action / Fix |
| :--- | :--- | :--- | :--- | :--- |
| **LANDIS-II Core Execution** | `NOT EXECUTED AT RUNTIME` | `core_engine/spatial.py:84`, `app.py` | UI simulation invokes `run_spatial_landscape_simulation()` (Python ODE), not `Landis.Console.exe`. | Change status badge to `LANDIS-II: STANDALONE ECOLOGICAL LAYER (ONE-WAY COUPLING ADAPTER)`. Document actual execution boundaries. |
| **FSI Validation Metric** | `HARD-CODED SCALAR` | `data_layer/india_gis.py:28`, `app.js:68` | `data_confidence = 0.94` is a hard-coded constant multiplied by 100 to produce `"94% (FSI Validated)"`. | **REMOVE 94% CLAIM IMMEDIATELY.** Replace with `FSI BASELINE: LITERATURE CURATED`. |
| **Species Confidence %** | `HARD-CODED CONSTANT` | `data_layer/trait_database.py:75` | `data_confidence=0.98` assigned manually without statistical calculation. | Replace arbitrary percentages with categorical provenance: `CURATED TAXON RECORD (TRY/BSI Literature)`. |
| **Observed Field Data Label** | `MISLABELLED APPROXIMATION` | `data_layer/forest_baseline.py:44` | Hard-coded constants `158.4 Mg/ha`, `26.8 Mg/ha`, `6.2 Mg/ha` labeled `OBSERVED`. | Reclassify status to `REGIONAL ESTIMATE (FSI ISFR 2021 / Literature Modelled)`. |
| **Analytical Jacobian Matrix** | `VERIFIED MATHEMATICALLY` | `core_engine/jacobian.py:24`, `tests/test_scientific_suite.py` | Analytical Continuous Jacobian $\mathbf{J}_F$ matches central finite difference within $10^{-5}$ error. | **KEEP & MAINTAIN.** Display verified finite-difference error ($< 10^{-4}$) transparently. |
| **Discrete Stability Map** | `VERIFIED MATHEMATICALLY` | `core_engine/stability.py:32` | $\mathbf{J}_{map} = \mathbf{I} + \Delta t \mathbf{J}_F$, $\rho = \max |\lambda_i|$ computed dynamically via `np.linalg.eigvals`. | Clarify that $\rho < 1$ represents **local mathematical stability of the discrete map**, not ecological resilience. |
| **2D Spatial Simulation Grid** | `SYNTHETIC CELLULAR AUTOMATA` | `core_engine/spatial.py:90` | Initialized with uniform biomass array ($145.0\text{ Mg/ha}$ everywhere) and artificial Gaussian perturbation. | Explicitly label as `SPATIAL SIMULATION: SYNTHETIC CELLULAR AUTOMATA`. Separate cell area ($1\text{ ha}$) from reserve extent ($32,100\text{ ha}$). |
| **3D Forest Visualizer** | `PROCEDURAL GRAPHICS DEMO` | `frontend/app.js:320-370` | Trees placed via `(Math.random() - 0.5) * 70` and terrain via `Math.sin(px * 0.1) * 3`. | Connect 3D mesh instancing directly to 2D simulation cell grid state $[x_{i,j}, y_{i,j}, z_{i,j}]$. Label as `3D VIEW: MODELLED STATE MESH`. |
| **10 Management Scenarios** | `PARAMETRIC DIFFERENCES` | `core_engine/scenarios.py:25-70` | Scenarios dynamically alter parameters ($D_z, D_i, r_3, \text{stress}$), but share synthetic initial grid. | Document parameter changes explicitly for every scenario; display exact parameter deltas. |
| **Decision Report LaTeX** | `BROKEN RENDERING` | `frontend/app.js:400` | Markdown replaced via naive regex, leaving raw `$$\frac{dx}{dt}$$` LaTeX syntax unrendered. | Integrate KaTeX / MathJax or render clean mathematical Unicode formulas in the report. |
| **API / Provenance Audit** | `PARTIAL / IN-MEMORY ONLY` | `data_layer/audit_logger.py`, `external_adapters.py` | External calls only logged if triggered; table appears empty if no live API call occurred during session. | Display explicit state: `NO LIVE EXTERNAL API CALLS RECORDED IN CURRENT SESSION (OFFLINE / LOCAL CACHE ACTIVE)`. |
| **Management Effect Claims** | `UNSOURCED SPECIFICITY` | `decision_support/management_engine.py:25` | Claims like "90-95% reduction" and "+1.8 Mg C/ha/yr" stored as hard-coded strings. | Label as `QUALITATIVE LITERATURE ESTIMATE (Babu et al. 2009 / Ramaswami & Sukumar 2014)`. |
