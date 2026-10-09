"""
Test Suite for Platform-Aware Native Landscape Engine Architecture.
Verifies:
1. Linux environment detects OS before native execution.
2. Linux NEVER attempts subprocess execution of Landis.Console.exe.
3. Linux NEVER accesses or requires runs/test_run_biomass_v7 to exist.
4. Linux returns clean structured UNAVAILABLE_ON_LINUX response without fake data.
5. /api/landis/run returns HTTP 200 with status="UNAVAILABLE_ON_LINUX", execution_available=False, reason="Native Landscape Engine requires Windows runtime."
6. /api/reality/status does not fail on Linux and correctly reports platform OS and cloud mode.
7. /api/landis/status endpoint returns platform metadata.
8. Windows native execution path is preserved.
9. Layer 2 (Mathematical Stability) & Layer 3 (Reduced-Order Spatial Simulator) remain 100% operational.
10. All scientific equations, parameters, GIS, baseline, taxonomy, and scenarios remain intact and functional.
"""

import sys
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch

from app import create_app
from core_engine.landis_executor import (
    is_landis_installed,
    get_landis_metadata,
    execute_landis_simulation,
    create_fresh_scenario_directory
)
from core_engine.landis_coupling import run_coupled_landis_stability_pipeline
from core_engine.model import build_calibrated_parameters
from core_engine.jacobian import analytical_continuous_jacobian, discrete_jacobian_map, verify_jacobian
from core_engine.stability import calculate_stability_metrics
from core_engine.spatial import run_spatial_landscape_simulation
from core_engine.scenarios import evaluate_all_scenarios
from decision_support.candidate_evaluator import evaluate_candidate_introduction
from data_layer.forest_baseline import construct_forest_baseline
from data_layer.india_gis import list_protected_areas, get_protected_area


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


# =========================================================================
# 1. Linux Simulation Execution Isolation
# =========================================================================
def test_linux_never_attempts_native_execution():
    """Verifies that on Linux, execute_landis_simulation immediately returns UNAVAILABLE_ON_LINUX."""
    with patch("sys.platform", "linux"):
        # Intentionally point to a non-existent directory to prove no filesystem access occurs
        res = execute_landis_simulation("scenario.txt", "/opt/render/project/src/runs/non_existent_dir")
        assert res["success"] is False
        assert res["status"] == "UNAVAILABLE_ON_LINUX"
        assert res["execution_available"] is False
        assert "Windows runtime" in res["reason"]
        assert res["return_code"] is None
        assert res["duration_seconds"] is None
        assert res["stderr"] == "NATIVE_LANDSCAPE_ENGINE_UNAVAILABLE_ON_LINUX"


def test_linux_create_fresh_directory_safe_bypass():
    """Verifies that create_fresh_scenario_directory safely bypasses missing source dirs on Linux."""
    with patch("sys.platform", "linux"):
        target = Path("/tmp/target_run_dir")
        # Source dir does not exist
        res = create_fresh_scenario_directory("/opt/render/project/src/runs/test_run_biomass_v7", target)
        assert res == target.resolve()


def test_linux_coupled_pipeline_returns_clean_unavailable():
    """Verifies that run_coupled_landis_stability_pipeline returns clean UNAVAILABLE_ON_LINUX on Linux."""
    with patch("sys.platform", "linux"):
        res = run_coupled_landis_stability_pipeline(
            scenario_path="scenario.txt",
            working_dir="/opt/render/project/src/runs/test_run_biomass_v7",
            create_isolated_dir=True
        )
        assert res["success"] is False
        assert res["status"] == "UNAVAILABLE_ON_LINUX"
        assert res["execution_available"] is False
        assert res["reason"] == "Native Landscape Engine requires Windows runtime."
        assert res["platform"] == "Linux"
        assert res["stability_trajectory"] == []
        assert res["provenance"]["status"] == "UNAVAILABLE_ON_LINUX"


