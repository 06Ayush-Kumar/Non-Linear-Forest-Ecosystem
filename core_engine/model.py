"""
Our Original Nonlinear Multi-Species Ecological Dynamics Model.
Three-state coupled ordinary differential equations with environmental modulation:
  dx/dt = r1 * x * (1 - (x + a12*y + a13*z) / K1)
  dy/dt = r2 * y * (1 - (y + a21*x + a23*z) / K2)
  dz/dt = r3 * z * (1 - (z + a31*x + a32*y) / K3)

Where:
  x = Native climax timber/tree biomass state (Mg/ha)
  y = Competing understory / shrub biomass state (Mg/ha)
  z = Introduced candidate / invasive species biomass state (Mg/ha)

NOTE: This layer represents OUR SCIENTIFIC CONTRIBUTION, coupled with LANDIS-II landscape grids.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Tuple


@dataclass(frozen=True)
class EcologicalParameters:
    growth_rates: np.ndarray        # [r1, r2, r3] modulated by suitability & stress
    carrying_capacities: np.ndarray # [K1, K2, K3] in Mg/ha
    competition_matrix: np.ndarray  # 3x3 matrix [[a_ij]]
    climate_suitability: float      # S_abiotic in [0, 1]
    environmental_stress: float     # D_i in [0, 1]
    invasive_pressure: float        # Propagule pressure multiplier


def build_calibrated_parameters(
    suitability: float = 0.85,
    stress: float = 0.15,
    invasive_pressure: float = 1.0,
    base_r1: float = 0.45,
    base_r2: float = 0.68,
    base_r3: float = 0.92,
    k1: float = 180.0,
    k2: float = 45.0,
    k3: float = 65.0,
    a12: float = 0.35,
    a13: float = 0.58,
    a21: float = 0.24,
    a23: float = 0.42,
    a31: float = 0.22,
    a32: float = 0.30
) -> EcologicalParameters:
    suitability = float(np.clip(suitability, 0.05, 1.0))
    stress = float(np.clip(stress, 0.0, 0.95))
    invasive_pressure = float(np.clip(invasive_pressure, 0.1, 3.0))

    # Environmental Modulation: r_i' = r_i * S_i * (1 - D_i)
    env_mod = suitability * (1.0 - 0.5 * stress)
    r1_mod = base_r1 * env_mod
    r2_mod = base_r2 * (1.0 - 0.25 * stress) # understory resilient to light disturbance
    r3_mod = base_r3 * suitability * invasive_pressure * (1.0 + 0.3 * stress) # invasives exploit disturbed canopy

    growth_rates = np.array([r1_mod, r2_mod, r3_mod], dtype=float)
    carrying_capacities = np.array([k1, k2, k3], dtype=float)

    # Interspecific competition matrix
    competition = np.array([
        [1.0, a12, a13],
        [a21, 1.0, a23],
        [a31, a32, 1.0]
    ], dtype=float)

    return EcologicalParameters(
        growth_rates=growth_rates,
        carrying_capacities=carrying_capacities,
        competition_matrix=competition,
        climate_suitability=suitability,
        environmental_stress=stress,
        invasive_pressure=invasive_pressure
    )


def ecological_derivatives(state: np.ndarray, params: EcologicalParameters) -> np.ndarray:
    """
    Computes time-derivatives [dx/dt, dy/dt, dz/dt].
    Strictly preserves biological non-negativity and finite capacities.
    """
    state = np.asarray(state, dtype=float)
    x, y, z = state[..., 0], state[..., 1], state[..., 2]
    
    # Strictly zero out negative populations to avoid unphysical negative growth
    x_pos = np.maximum(0.0, x)
    y_pos = np.maximum(0.0, y)
    z_pos = np.maximum(0.0, z)

    r1, r2, r3 = params.growth_rates
    k1, k2, k3 = params.carrying_capacities
    a = params.competition_matrix

    dx = r1 * x_pos * (1.0 - (x_pos + a[0, 1] * y_pos + a[0, 2] * z_pos) / k1)
    dy = r2 * y_pos * (1.0 - (y_pos + a[1, 0] * x_pos + a[1, 2] * z_pos) / k2)
    dz = r3 * z_pos * (1.0 - (z_pos + a[2, 0] * x_pos + a[2, 1] * y_pos) / k3)

    return np.stack([dx, dy, dz], axis=-1)
