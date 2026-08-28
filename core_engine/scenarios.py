"""
Standardized Management Scenario Simulation & Stability Evaluation Engine.
Simulates 10 comparative management policies by dynamically altering ecological parameters,
stress factors, invasive propagule pressure, and restoration boosts:
  1. Baseline / No Intervention
  2. Early Detection & Rapid Response (EDRR)
  3. Containment & Perimeter Buffer
  4. Mechanical Rootstock Removal (CRD Method)
  5. Active Native Succession Restoration
  6. Climate Warming Stress (+2.0°C)
  7. Severe Multi-Year Drought Stress
  8. Severe Wildfire Disturbance Event
  9. High Invasive Propagule Pressure
  10. Integrated Control + Active Restoration Policy

For each scenario, computes:
  - Exact state trajectories [x, y, z] across years
  - Continuous & discrete Jacobian matrices
  - Eigenvalues and Spectral Radius rho(J_map)
  - Finite-difference Jacobian cross-check
  - Total Aboveground Biomass (Mg/ha) and Carbon Stock (Mg C/ha = AGB * 0.47)
  - Invasive Impact Score (IIS) and dynamic ranking.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
import numpy as np

from .model import EcologicalParameters, build_calibrated_parameters, ecological_derivatives
from .jacobian import analytical_continuous_jacobian, discrete_jacobian_map, verify_jacobian
from .stability import calculate_stability_metrics
from .spatial import run_spatial_landscape_simulation
from .invasive_model import calculate_invasive_impact_score


SCENARIO_DEFINITIONS = [
    {
        "id": "scenario_baseline",
        "name": "1. Baseline / No Intervention",
        "description": "Status-quo passive management without invasive control or active restoration.",
        "stress_mod": 0.10, "inv_pressure": 1.0, "removal_rate": 0.0, "restoration_boost": 0.0,
        "suitability": 0.85
    },
    {
        "id": "scenario_edrr",
        "name": "2. Early Detection & Rapid Response (EDRR)",
        "description": "Rapid localized eradication of new colonization foci before extensive seed bank formation.",
        "stress_mod": 0.10, "inv_pressure": 0.35, "removal_rate": 0.40, "restoration_boost": 0.10,
        "suitability": 0.85
    },
    {
        "id": "scenario_containment",
        "name": "3. Containment & Perimeter Buffer",
        "description": "Establishment of 100m containment buffer strips around core forest zones to arrest front expansion.",
        "stress_mod": 0.10, "inv_pressure": 0.50, "removal_rate": 0.25, "restoration_boost": 0.05,
        "suitability": 0.85
    },
    {
        "id": "scenario_mechanical_crd",
        "name": "4. Mechanical Rootstock Removal (CRD Method)",
        "description": "Cut-Rootstock-Deposition method targeting subterranean root crowns of invasive thickets.",
        "stress_mod": 0.15, "inv_pressure": 0.40, "removal_rate": 0.65, "restoration_boost": 0.15,
        "suitability": 0.85
    },
    {
        "id": "scenario_restoration",
        "name": "5. Active Native Succession Restoration",
        "description": "Dense enrichment planting of native climax shade trees and fast-growing understory bamboos.",
        "stress_mod": 0.08, "inv_pressure": 0.70, "removal_rate": 0.20, "restoration_boost": 0.55,
        "suitability": 0.90
    },
    {
        "id": "scenario_climate_stress",
        "name": "6. Climate Warming Stress (+2.0°C)",
        "description": "Projected climate warming exacerbating vapor pressure deficit and water stress on native timber.",
        "stress_mod": 0.45, "inv_pressure": 1.40, "removal_rate": 0.0, "restoration_boost": -0.15,
        "suitability": 0.70
    },
    {
        "id": "scenario_drought",
        "name": "7. Severe Multi-Year Drought Stress",
        "description": "Consecutive sub-normal monsoon seasons impairing native seedling recruitment.",
        "stress_mod": 0.60, "inv_pressure": 1.25, "removal_rate": 0.0, "restoration_boost": -0.25,
        "suitability": 0.60
    },
    {
        "id": "scenario_wildfire",
        "name": "8. Severe Wildfire Disturbance Event",
        "description": "Ground fires opening canopy gaps and triggering rapid post-fire invasive sprouting.",
        "stress_mod": 0.70, "inv_pressure": 1.80, "removal_rate": 0.0, "restoration_boost": -0.30,
        "suitability": 0.65
    },
    {
        "id": "scenario_high_pressure",
        "name": "9. High Invasive Propagule Pressure",
        "description": "Adjacent agricultural fringe and road networks driving persistent propagule influx.",
        "stress_mod": 0.15, "inv_pressure": 2.20, "removal_rate": 0.0, "restoration_boost": 0.0,
        "suitability": 0.85
    },
    {
        "id": "scenario_integrated",
        "name": "10. Integrated Control + Active Restoration Policy",
        "description": "Holistic combination of mechanical removal, biological barrier plantings, native seeding, and long-term surveillance.",
        "stress_mod": 0.05, "inv_pressure": 0.20, "removal_rate": 0.80, "restoration_boost": 0.65,
        "suitability": 0.92
    }
]


def evaluate_all_scenarios(
    grid_size: int = 25,
    years: int = 30,
    baseline_native: float = 145.0,
    baseline_competing: float = 28.0,
    baseline_invasive: float = 4.0
) -> List[Dict[str, Any]]:
    """
    Executes simulations for all 10 management scenarios by varying physical & biological parameters,
    computing stability metrics, Jacobian verification, and carbon dynamics for each.
    """
    results = []

    for sc in SCENARIO_DEFINITIONS:
        # 1. Run dynamic landscape simulation
        sim = run_spatial_landscape_simulation(
            grid_size=grid_size,
            years=years,
            dt=0.1,
            initial_native=baseline_native * (1.0 + sc["restoration_boost"]),
            initial_competing=baseline_competing,
            initial_invasive=baseline_invasive * sc["inv_pressure"] * max(0.1, 1.0 - sc["removal_rate"]),
            invasive_pressure=sc["inv_pressure"]
        )

        final_native = float(sim["biomass_series"]["native"][-1])
        final_competing = float(sim["biomass_series"]["competing"][-1])
        final_invasive = float(sim["biomass_series"]["invasive"][-1])
        final_cov = float(sim["invasive_coverage_series"][-1])
        total_agb = round(final_native + final_competing + final_invasive, 2)
        carbon_stock = round(total_agb * 0.47, 2)

        # 2. Build calibrated parameters and compute final stability
        params = build_calibrated_parameters(
            suitability=sc.get("suitability", 0.85),
            stress=sc["stress_mod"],
            invasive_pressure=sc["inv_pressure"]
        )
        final_state = np.array([final_native, final_competing, final_invasive], dtype=float)
        stability = calculate_stability_metrics(final_state, params, dt=0.1)

        # 3. Compute Invasive Impact Score
        iis = calculate_invasive_impact_score(
            native_initial_biomass=baseline_native,
            native_final_biomass=final_native,
            invasive_final_biomass=final_invasive,
            invasive_max_capacity=65.0,
            invasive_coverage_pct=final_cov,
            spread_rate_m_yr=18.0 * sc["inv_pressure"],
            initial_shannon=0.92,
            final_shannon=max(0.2, 0.92 - (final_cov / 100.0) * 0.45)
        )

        results.append({
            "id": sc["id"],
            "name": sc["name"],
            "description": sc["description"],
            "final_native_biomass": final_native,
            "final_competing_biomass": final_competing,
            "final_invasive_biomass": final_invasive,
            "final_total_biomass": total_agb,
            "final_carbon_stock_mg_c_ha": carbon_stock,
            "final_invasive_coverage_pct": final_cov,
            "spectral_radius": stability["spectral_radius"],
            "stability_class": stability["stability_class"],
            "stability_label": stability["stability_label"],
            "continuous_eigenvalues": stability["continuous_eigenvalues"],
            "discrete_eigenvalues": stability["discrete_eigenvalues"],
            "verification": stability["verification"],
            "iis_score": iis["invasive_impact_score"],
            "risk_category": iis["risk_category"],
            "risk_color": iis["risk_color"],
            "timelines": sim["timelines"],
            "biomass_series": sim["biomass_series"],
            "coverage_series": sim["invasive_coverage_series"],
            "provenance": {
                "simulation_type": "Coupled Dynamic Parameter Variation",
                "carbon_stock_eq": "Carbon (Mg C/ha) = Aboveground Biomass * 0.47 (IPCC 2006 / FSI)",
                "stability_eq": "rho(J_map) = max |lambda_i| from J_map = I + dt * J_F",
                "verification_status": stability["verification"]["status"]
            }
        })

    # Sort scenarios from lowest risk (best ecological outcome) to highest risk
    results.sort(key=lambda x: x["iis_score"])
    return results
