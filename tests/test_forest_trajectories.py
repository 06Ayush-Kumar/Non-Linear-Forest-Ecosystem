import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_layer.india_gis import PROTECTED_AREAS
from core_engine.spatial import run_spatial_landscape_simulation



def test_forest_trajectories_exact_initial_conditions():
    forest_keys = ['mudumalai', 'kanha', 'kaziranga', 'gir', 'wayanad']
    print("\n" + "=" * 95)
    print(f"{'FOREST':<22} | {'x0':<6} {'y0':<6} {'z0':<6} | {'traj[0] (x, y, z)':<22} | {'traj[30] (x, y, z)':<22} | {'rho[0]':<8} | {'rho[30]':<8}")
    print("=" * 95)

    results = {}
    for f_id in forest_keys:
        pa = PROTECTED_AREAS[f_id]
        x0, y0, z0 = pa.native_standing_biomass_mg_ha, pa.understory_biomass_mg_ha, pa.invasive_biomass_mg_ha
        sim = run_spatial_landscape_simulation(grid_size=30, years=30, dt=0.1, initial_native=x0, initial_competing=y0, initial_invasive=z0)
        
        t0_x = sim['biomass_series']['native'][0]
        t0_y = sim['biomass_series']['competing'][0]
        t0_z = sim['biomass_series']['invasive'][0]
        
        t30_x = sim['biomass_series']['native'][-1]
        t30_y = sim['biomass_series']['competing'][-1]
        t30_z = sim['biomass_series']['invasive'][-1]
        
        rho0 = sim['spectral_radius_series'][0]
        rho30 = sim['spectral_radius_series'][-1]
        
        # Verify exact equality of trajectory[0] to [x0, y0, z0]
        assert t0_x == x0, f"{f_id}: t0_x ({t0_x}) != x0 ({x0})"
        assert t0_y == y0, f"{f_id}: t0_y ({t0_y}) != y0 ({y0})"
        assert t0_z == z0, f"{f_id}: t0_z ({t0_z}) != z0 ({z0})"

        t0_str = f"({t0_x:.1f}, {t0_y:.1f}, {t0_z:.1f})"
        t30_str = f"({t30_x:.1f}, {t30_y:.1f}, {t30_z:.1f})"
        print(f"{pa.name[:22]:<22} | {x0:<6.1f} {y0:<6.1f} {z0:<6.1f} | {t0_str:<22} | {t30_str:<22} | {rho0:<8.4f} | {rho30:<8.4f}")
        results[f_id] = {
            "name": pa.name,
            "x0": x0, "y0": y0, "z0": z0,
            "t0": (t0_x, t0_y, t0_z),
            "t30": (t30_x, t30_y, t30_z),
            "rho0": rho0, "rho30": rho30
        }

    print("=" * 95)
    
    # Assert all 5 initial native biomasses are distinct
    assert results["gir"]["x0"] == 98.2
    assert results["mudumalai"]["x0"] == 158.4
    assert results["kanha"]["x0"] == 174.2
    assert results["wayanad"]["x0"] == 185.3
    assert results["kaziranga"]["x0"] == 210.8


def test_deterministic_spatial_heterogeneity_and_baseline_preservation():
    """
    Requirements 1, 2, 3, 4, 5, 11:
    - mean(native_grid) == x0 (baseline strictly preserved)
    - mean(understory_grid) == y0
    - mean(invasive_grid) == z0
    - deterministic output for same area_id
    - different patterns for different area_ids
    - visible spatial heterogeneity (std > 0)
    """
    import numpy as np
    from core_engine.spatial import generate_deterministic_spatial_pattern

    forests = ['gir', 'mudumalai', 'kanha', 'kaziranga', 'nagarhole', 'wayanad']
    patterns = {}

    for f_id in forests:
        pa = PROTECTED_AREAS[f_id]
        x0, y0, z0 = pa.native_standing_biomass_mg_ha, pa.understory_biomass_mg_ha, pa.invasive_biomass_mg_ha

        # 1. Determinism check: same area_id produces exact identical array
        pat_n1 = generate_deterministic_spatial_pattern(30, f_id, "native")
        pat_n2 = generate_deterministic_spatial_pattern(30, f_id, "native")
        assert np.array_equal(pat_n1, pat_n2), f"Pattern for {f_id} must be perfectly deterministic"

        pat_u = generate_deterministic_spatial_pattern(30, f_id, "understory")
        pat_i = generate_deterministic_spatial_pattern(30, f_id, "invasive")

        # 2. Normalized pattern mean must strictly be 1.0
        assert abs(np.mean(pat_n1) - 1.0) < 1e-7
        assert abs(np.mean(pat_u) - 1.0) < 1e-7
        assert abs(np.mean(pat_i) - 1.0) < 1e-7

        # 3. Scaled grid means must equal x0, y0, z0 within numerical tolerance
        native_grid = x0 * pat_n1
        understory_grid = y0 * pat_u
        invasive_grid = z0 * pat_i

        assert abs(np.mean(native_grid) - x0) < 1e-5, f"{f_id}: mean(native_grid) {np.mean(native_grid)} != x0 {x0}"
        assert abs(np.mean(understory_grid) - y0) < 1e-5, f"{f_id}: mean(understory_grid) {np.mean(understory_grid)} != y0 {y0}"
        assert abs(np.mean(invasive_grid) - z0) < 1e-5, f"{f_id}: mean(invasive_grid) {np.mean(invasive_grid)} != z0 {z0}"

        # 4. Spatial heterogeneity: standard deviation must show visible contrast
        assert np.std(native_grid) > 10.0, f"{f_id}: native grid must have visible spatial variance"
        assert np.min(native_grid) < x0 * 0.7, f"{f_id}: canopy gaps must be present"
        assert np.max(native_grid) > x0 * 1.3, f"{f_id}: dense canopy patches must be present"

        # 5. Full spatial simulation snapshot test
        sim = run_spatial_landscape_simulation(
            grid_size=30, years=2, dt=0.1,
            initial_native=x0, initial_competing=y0, initial_invasive=z0,
            area_id=f_id
        )
        snap0 = sim["spatial_grids"][0]
        snap_native_mean = float(np.mean([[cell["native"] for cell in row] for row in snap0]))
        assert abs(snap_native_mean - x0) < 0.1, f"Year 0 snapshot mean {snap_native_mean} != x0 {x0}"

        patterns[f_id] = pat_n1

    # 6. Pairwise distinctness check: every forest has a different spatial pattern
    for i, f1 in enumerate(forests):
        for j, f2 in enumerate(forests):
            if i < j:
                diff = np.max(np.abs(patterns[f1] - patterns[f2]))
                assert diff > 0.2, f"Patterns for {f1} and {f2} must be visibly different (max diff = {diff})"


if __name__ == "__main__":
    test_forest_trajectories_exact_initial_conditions()
    test_deterministic_spatial_heterogeneity_and_baseline_preservation()
    print("All spatial heterogeneity and trajectory tests PASSED successfully.")

