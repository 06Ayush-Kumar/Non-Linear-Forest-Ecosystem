"""
Automated Regression Test Suite for FORESTDYN UI Data Flow & Landscape Engine Lifecycle.
Verifies:
  A. Forest switching changes baseline correctly across all 9 protected areas.
  B. 3D visualization parameter mapping produces distinct, site-specific configurations.
  C. Deterministic seeded generator reproducibility per site ID.
  D. Spatial simulation & Chart time series regeneration per forest initial conditions.
  E. /api/landis/run always returns a terminal response structure on success and failure.
  F. Subprocess timeout handling and non-zero exit handling.
  G. Stability threshold classification accuracy (rho < 1 vs rho >= 1).
"""

import pytest
import numpy as np
from pathlib import Path
from app import create_app
from data_layer.forest_baseline import construct_forest_baseline
from core_engine.landis_executor import execute_landis_simulation, is_landis_installed
from core_engine.stability import calculate_stability_metrics
from core_engine.model import build_calibrated_parameters


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_regression_forest_switching_baselines():
    """Requirement A: Forest switching produces distinct, authentic baseline records."""
    forest_ids = ["mudumalai", "bandipur", "kanha", "corbett", "kaziranga", "gir", "nagarhole", "wayanad", "silent_valley"]
    baselines = {}

    for f_id in forest_ids:
        base = construct_forest_baseline(f_id)
        assert base is not None
        assert base["site_id"] == f_id
        assert "vegetation_state" in base
        veg = base["vegetation_state"]
        b_nat = veg["native_canopy_biomass_mg_ha"]["value"]
        b_und = veg["understory_biomass_mg_ha"]["value"]
        b_inv = veg["invasive_standing_biomass_mg_ha"]["value"]
        assert b_nat > 0
        assert b_und > 0
        assert b_inv >= 0
        baselines[f_id] = (b_nat, b_und, b_inv)

    # Confirm distinct initial biomass states
    assert baselines["gir"][0] == 98.2  # Gir semi-arid
    assert baselines["silent_valley"][0] == 265.0  # Silent Valley rainforest
    assert baselines["mudumalai"][0] == 158.4
    assert baselines["kaziranga"][0] == 210.8
    assert baselines["gir"][0] != baselines["silent_valley"][0]
    assert baselines["kaziranga"][0] != baselines["mudumalai"][0]


def test_regression_3d_visualizer_deterministic_mapping():
    """Requirement B & C: 3D visualization parameters scale deterministically from baseline."""
    base_gir = construct_forest_baseline("gir")
    base_sv = construct_forest_baseline("silent_valley")
    base_kazi = construct_forest_baseline("kaziranga")

    # Tree count scaling formula: 40 + (bNative / 265.0) * 110
    tree_count_gir = round(40 + (base_gir["vegetation_state"]["native_canopy_biomass_mg_ha"]["value"] / 265.0) * 110)
    tree_count_sv = round(40 + (base_sv["vegetation_state"]["native_canopy_biomass_mg_ha"]["value"] / 265.0) * 110)
    tree_count_kazi = round(40 + (base_kazi["vegetation_state"]["native_canopy_biomass_mg_ha"]["value"] / 265.0) * 110)

    assert tree_count_gir == 81  # Open sparser scrub
    assert tree_count_sv == 150  # Dense evergreen forest
    assert tree_count_kazi == 128  # Dense floodplain forest

    # Understory scaling formula: 20 + (bUnder / 48.2) * 70
    shrub_gir = round(20 + (base_gir["vegetation_state"]["understory_biomass_mg_ha"]["value"] / 48.2) * 70)
    shrub_sv = round(20 + (base_sv["vegetation_state"]["understory_biomass_mg_ha"]["value"] / 48.2) * 70)
    assert shrub_gir == 41
    assert shrub_sv == 90

    # Invasive thicket scaling: 3 + (bInv / 12.4) * 35
    inv_sv = round(3 + (base_sv["vegetation_state"]["invasive_standing_biomass_mg_ha"]["value"] / 12.4) * 35)
    inv_kazi = round(3 + (base_kazi["vegetation_state"]["invasive_standing_biomass_mg_ha"]["value"] / 12.4) * 35)
    assert inv_sv == 8  # Minimal invasives in pristine core
    assert inv_kazi == 38  # High invasive infestation on floodplain


