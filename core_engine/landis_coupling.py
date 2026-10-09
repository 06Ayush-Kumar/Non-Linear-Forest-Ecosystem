"""
LANDIS-II Coupling & Scientific Stability Analysis Pipeline.
Connects the official LANDIS-II landscape simulation engine to our original
Nonlinear 3-State Population Dynamics, Jacobian, Eigenvalue, and Stability Analysis layer.

Scientific Separation:
  - LANDIS-II simulates spatial forest landscape succession, cohorts, and disturbance.
  - Our scientific layer performs mathematical stability analysis (Continuous/Discrete Jacobian,
    eigenvalues, spectral radius, finite-difference verification) on variables derived from LANDIS-II outputs.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

import uuid
import json
import time
from datetime import datetime

from .landis_executor import is_landis_installed, execute_landis_simulation, prepare_landis_run_directory, create_fresh_scenario_directory
from .landis_parser import parse_landis_output_directory, extract_three_state_variables
from .model import EcologicalParameters, build_calibrated_parameters, ecological_derivatives
from .jacobian import analytical_continuous_jacobian, discrete_jacobian_map, verify_jacobian
from .stability import calculate_stability_metrics, find_system_equilibria


def run_coupled_landis_stability_pipeline(
    scenario_path: str | Path,
    working_dir: str | Path,
    suitability: float = 0.85,
    stress: float = 0.15,
    invasive_pressure: float = 1.0,
    dt: float = 0.1,
    simulation_id: Optional[str] = None,
    create_isolated_dir: bool = False,
    area_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Complete end-to-end pipeline:
    1. On Linux/cloud: Never executes native engine, returns clean UNAVAILABLE_ON_LINUX structure.
    2. On Windows: Optionally creates a fresh isolated run directory with input/, output/, logs/, metadata/.
    3. Executes the official LANDIS-II simulation.
    4. Parses actual newly generated output CSV logs and GeoTIFF maps.
    5. Extracts state variables [x, y, z] across time steps.
    6. Evaluates continuous & discrete Jacobian, eigenvalues, and spectral radius for each step.
    7. Runs numerical finite-difference cross-check.
    8. Returns structured scientific results with full provenance.
    """
    # 1. Platform Detection
    if not sys.platform.startswith("win"):
        return {
            "success": False,
            "status": "UNAVAILABLE_ON_LINUX",
            "execution_available": False,
            "reason": "Native Landscape Engine requires Windows runtime.",
            "error": "Native Landscape Engine requires Windows .NET/GDAL runtime. This Linux cloud deployment executes the Layer 2/3 Reduced-Order Spatial Simulator.",
            "platform": "Linux",
            "execution": {
                "success": False,
                "status": "UNAVAILABLE_ON_LINUX",
                "execution_available": False,
                "reason": "Native Landscape Engine requires Windows runtime.",
                "return_code": None,
                "duration_seconds": None,
                "stdout": "",
                "stderr": "NATIVE_LANDSCAPE_ENGINE_UNAVAILABLE_ON_LINUX"
            },
            "stability_trajectory": [],
            "provenance": {
                "engine": "LANDIS-II v7.0",
                "platform": "Linux",
                "status": "UNAVAILABLE_ON_LINUX"
            }
        }

    if not is_landis_installed():
        return {
            "success": False,
            "status": "NEEDS_BUILD",
            "execution_available": False,
            "reason": "LANDIS-II executable not found in build_landis/bin.",
            "error": "LANDIS-II executable not found in build_landis/bin.",
            "execution": {
                "success": False,
                "status": "NEEDS_BUILD",
                "execution_available": False,
                "reason": "LANDIS-II executable not found in build_landis/bin.",
                "return_code": -1,
                "duration_seconds": 0.0,
                "stdout": "",
                "stderr": "LANDIS_EXE_NOT_FOUND"
            },
            "stability_trajectory": [],
            "provenance": {
                "engine": "LANDIS-II v7.0",
                "status": "NEEDS_BUILD"
            }
        }

    t_start = time.time()
    if not simulation_id:
        area_tag = area_id if area_id else "sim"
        simulation_id = f"landis_{area_tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"

    working_path = Path(working_dir).resolve()
    scenario_file = Path(scenario_path).name

    if create_isolated_dir:
        from .landis_executor import RUNS_DIR
        target_run_dir = RUNS_DIR / simulation_id
        if working_path.exists():
            create_fresh_scenario_directory(working_path, target_run_dir)
            working_path = target_run_dir

    # 1. Execute LANDIS-II
    exec_result = execute_landis_simulation(
        scenario_file=scenario_file,
        working_dir=working_path,
        timeout_seconds=240
    )

    # Save log file in working directory logs subfolder
    logs_dir = working_path / "logs"
    os.makedirs(logs_dir, exist_ok=True)
    with open(logs_dir / "execution.log", "w", encoding="utf-8") as f_log:
        f_log.write(f"Simulation ID: {simulation_id}\n")
        f_log.write(f"Command: {exec_result.get('command')}\n")
        f_log.write(f"Duration: {exec_result.get('duration_seconds')} s\n")
        f_log.write(f"Return Code: {exec_result.get('return_code')}\n\nSTDOUT:\n")
        f_log.write(exec_result.get("stdout", ""))
        f_log.write("\n\nSTDERR:\n")
        f_log.write(exec_result.get("stderr", ""))

    if not exec_result["success"]:
        return {
            "success": False,
            "simulation_id": simulation_id,
            "error": exec_result.get("error", "LANDIS-II execution failed."),
            "execution": exec_result,
            "stability_trajectory": [],
            "provenance": {
                "engine": "LANDIS-II v7.0",
                "status": "EXECUTION_FAILED"
            }
        }

    # 2. Parse LANDIS-II Outputs
    parsed = parse_landis_output_directory(working_path)

    state_traj = parsed.get("state_trajectory", [])

    if not state_traj:
        return {
            "success": False,
            "error": "No state trajectory could be extracted from LANDIS-II output files.",
            "execution": exec_result,
            "parsed_output": parsed,
            "stability_trajectory": []
        }

    # 3. Build scientific model parameters
    params = build_calibrated_parameters(
        suitability=suitability,
        stress=stress,
        invasive_pressure=invasive_pressure
    )

    # 4. Evaluate Jacobian and Stability for each time step in the trajectory
    stability_trajectory = []
    for point in state_traj:
        year = point["year"]
        x = point["x_native_canopy_mg_ha"]
        y = point["y_understory_mg_ha"]
        z = point["z_invasive_mg_ha"]

        state_vec = np.array([x, y, z], dtype=float)
        metrics = calculate_stability_metrics(state_vec, params, dt=dt)

        stability_trajectory.append({
            "year": year,
            "state": {
                "x_native_canopy_mg_ha": x,
                "y_understory_mg_ha": y,
                "z_invasive_mg_ha": z,
                "total_biomass_mg_ha": point["total_biomass_mg_ha"],
                "carbon_stock_mg_c_ha": point["carbon_stock_mg_c_ha"]
            },
            "spectral_radius": metrics["spectral_radius"],
            "stability_class": metrics["stability_class"],
            "stability_label": metrics["stability_label"],
            "risk_color": metrics["risk_color"],
            "continuous_eigenvalues": metrics["continuous_eigenvalues"],
            "discrete_eigenvalues": metrics["discrete_eigenvalues"],
            "jacobian_continuous": metrics["jacobian_continuous"],
            "jacobian_discrete": metrics["jacobian_discrete"],
            "verification": metrics["verification"],
            "provenance": {
                "input_source": "LANDIS-II Output (spp-biomass-log.csv)",
                "mathematical_model": "3-State Coupled Nonlinear ODE Stability Layer",
                "continuous_jacobian_eq": "J_F = [df_i/dx_j]",
                "discrete_map_eq": "J_map = I + dt * J_F",
                "spectral_radius_eq": "rho(J_map) = max |lambda_i|",
                "stability_criterion": "rho < 1.0 (Locally Asymptotically Stable)",
                "carbon_stock_eq": "Carbon (Mg C/ha) = Total Biomass * 0.47 (IPCC 2006; FSI)",
                "dt": dt
            }
        })

    equilibria = find_system_equilibria(params)

    # Save metadata JSON file in working directory metadata subfolder
    metadata_dir = working_path / "metadata"
    os.makedirs(metadata_dir, exist_ok=True)
    sim_meta = {
        "simulation_id": simulation_id,
        "timestamp": datetime.now().isoformat(),
        "working_directory": str(working_path),
        "execution_duration_seconds": exec_result.get("duration_seconds"),
        "return_code": exec_result.get("return_code"),
        "raster_maps_generated": parsed.get("raster_maps_count", 0),
        "trajectory_timesteps": len(stability_trajectory),
        "parameters": {
            "suitability": suitability,
            "stress": stress,
            "invasive_pressure": invasive_pressure,
            "dt": dt
        }
    }
    with open(metadata_dir / "simulation_metadata.json", "w", encoding="utf-8") as f_meta:
        json.dump(sim_meta, f_meta, indent=2)

    return {
        "success": True,
        "simulation_id": simulation_id,
        "working_directory": str(working_path),
        "execution": exec_result,
        "parsed_output": {
            "biomass_log_count": len(parsed.get("biomass_log", [])),
            "raster_maps_count": parsed.get("raster_maps_count", 0),
            "species_tracked": list(parsed.get("species_log", {}).get("species_data", {}).keys())
        },
        "stability_trajectory": stability_trajectory,
        "equilibria": equilibria,
        "model_parameters": {
            "growth_rates": params.growth_rates.tolist(),
            "carrying_capacities": params.carrying_capacities.tolist(),
            "competition_matrix": params.competition_matrix.tolist(),
            "suitability": params.climate_suitability,
            "stress": params.environmental_stress,
            "invasive_pressure": params.invasive_pressure
        },
        "scientific_separation_note": (
            "Forest landscape dynamics simulated by LANDIS-II v7; "
            "Jacobian eigenvalues and spectral radius calculated by the scientific mathematical stability layer."
        )
    }

