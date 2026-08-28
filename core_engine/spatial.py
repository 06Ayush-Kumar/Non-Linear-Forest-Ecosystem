"""
Spatial Landscape & Diffusion Solver.
Simulates cellular landscape grid with:
  - Local nonlinear population dynamics (RK4 solver)
  - Dispersal diffusion D_z * Laplacian(z)
  - Propagule pressure and neighborhood seed rain
  - Environmental suitability spatial maps
  - Disturbance events (fire scars, logging, insect defoliation)
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, List, Tuple
from .model import EcologicalParameters, build_calibrated_parameters, ecological_derivatives
from .jacobian import analytical_continuous_jacobian, discrete_jacobian_map
from .stability import calculate_stability_metrics


def solve_rk4_step(state: np.ndarray, params: EcologicalParameters, dt: float) -> np.ndarray:
    """4th-order Runge-Kutta integrator step for spatial state grid [rows, cols, 3]."""
    k1 = ecological_derivatives(state, params)
    k2 = ecological_derivatives(state + 0.5 * dt * k1, params)
    k3 = ecological_derivatives(state + 0.5 * dt * k2, params)
    k4 = ecological_derivatives(state + dt * k3, params)
    
    new_state = state + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    # Strictly enforce biological non-negativity
    return np.maximum(0.0, new_state)


def discrete_laplacian_2d(grid: np.ndarray) -> np.ndarray:
    """Computes 5-point discrete spatial Laplacian operator for 2D diffusion."""
    lap = -4.0 * grid.copy()
    lap[:-1, :] += grid[1:, :]   # North
    lap[1:, :] += grid[:-1, :]   # South
    lap[:, :-1] += grid[:, 1:]   # East
    lap[:, 1:] += grid[:, :-1]   # West
    return lap


def generate_deterministic_spatial_pattern(
    grid_size: int = 30,
    area_id: str = "mudumalai",
    stratum: str = "native"
) -> np.ndarray:
    """
    Generates a deterministic 2D spatial pattern for a protected area.
    Normalized such that np.mean(pattern) == 1.0 strictly.
    Uses area_id and stratum as seeds, without non-deterministic randomness.
    """
    import hashlib
    seed_str = f"{area_id.lower().strip()}_{stratum}_spatial_v1"
    h_bytes = hashlib.sha256(seed_str.encode("utf-8")).digest()
    seed_int = int.from_bytes(h_bytes[:4], "big")
    rng = np.random.default_rng(seed_int)

    rows, cols = np.indices((grid_size, grid_size))
    r_norm = rows / max(1, grid_size - 1)
    c_norm = cols / max(1, grid_size - 1)

    # 1. Harmonic macro-scale environmental gradient
    f1 = 1.0 + float(h_bytes[0] % 3)
    f2 = 1.0 + float(h_bytes[1] % 3)
    p1 = (float(h_bytes[2]) / 255.0) * 2 * np.pi
    p2 = (float(h_bytes[3]) / 255.0) * 2 * np.pi

    harmonics = (
        0.30 * np.sin(2 * np.pi * f1 * r_norm + p1) +
        0.25 * np.cos(2 * np.pi * f2 * c_norm + p2) +
        0.15 * np.sin(2 * np.pi * (f1 * r_norm + f2 * c_norm))
    )

    # 2. Clustered biomass patches (Gaussian kernels)
    n_patches = 4 + (h_bytes[4] % 4)
    patches = np.zeros((grid_size, grid_size), dtype=float)
    for _ in range(n_patches):
        pr = rng.uniform(0.1, 0.9) * grid_size
        pc = rng.uniform(0.1, 0.9) * grid_size
        sigma = rng.uniform(2.5, 6.0)
        weight = rng.uniform(0.4, 0.9)
        patches += weight * np.exp(-((rows - pr)**2 + (cols - pc)**2) / (2 * sigma**2))

    # 3. Canopy gaps (localized dips)
    n_gaps = 2 + (h_bytes[5] % 3)
    gaps = np.zeros((grid_size, grid_size), dtype=float)
    for _ in range(n_gaps):
        gr = rng.uniform(0.15, 0.85) * grid_size
        gc = rng.uniform(0.15, 0.85) * grid_size
        sigma_g = rng.uniform(1.8, 3.8)
        gaps += 0.45 * np.exp(-((rows - gr)**2 + (cols - gc)**2) / (2 * sigma_g**2))

    if stratum == "native":
        raw = 1.0 + harmonics + 0.4 * patches - 0.7 * gaps
    elif stratum == "understory":
        raw = 1.0 - 0.4 * harmonics - 0.3 * patches + 0.8 * gaps
    elif stratum == "invasive":
        diag = np.exp(-((rows - cols)**2) / (2 * (grid_size * 0.2)**2)) if (h_bytes[6] % 2 == 0) else np.exp(-((rows + cols - grid_size)**2) / (2 * (grid_size * 0.2)**2))
        raw = 0.15 + 0.85 * patches + 0.5 * diag + 0.4 * gaps
    else:
        raw = 1.0 + harmonics

    raw = np.maximum(0.05, raw)
    normalized = raw / np.mean(raw)
    return normalized


def run_spatial_landscape_simulation(
    grid_size: int = 30,
    years: int = 30,
    dt: float = 0.1,
    suitability_grid: np.ndarray | None = None,
    disturbance_grid: np.ndarray | None = None,
    initial_native: float = 140.0,
    initial_competing: float = 28.0,
    initial_invasive: float = 4.0,
    diffusion_coeff: float = 0.045,
    invasive_pressure: float = 1.0,
    area_id: str = "mudumalai"
) -> Dict[str, Any]:
    if suitability_grid is None:
        # Default spatial elevation / moisture gradient
        rows, cols = np.indices((grid_size, grid_size))
        dist = np.sqrt((rows - grid_size/2)**2 + (cols - grid_size/2)**2)
        suitability_grid = np.clip(0.95 - 0.02 * dist, 0.4, 0.98)

    if disturbance_grid is None:
        disturbance_grid = np.zeros((grid_size, grid_size), dtype=float)

    # Generate deterministic normalized spatial patterns (mean == 1.0)
    pat_native = generate_deterministic_spatial_pattern(grid_size, area_id, "native")
    pat_understory = generate_deterministic_spatial_pattern(grid_size, area_id, "understory")
    pat_invasive = generate_deterministic_spatial_pattern(grid_size, area_id, "invasive")

    # Initialize 3-state landscape grid: [rows, cols, 3] with site-specific baseline initial state
    landscape = np.zeros((grid_size, grid_size, 3), dtype=float)
    landscape[:, :, 0] = initial_native * pat_native
    landscape[:, :, 1] = initial_competing * pat_understory
    landscape[:, :, 2] = initial_invasive * pat_invasive


    # Setup parameters
    mean_suit = float(np.mean(suitability_grid))
    mean_dist = float(np.mean(disturbance_grid))
    params = build_calibrated_parameters(mean_suit, mean_dist, invasive_pressure)

    total_steps = int(years / dt)
    record_interval = max(1, int(1.0 / dt)) # Record yearly

    yearly_timelines = []
    yearly_biomass_native = []
    yearly_biomass_competing = []
    yearly_biomass_invasive = []
    yearly_invasive_coverage = []
    yearly_spectral_radius = []
    yearly_snapshots = []

    for step in range(total_steps):
        # Record metrics yearly (including exact Step 0 before first integration step)
        if step % record_interval == 0:
            sim_year = int(step * dt)
            mean_n = float(np.mean(landscape[:, :, 0]))
            mean_c = float(np.mean(landscape[:, :, 1]))
            mean_i = float(np.mean(landscape[:, :, 2]))

            # Invasive spatial occupancy (> 2 Mg/ha threshold)
            inv_cells = int(np.count_nonzero(landscape[:, :, 2] > 2.0))
            cov_pct = round(100.0 * inv_cells / (grid_size * grid_size), 1)

            # Evaluate stability on the landscape state vector [x, y, z]
            landscape_state = np.array([mean_n, mean_c, mean_i], dtype=float)
            stab = calculate_stability_metrics(landscape_state, params, dt)

            yearly_timelines.append(sim_year)
            yearly_biomass_native.append(round(mean_n, 2))
            yearly_biomass_competing.append(round(mean_c, 2))
            yearly_biomass_invasive.append(round(mean_i, 2))
            yearly_invasive_coverage.append(cov_pct)
            yearly_spectral_radius.append(stab["spectral_radius"])

            # Save grid snapshot for interactive time machine
            grid_snapshot = []
            for r in range(grid_size):
                row_cells = []
                for c in range(grid_size):
                    n_val = float(landscape[r, c, 0])
                    c_val = float(landscape[r, c, 1])
                    i_val = float(landscape[r, c, 2])
                    local_rho = round(stab["spectral_radius"] * (1.0 + 0.05 * (i_val / 20.0)), 4)
                    p_code = "HIGH_INTERVENTION" if i_val > 15.0 else ("CONTAINMENT" if i_val > 3.0 else "MAINTENANCE")
                    row_cells.append({
                        "native": round(n_val, 1),
                        "competing": round(c_val, 1),
                        "invasive": round(i_val, 1),
                        "rho": local_rho,
                        "priority": p_code,
                        "suitability": round(float(suitability_grid[r, c]), 2)
                    })
                grid_snapshot.append(row_cells)
            yearly_snapshots.append(grid_snapshot)

        # 1. Local Ecological Kinetics
        landscape = solve_rk4_step(landscape, params, dt)

        # 2. Spatial Diffusion & Seed Dispersal for Invasive State (z)
        lap_z = discrete_laplacian_2d(landscape[:, :, 2])
        diffusion_flux = diffusion_coeff * lap_z * dt
        landscape[:, :, 2] = np.maximum(0.0, landscape[:, :, 2] + diffusion_flux)

    # Record final state at end of simulation
    if len(yearly_timelines) <= years:
        sim_year = years
        mean_n = float(np.mean(landscape[:, :, 0]))
        mean_c = float(np.mean(landscape[:, :, 1]))
        mean_i = float(np.mean(landscape[:, :, 2]))
        inv_cells = int(np.count_nonzero(landscape[:, :, 2] > 2.0))
        cov_pct = round(100.0 * inv_cells / (grid_size * grid_size), 1)
        landscape_state = np.array([mean_n, mean_c, mean_i], dtype=float)
        stab = calculate_stability_metrics(landscape_state, params, dt)

        yearly_timelines.append(sim_year)
        yearly_biomass_native.append(round(mean_n, 2))
        yearly_biomass_competing.append(round(mean_c, 2))
        yearly_biomass_invasive.append(round(mean_i, 2))
        yearly_invasive_coverage.append(cov_pct)
        yearly_spectral_radius.append(stab["spectral_radius"])

        grid_snapshot = []
        for r in range(grid_size):
            row_cells = []
            for c in range(grid_size):
                n_val = float(landscape[r, c, 0])
                c_val = float(landscape[r, c, 1])
                i_val = float(landscape[r, c, 2])
                local_rho = round(stab["spectral_radius"] * (1.0 + 0.05 * (i_val / 20.0)), 4)
                p_code = "HIGH_INTERVENTION" if i_val > 15.0 else ("CONTAINMENT" if i_val > 3.0 else "MAINTENANCE")
                row_cells.append({
                    "native": round(n_val, 1),
                    "competing": round(c_val, 1),
                    "invasive": round(i_val, 1),
                    "rho": local_rho,
                    "priority": p_code,
                    "suitability": round(float(suitability_grid[r, c]), 2)
                })
            grid_snapshot.append(row_cells)
        yearly_snapshots.append(grid_snapshot)

    return {
        "grid_size": grid_size,
        "simulation_years": years,
        "dt": dt,
        "timelines": yearly_timelines,
        "spatial_grids": yearly_snapshots,
        "biomass_series": {
            "native": yearly_biomass_native,
            "competing": yearly_biomass_competing,
            "invasive": yearly_biomass_invasive
        },
        "invasive_coverage_series": yearly_invasive_coverage,
        "spectral_radius_series": yearly_spectral_radius
    }
