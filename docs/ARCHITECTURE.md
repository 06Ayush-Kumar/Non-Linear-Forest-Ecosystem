# LANDIS-II v8 Architecture & Scientific Coupling System Design

## 1. Upstream LANDIS-II Architecture Audit

The cloned upstream repository contains the complete **LANDIS-II Forest Landscape Simulation Ecosystem**:

```plaintext
Landis2_Project/
├── core/
│   └── Core-Model-v7/               # Console Application, Extension Admin, Core interfaces
├── libraries/
│   ├── Library-Core/                # Landis.Core (ISpecies, IEcoregion, ILandscape, IExtension)
│   ├── Library-Spatial/             # Landis.SpatialModeling, Landis.RasterIO (GDAL bindings)
│   ├── Library-Utilities/           # TextParser, LineReader, CSV parsers
│   ├── Library-Climate/             # Climate library (ERA5 / gridded weather generators)
│   ├── Library-Metadata/            # Metadata logging and schema definitions
│   └── Support-Library-Dlls-v7/     # Precompiled .NET assemblies (Succession-v8, BiomassCohorts-v4)
├── extensions/
│   ├── succession/                  # Succession Extensions
│   │   ├── Extension-Biomass-Succession/ # Biomass Succession v7.2 (Age-biomass cohorts)
│   │   ├── Extension-NECN-Succession/    # Century C & N soil/biomass dynamics v8.2
│   │   └── Extension-PnET-Succession/    # Photosynthesis & evapotranspiration v6.1
│   ├── disturbance/                 # Disturbance Extensions
│   │   ├── Extension-Dynamic-Fire-System/ # Dynamic Fire System v4.1 (Ignition, spread, fuel)
│   │   ├── Extension-Base-Harvest/        # Forest Harvest v5.1 (Prescriptions, stands, mgmt zones)
│   │   ├── Extension-Biomass-BDA/         # Biological Disturbance Agent v2.4 (Insect/pathogen)
│   │   └── Extension-Base-Wind/           # Windthrow Disturbance v4.1
│   └── output/                      # Output Extensions
│       └── Extension-Output-Biomass/ # Spatial raster maps (.img, .tif) & tabular CSV summaries
└── examples/
    ├── Project-Lake-Tahoe-2017/     # Multi-decadal forest landscape scenario datasets
    └── Project-Teaching-Materials/  # Laboratory scenarios for biomass succession & fire
```

---

## 2. LANDIS-II Core Data Representations

### Landscape & Spatial Grids
* **Landscape:** Represented as an active grid of cells indexed by `(row, column)`. Inactive cells (water bodies, non-forest rock) are flagged by `InactiveSite`.
* **Spatial Resolution:** Cell size typically ranges from $30	ext{m} 	imes 30	ext{m}$ ($0.09	ext{ ha}$) to $100	ext{m} 	imes 100	ext{m}$ ($1.0	ext{ ha}$) or $250	ext{m} 	imes 250	ext{m}$ ($6.25	ext{ ha}$).

### Species & Age-Biomass Cohorts
* **Species Representation:** Defined in `species.txt` with parameters: Longevity, Sexual Maturity Age, Shade Tolerance ($1-5$), Fire Tolerance ($1-5$), Effective Seed Dispersal Distance ($m$), Maximum Dispersal Distance ($m$), Vegetative Reproduction Probability, Sprout Age Min/Max, and Post-Fire Regeneration Strategy (`resprout`, `serotiny`, `none`).
* **Cohort Structure:** In `Biomass Succession`, each cell maintains a list of living cohorts per species: `(Species, Age, Biomass g/m²)`. Biomass accumulates annually via growth functions and decreases due to senescence, competition mortality, and disturbance.

---

## 3. Coupling Architecture: LANDIS-II + Our Original Scientific Layer

```plaintext
                 REAL LANDIS-II ENGINE (C# / .NET)
                                 │
           ┌─────────────────────┴─────────────────────┐
           ▼                                           ▼
   Succession Extensions                       Disturbance Extensions
 (Biomass, NECN, PnET)                      (Dynamic Fire, Base Harvest)
           │                                           │
           └─────────────────────┬─────────────────────┘
                                 │
                     LANDSCAPE STATE & OUTPUTS
                 (Spatial Rasters & Biomass CSVs)
                                 │
                                 ▼
                     LANDIS COUPLING ADAPTER
               (Unit Conversion: 1 g/m² = 0.01 Mg/ha)
                                 │
                                 ▼
            OUR ORIGINAL SCIENTIFIC ECOLOGY & STABILITY LAYER
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    Species Dynamics        Invasive Spread         Stability Analysis
   - Nonlinear 3-State     - Spatial Diffusion     - Continuous J_F
   - Gaussian Abiotic        D_z ∇²z               - Discrete J_map
     Suitability S_abiotic - Invasive Impact (IIS) - Spectral Radius ρ
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                       INDIA DECISION LAYER
           (28 States, 40+ Protected Areas, 10 Scenarios)
                                 │
                                 ▼
                 PROFESSIONAL SCIENTIFIC WORKSTATION UI
```

---

## 4. Coupling Type Classification

* **Current Implementation:** **Validated One-Way Coupled Pipeline (`LANDIS-II Outputs → Our Scientific Analysis Layer`)**.
* **Integrity Mandate:** We explicitly state that the current system reads, parses, and translates LANDIS-II spatial rasters and tabular outputs into our mathematical analysis engine. It does not claim full two-way feedback loop into LANDIS-II runtime memory unless supported by valid extension hooks.