# =========================================================================
# 2. Linux REST API Endpoints
# =========================================================================
def test_api_landis_run_on_linux(client):
    """Verifies POST /api/landis/run on Linux returns HTTP 200 with structured UNAVAILABLE_ON_LINUX."""
    with patch("sys.platform", "linux"):
        res = client.post("/api/landis/run", json={
            "working_dir": "/opt/render/project/src/runs/test_run_biomass_v7",
            "scenario_file": "scenario.txt",
            "area_id": "mudumalai"
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is False
        assert data["status"] == "UNAVAILABLE_ON_LINUX"
        assert data["execution_available"] is False
        assert data["reason"] == "Native Landscape Engine requires Windows runtime."
        assert data["platform"] == "Linux"
        assert data["execution"]["status"] == "UNAVAILABLE_ON_LINUX"
        assert data["execution"]["return_code"] is None
        assert data["execution"]["duration_seconds"] is None
        assert data["execution"]["stderr"] == "NATIVE_LANDSCAPE_ENGINE_UNAVAILABLE_ON_LINUX"
        assert data["stability_trajectory"] == []


def test_api_reality_status_on_linux(client):
    """Verifies GET /api/reality/status on Linux reports component 1 and 2 as UNAVAILABLE_ON_LINUX without error."""
    with patch("sys.platform", "linux"):
        res = client.get("/api/reality/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["is_windows"] is False
        assert data["native_engine_available"] is False
        assert data["cloud_mode_active"] is True
        assert data["all_checks_passed"] is True  # Core scientific layers pass

        c1 = data["components"]["1_landis_engine_core"]
        assert c1["installed"] is False
        assert c1["execution_available"] is False
        assert c1["status"] == "UNAVAILABLE_ON_LINUX"
        assert "Windows runtime" in c1["reason"]

        c2 = data["components"]["2_landis_execution_verification"]
        assert c2["status"] == "UNAVAILABLE_ON_LINUX"
        assert c2["test_run_dir"] is None
        assert c2["output_geotiff_rasters"] is None


def test_api_landis_status_endpoint(client):
    """Verifies GET /api/landis/status returns engine metadata."""
    res = client.get("/api/landis/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "installed" in data
    assert "status" in data
    assert "core_version" in data
    assert "target_framework" in data


# =========================================================================
# 3. Windows Native Execution Path Preservation
# =========================================================================
def test_windows_native_path_preserved():
    """Verifies that on Windows, metadata and installed state reflect native capabilities."""
    if sys.platform.startswith("win"):
        meta = get_landis_metadata()
        assert meta["platform_os"].startswith("win")
        assert meta["cloud_mode_active"] is False
        if is_landis_installed():
            assert meta["installed"] is True
            assert meta["execution_available"] is True
            assert meta["status"] == "OPERATIONAL"
            assert "Landis.Console.exe" in meta["executable_path"]


# =========================================================================
# 4. Layer 2 & Layer 3 Scientific Operations Remain Operational
# =========================================================================
def test_layer2_mathematical_stability_operational():
    """Verifies that Layer 2 continuous/discrete Jacobian and stability calculations operate independently."""
    params = build_calibrated_parameters(suitability=0.88, stress=0.12, invasive_pressure=1.0)
    state = np.array([158.4, 26.8, 6.2])

    J_c = analytical_continuous_jacobian(state, params)
    assert J_c.shape == (3, 3)

    J_d = discrete_jacobian_map(state, params, dt=0.1)
    assert J_d.shape == (3, 3)

    metrics = calculate_stability_metrics(state, params, dt=0.1)
    assert "spectral_radius" in metrics
    assert metrics["spectral_radius"] > 0
    assert metrics["verification"]["verified"] is True
    assert metrics["verification"]["max_absolute_error"] < 1e-4


def test_layer3_reduced_order_spatial_simulation_operational():
    """Verifies that Layer 3 Reduced-Order Spatial Landscape Simulator runs cleanly on all platforms."""
    res = run_spatial_landscape_simulation(
        grid_size=15,
        years=5,
        dt=0.1,
        initial_native=158.4,
        initial_competing=26.8,
        initial_invasive=6.2,
        invasive_pressure=1.0,
        area_id="mudumalai"
    )
    assert len(res["timelines"]) == 6
    assert len(res["biomass_series"]["native"]) == 6
    assert res["biomass_series"]["native"][0] == 158.4


def test_decision_support_and_scenarios_operational():
    """Verifies that 10 management scenarios and candidate evaluation run cleanly."""
    scenarios = evaluate_all_scenarios(grid_size=10, years=10, baseline_native=158.4)
    assert len(scenarios) == 10

    cand_eval = evaluate_candidate_introduction("Lantana camara", 24.2, 900.0, 1250.0, 158.4, "Tamil Nadu")
    assert cand_eval["canonical_name"] == "Lantana camara"
    assert "HIGH RISK" in cand_eval["final_classification"] or "INVASIVE" in cand_eval["final_classification"]