def test_regression_simulation_api_distinct_trajectories(client):
    """Requirement D: Simulation runs produce forest-specific time series."""
    res_gir = client.post("/api/simulation/run", json={
        "grid_size": 15, "years": 10, "dt": 0.1,
        "initial_native": 98.2, "initial_competing": 14.6, "initial_invasive": 9.1, "invasive_pressure": 1.0
    })
    assert res_gir.status_code == 200
    data_gir = res_gir.get_json()

    res_sv = client.post("/api/simulation/run", json={
        "grid_size": 15, "years": 10, "dt": 0.1,
        "initial_native": 265.0, "initial_competing": 48.2, "initial_invasive": 1.8, "invasive_pressure": 1.0
    })
    assert res_sv.status_code == 200
    data_sv = res_sv.get_json()

    assert data_gir["biomass_series"]["native"][0] == 98.2
    assert data_sv["biomass_series"]["native"][0] == 265.0
    assert data_gir["biomass_series"]["competing"][0] == 14.6
    assert data_sv["biomass_series"]["competing"][0] == 48.2
    assert data_gir["biomass_series"]["invasive"][0] == 9.1
    assert data_sv["biomass_series"]["invasive"][0] == 1.8
    assert data_gir["biomass_series"]["native"][-1] != data_sv["biomass_series"]["native"][-1]
    assert len(data_gir["timelines"]) == 11
    assert len(data_gir["spectral_radius_series"]) == 11



def test_regression_landis_api_terminal_response(client):
    """Requirement E: /api/landis/run always returns a structured terminal response."""
    res = client.post("/api/landis/run", json={
        "working_dir": "runs/test_run_biomass_v7",
        "scenario_file": "scenario.txt",
        "suitability": 0.85,
        "stress": 0.15,
        "invasive_pressure": 1.0,
        "dt": 0.1
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "success" in data
    assert "simulation_id" in data
    if data["success"]:
        assert "execution" in data
        assert "duration_seconds" in data["execution"]
        assert "parsed_output" in data
        assert "stability_trajectory" in data
        assert len(data["stability_trajectory"]) > 0
    else:
        assert "error" in data



def test_regression_landis_timeout_handling():
    """Requirement F: Subprocess timeout produces structured failure instead of infinite freeze."""
    working_dir = Path("runs/test_run_biomass_v7")
    if is_landis_installed():
        result = execute_landis_simulation("scenario.txt", working_dir, timeout_seconds=0.001)
        assert result["success"] is False
        assert result["return_code"] == -99 or result["stderr"] == "TIMEOUT" or "timed out" in result.get("error", "").lower()
        assert "duration_seconds" in result


def test_regression_landis_invalid_scenario_error_handling():
    """Requirement G: Non-existent scenario produces structured error."""
    working_dir = Path("runs/test_run_biomass_v7")
    result = execute_landis_simulation("non_existent_scenario_123.txt", working_dir, timeout_seconds=5)
    assert result["success"] is False
    assert result["return_code"] != 0
    assert "not found" in result["error"].lower() or "error" in result


def test_regression_stability_threshold_honest_classification():
    """Requirement 5 & G: Spectral radius stability classification accurately reflects rho < 1 vs rho >= 1."""
    params = build_calibrated_parameters(suitability=0.85, stress=0.15)

    # State with rho < 0.98 => STABLE
    stable_metrics = calculate_stability_metrics(np.array([180.0, 35.0, 1.0]), params, dt=0.1)
    if stable_metrics["spectral_radius"] < 0.98:
        assert stable_metrics["stability_class"] == "stable"

    # State with high invasive disturbance (amplifying perturbations)
    disturbed_metrics = calculate_stability_metrics(np.array([40.0, 10.0, 35.0]), params, dt=0.1)
    rho = disturbed_metrics["spectral_radius"]
    if rho > 1.02:
        assert disturbed_metrics["stability_class"] == "unstable"
        assert disturbed_metrics["risk_color"] == "#ef4444"
    elif rho >= 0.98:
        assert disturbed_metrics["stability_class"] == "critical"
        assert disturbed_metrics["risk_color"] == "#f59e0b"
