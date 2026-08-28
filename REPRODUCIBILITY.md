# REPRODUCIBILITY & SIMULATION METADATA SCHEMA (REPRODUCIBILITY.md)

Every simulation run generates a structured reproducibility package containing:

1. **`simulation_id`**: Cryptographic/timestamp unique identifier (e.g. `sim_20260828_153022_mudumalai`).
2. **`engine_metadata`**:
   - LANDIS-II Core Version: 7.0 Release
   - Extensions: Biomass Succession v7.2, Output Biomass v4.1
   - Runtime: .NET Framework 4.8 / Roslyn C#
   - GDAL Version: 2.0.2 Native
3. **`input_state`**:
   - Protected Area ID & Cadastral Coordinates
   - Baseline Stratum Biomass [x0, y0, z0] (Mg/ha)
   - Initial Carbon Pool (kt C)
4. **`environmental_parameters`**:
   - Sourced ERA5 Mean Temperature (°C) and Annual Rainfall (mm)
   - NASA/SRTM Elevation (m ASL)
   - Calculated Abiotic Suitability S_abiotic and Stress Factor D_i
5. **`model_configuration`**:
   - Time Step dt = 0.1 yr
   - Duration = 30 yr (or 50 yr for LANDIS-II)
   - Numerical Solver: 4th-Order Runge-Kutta (RK4)
6. **`output_artifacts`**:
   - Complete yearly trajectories [x(t), y(t), z(t), rho(t)]
   - Generated GeoTIFF raster maps
   - Analytical & Numerical Jacobian matrices with error metrics.
