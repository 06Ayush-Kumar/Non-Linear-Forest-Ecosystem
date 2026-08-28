# REAL LANDIS-II INTEGRATION & EXECUTION ARCHITECTURE (LANDIS_INTEGRATION.md)

## 1. Engine & Runtime Verification

- **Engine Binary:** `build_landis/bin/Landis.Console.exe`
- **Compiler / Source:** Roslyn C# Compiler targeting .NET Standard 2.0 / .NET Framework 4.8 Runtime.
- **Core Library:** `Landis.Core.dll` (v7.0)
- **Active Extensions:**
  1. `Landis.Extension.Succession.Biomass-v7.dll` (Biomass Succession v7.2)
  2. `Landis.Extension.Output.Biomass-v4.dll` (Output Biomass v4.1)
- **Raster I/O Driver:** GDAL 2.0.2 Native Runtime (`gdal202.dll`, `gdal_wrap.dll`, `Gdal.Core.dll`)

---

## 2. LANDIS-II Scenario Architecture

- **Landscape Grid:** 99 rows x 99 columns = 9,801 landscape cells at 100m x 100m (1 ha/cell).
- **Active Ecoregions:** Defined in `ecoregions.txt` and `ecoregions.tif`.
- **Species Parameters:** Defined in `Core_species_data.txt` and `SpeciesData.csv` (15 species cohorts with shade tolerance, fire tolerance, longevity, mature age, seed dispersal distance).
- **Climate Generator:** `biomass-succession_ClimateGenerator.txt` driven by monthly temperature, precipitation, and variance.

---

## 3. Subprocess Execution & Safety Protocols

Execution is managed via `core_engine/landis_executor.py`:
1. Validates presence of `Landis.Console.exe` and assemblies.
2. Injects `build_landis/bin/` into process `PATH` so GDAL runtime DLLs load seamlessly.
3. Spawns process with timeout guard (default 120s).
4. Captures `stdout`, `stderr`, exit code, execution duration, and log timestamps.
5. Returns structured JSON dictionary to API without hanging the main web server.

---

## 4. Output Parsing & Transformation Pipeline

The parser in `core_engine/landis_parser.py`:
1. Reads `Biomass-succession-log.csv`:
   - `AvgLiveB` (g/m²) converted to `biomass_mg_ha` via factor 0.01.
   - `AvgAG_NPP` (g/m²/yr) converted to `anpp_mg_ha_yr` via factor 0.01.
   - Aboveground Carbon calculated via IPCC 2006 factor: Carbon = Biomass * 0.47.
2. Reads `spp-biomass-log.csv`:
   - Extracts individual species biomass columns (`AboveGroundBiomass_<species>`).
   - Aggregates cohorts into the 3 functional strata:
     - x(t): Native Climax Canopy Cohorts (Teak, Sal, Rosewood, Pine, Oak, Maple)
     - y(t): Subordinate Understory Cohorts (Bamboo, Birch, Ash, Basswood)
     - z(t): Invasive / Fast-spreading Cohorts (Lantana, Aspen, Jack Pine)
3. Catalogs 108 generated GeoTIFF raster maps (`outputs/biomass/*.tif`) for spatial GIS inspection.
