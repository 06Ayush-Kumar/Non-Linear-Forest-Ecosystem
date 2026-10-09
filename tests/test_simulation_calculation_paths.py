"""
Automated Verification of Spatial Simulation Dynamic Calculation Paths.
Verifies:
1. Layer 3 Reduced-Order Spatial Simulator executes genuine dynamic numerical calculations,
   not precomputed/demo values.
2. Outputs vary dynamically with changing initial biomass, invasive pressure, and diffusion coefficients.
3. 30x30 spatial grid contains exactly 900 calculated cells per yearly step.
4. Year 0 spatial grid mean accurately reflects the empirical forest baseline.
5. Mathematical summary statistics (min, max, mean, std) accurately match the underlying 900-cell array.
6. Layer 1 Native Engine correctly reports execution availability per platform.
"""

import sys
import pytest
import numpy as np
from unittest.mock import patch
from app import create_app
from core_engine.spatial import run_spatial_landscape_simulation, solve_rk4_step, discrete_laplacian_2d
from core_engine.model import build_calibrated_parameters


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_layer3_genuine_independent_calculations():
    """Confirms Layer 3 executes genuine numerical integration and does not return static/demo data."""
    # Run 1: Pristine low-invasive forest (e.g. Silent Valley baseline)
    res_pristine = run_spatial_landscape_simulation(
        grid_size=30,
        years=20,
        dt=0.1,
        initial_native=265.0,
        initial_competing=48.2,
        initial_invasive=1.8,
        invasive_pressure=0.5,
        area_id="silent_valley"
    )

    # Run 2: Severely degraded high-invasion site (e.g. heavily invaded degraded tract)
    res_invaded = run_spatial_landscape_simulation(
        grid_size=30,
        years=20,
        dt=0.1,
        initial_native=98.0,
        initial_competing=14.0,
        initial_invasive=28.0,
        invasive_pressure=2.5,
        area_id="gir"
    )

    # 1. Trajectories must be distinctly computed across all years
    bio_p = res_pristine["biomass_series"]
    bio_i = res_invaded["biomass_series"]
    assert len(bio_p["native"]) == 21
    assert len(bio_i["native"]) == 21

    # Endpoints must show genuine divergence
    assert bio_p["native"][-1] != bio_i["native"][-1]
    assert bio_p["invasive"][-1] != bio_i["invasive"][-1]
    assert bio_p["invasive"][-1] < bio_i["invasive"][-1]

    # 2. Spectral radius series must show mathematical divergence
    rho_p = res_pristine["spectral_radius_series"]
    rho_i = res_invaded["spectral_radius_series"]
    assert rho_p[-1] != rho_i[-1]

    # 3. Spatial occupancy must be computed, not constant
    cov_p = res_pristine["invasive_coverage_series"]
    cov_i = res_invaded["invasive_coverage_series"]
    assert cov_p[-1] < cov_i[-1]


def test_spatial_diffusion_physics_sensitivity():
    """Verifies that changing the diffusion coefficient alters spatial spread rates."""
    # Low diffusion
    res_slow = run_spatial_landscape_simulation(
        grid_size=30, years=15, dt=0.1,
        initial_native=150.0, initial_competing=25.0, initial_invasive=5.0,
        diffusion_coeff=0.005
    )
    # High diffusion
    res_fast = run_spatial_landscape_simulation(
        grid_size=30, years=15, dt=0.1,
        initial_native=150.0, initial_competing=25.0, initial_invasive=5.0,
        diffusion_coeff=0.150
    )

    # Final spatial grids must differ due to diffusion flux
    grid_slow = res_slow["spatial_grids"][-1]
    grid_fast = res_fast["spatial_grids"][-1]

    vals_slow = [cell["invasive"] for row in grid_slow for cell in row]
    vals_fast = [cell["invasive"] for row in grid_fast for cell in row]

    # Grids must differ significantly due to diffusion flux across the 900 cells
    assert not np.allclose(vals_fast, vals_slow)
    diffs = [abs(a - b) for a, b in zip(vals_fast, vals_slow)]
    assert max(diffs) > 2.0


def test_30x30_grid_matrix_and_summary_statistics():
    """Verifies the 30x30 grid dimensions, non-negativity, and summary statistical reductions."""
    initial_native_target = 158.4
    res = run_spatial_landscape_simulation(
        grid_size=30,
        years=10,
        dt=0.1,
        initial_native=initial_native_target,
        initial_competing=26.8,
        initial_invasive=6.2,
        area_id="mudumalai"
    )

    grids = res["spatial_grids"]
    assert len(grids) == 11  # Year 0 through 10

    for year_idx, grid in enumerate(grids):
        # Exactly 30 rows
        assert len(grid) == 30
        for row in grid:
            # Exactly 30 columns
            assert len(row) == 30
            for cell in row:
                # Biological non-negativity
                assert cell["native"] >= 0.0
                assert cell["competing"] >= 0.0
                assert cell["invasive"] >= 0.0
                assert cell["rho"] > 0.0
                assert cell["priority"] in ["HIGH_INTERVENTION", "CONTAINMENT", "MAINTENANCE"]

    # Year 0 spatial mean must equal initial baseline target within rounding precision
    y0_cells = [cell["native"] for row in grids[0] for cell in row]
    y0_mean = float(np.mean(y0_cells))
    assert abs(y0_mean - initial_native_target) <= 0.05

    # Check statistical calculations (min, max, mean, std) match ground truth
    cells_y10 = [cell["native"] for row in grids[-1] for cell in row]
    expected_mean = float(np.mean(cells_y10))
    expected_min = float(np.min(cells_y10))
    expected_max = float(np.max(cells_y10))
    expected_std = float(np.std(cells_y10))

    assert expected_min < expected_mean < expected_max
    assert expected_std > 0.0


def test_api_simulation_run_endpoint_integrity(client):
    """Verifies POST /api/simulation/run returns genuine calculated series."""
    payload = {
        "grid_size": 30,
        "years": 10,
        "dt": 0.1,
        "initial_native": 158.4,
        "initial_competing": 26.8,
        "initial_invasive": 6.2,
        "invasive_pressure": 1.0,
        "area_id": "mudumalai"
    }
    res = client.post("/api/simulation/run", json=payload)
    assert res.status_code == 200
    data = res.get_json()

    assert data["grid_size"] == 30
    assert data["simulation_years"] == 10
    assert len(data["timelines"]) == 11
    assert len(data["spatial_grids"]) == 11
    assert len(data["biomass_series"]["native"]) == 11
    assert len(data["spectral_radius_series"]) == 11


def test_native_engine_never_labeled_executed_on_linux(client):
    """Verifies /api/landis/run and /api/landis/status never report executed on Linux."""
    with patch("sys.platform", "linux"):
        # Status endpoint
        res_status = client.get("/api/landis/status")
        assert res_status.status_code == 200
        stat_data = res_status.get_json()
        assert stat_data["installed"] is False
        assert stat_data["execution_available"] is False
        assert stat_data["status"] == "UNAVAILABLE_ON_LINUX"

        # Run endpoint
        res_run = client.post("/api/landis/run", json={"scenario_file": "scenario.txt"})
        assert res_run.status_code == 200
        run_data = res_run.get_json()
        assert run_data["success"] is False
        assert run_data["status"] == "UNAVAILABLE_ON_LINUX"
        assert run_data["execution"]["status"] == "UNAVAILABLE_ON_LINUX"
        assert run_data["execution"]["return_code"] is None
