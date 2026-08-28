# LANDIS-II INTEGRATION & EXECUTION STATUS

**Document Type:** Technical Integration Specification & Reality Assessment  
**Date:** 2026-08-27  

---

## 1. Upstream LANDIS-II Ecosystem Inventory

The repository contains the genuine, uncorrupted LANDIS-II v8 and v7 codebases located at `Landis2_Project\`:

* **Core Engine:** `core/Core-Model-v7` (.NET Core / Framework C# console application)
* **Precompiled Assemblies:** `libraries/Support-Library-Dlls-v7` (including `Landis.Library.Succession-v8.dll`, `Landis.Library.BiomassCohorts-v4.dll`, `Landis.Library.Climate-v4.4.dll`, `MathNet.Numerics.dll`)
* **Succession Extensions:** `Extension-Biomass-Succession`, `Extension-NECN-Succession`, `Extension-PnET-Succession`
* **Disturbance Extensions:** `Extension-Dynamic-Fire-System`, `Extension-Base-Harvest`, `Extension-Biomass-BDA`, `Extension-Base-Wind`
* **Output Extensions:** `Extension-Output-Biomass`
* **Sample Scenarios:** `examples/Project-Lake-Tahoe-2017`, `examples/Project-Teaching-Materials`

---

## 2. Actual Coupling State vs Claimed Coupling

| Dimension | Current Reality | Required Scientific Description |
| :--- | :--- | :--- |
| **Scenario Parsing** | **IMPLEMENTED & VERIFIED** | `core_engine/landis_coupling.py` parses `scenario.txt`, `species.txt`, and converts biomass units ($1\text{ g/m}^2 = 0.01\text{ Mg/ha}$). |
| **Runtime Execution** | **NOT CONNECTED TO UI SIMULATOR** | The web UI runs an independent Python cellular automaton (`core_engine/spatial.py`) rather than spawning `Landis.Console.exe`. |
| **Two-Way Feedback** | **NOT IMPLEMENTED** | Results from our mathematical stability model are not currently fed back into LANDIS-II C# memory during execution. |
| **Coupling Classification** | **ONE-WAY TRANSLATION ADAPTER** | Must be explicitly documented as **One-Way Coupling Adapter (File/Format Translation & Reduced-Order Analysis)**. |

---

## 3. Unit Translation Formulas & Standards

$$\text{Biomass}_{\text{Mg/ha}} = \text{Biomass}_{\text{g/m}^2} \times 0.01$$
$$\text{Biomass}_{\text{g/m}^2} = \text{Biomass}_{\text{Mg/ha}} \times 100.0$$
$$\text{Carbon}_{\text{Mg C/ha}} = \text{Biomass}_{\text{Mg/ha}} \times 0.47 \quad \text{(IPCC Good Practice Guidance)}$$
$$D_i = \min\left(1.0, \frac{\text{LANDIS Disturbance Severity (1 to 5)}}{5.0}\right)$$

---

## 4. Integration Roadmap

1. **Step 1 (Current):** File-based parser and unit translator for LANDIS-II scenario, species, and output files.
2. **Step 2:** Subprocess execution of `Landis.Console.exe` via CLI runner in `core_engine/landis_runner.py` for compiled scenarios.
3. **Step 3:** Dynamic translation of LANDIS-II output rasters (`biomass/{species}-{timestep}.img`) into the 2D/3D visualizer.
