# SYSTEM LIMITATIONS & DATA GAPS (LIMITATIONS.md)

In accordance with scientific integrity rules, known methodological limitations and data constraints are explicitly declared:

1. **LANDIS-II Spatial Grain vs Local ODEs:**
   - LANDIS-II executes at a 100m x 100m (1 ha) raster cell resolution. The coupled 3-state ODE layer provides spatial-aggregate and cellular-automata approximations; it does not replace individual tree-level spatial coordinates.
2. **Regional Climatological Averages:**
   - Open-Meteo ERA5 data provides a 0.1° (~11 km) gridded reanalysis. Micro-topographic temperature variations within deep valleys (e.g. Nilgiri ravines) are smoothed out.
3. **Trait Parameter Calibration:**
   - While all species traits are grounded in published Indian forestry monographs (Troup 1921, Champion & Seth 1968, KFRI 2018), exact in-situ competition coefficients a_ij vary across soil edaphic types and require site-specific plot calibration.
4. **Validation Ground-Truth Availability:**
   - Wall-to-wall annual empirical ground quadrat data across all 40+ Indian tiger reserves are not publicly accessible via live APIs. Regional baselines rely on published biennial FSI ISFR inventories and Forest Department Tiger Conservation Plans.
