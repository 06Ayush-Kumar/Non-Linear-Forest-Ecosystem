"""
Jacobian & Numerical Verification Engine.
Computes the analytical 3x3 Continuous Jacobian matrix J_F:
  J_F = [ df1/dx  df1/dy  df1/dz ]
        [ df2/dx  df2/dy  df2/dz ]
        [ df3/dx  df3/dy  df3/dz ]

And the Discrete-Time Approximation Matrix:
  J_map = I + dt * J_F

Also includes Central Finite-Difference Numerical Verification:
  df_i/dx_j ≈ [f_i(x + h*e_j) - f_i(x - h*e_j)] / (2*h)
Automatically reports maximum absolute error, relative error, and Pass/Fail verification.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, Tuple
from .model import EcologicalParameters, ecological_derivatives


def analytical_continuous_jacobian(state: np.ndarray, params: EcologicalParameters) -> np.ndarray:
    """Computes exact 3x3 analytical Jacobian matrix J_F for continuous ODE system."""
    x = float(state[0])
    y = float(state[1])
    z = float(state[2])
    r1, r2, r3 = params.growth_rates
    k1, k2, k3 = params.carrying_capacities
    a = params.competition_matrix

    J = np.zeros((3, 3), dtype=float)

    # Row 1: df1/dx, df1/dy, df1/dz
    J[0, 0] = r1 * (1.0 - (2.0 * x + a[0, 1] * y + a[0, 2] * z) / k1)
    J[0, 1] = -r1 * a[0, 1] * x / k1
    J[0, 2] = -r1 * a[0, 2] * x / k1

    # Row 2: df2/dx, df2/dy, df2/dz
    J[1, 0] = -r2 * a[1, 0] * y / k2
    J[1, 1] = r2 * (1.0 - (2.0 * y + a[1, 0] * x + a[1, 2] * z) / k2)
    J[1, 2] = -r2 * a[1, 2] * y / k2

    # Row 3: df3/dx, df3/dy, df3/dz
    J[2, 0] = -r3 * a[2, 0] * z / k3
    J[2, 1] = -r3 * a[2, 1] * z / k3
    J[2, 2] = r3 * (1.0 - (2.0 * z + a[2, 0] * x + a[2, 1] * y) / k3)

    return J


def discrete_jacobian_map(state: np.ndarray, params: EcologicalParameters, dt: float = 0.1) -> np.ndarray:
    """Computes discrete-time Jacobian map: J_map = I + dt * J_F."""
    J_continuous = analytical_continuous_jacobian(state, params)
    return np.eye(3, dtype=float) + dt * J_continuous


def numerical_finite_difference_jacobian(
    state: np.ndarray,
    params: EcologicalParameters,
    h: float = 1e-6
) -> np.ndarray:
    """
    Computes numerical Jacobian via central finite difference for interior points,
    or forward finite difference at boundary points (x_j <= 0).
    """
    J_num = np.zeros((3, 3), dtype=float)
    state_arr = np.asarray(state, dtype=float)

    for j in range(3):
        if state_arr[j] < h:
            # Forward difference at zero boundary: [f(x + h) - f(x)] / h
            state_plus = state_arr.copy()
            state_plus[j] += h
            f_plus = ecological_derivatives(state_plus, params)
            f_curr = ecological_derivatives(state_arr, params)
            J_num[:, j] = (f_plus - f_curr) / h
        else:
            # Central difference for interior points: [f(x + h) - f(x - h)] / (2h)
            state_plus = state_arr.copy()
            state_minus = state_arr.copy()
            state_plus[j] += h
            state_minus[j] -= h

            f_plus = ecological_derivatives(state_plus, params)
            f_minus = ecological_derivatives(state_minus, params)
            J_num[:, j] = (f_plus - f_minus) / (2.0 * h)

    return J_num


def verify_jacobian(
    state: np.ndarray,
    params: EcologicalParameters,
    h: float = 1e-6,
    tolerance: float = 1e-4
) -> Dict[str, Any]:
    """Cross-verifies analytical Jacobian against numerical finite differences."""
    J_analytical = analytical_continuous_jacobian(state, params)
    J_numerical = numerical_finite_difference_jacobian(state, params, h)

    abs_diff = np.abs(J_analytical - J_numerical)
    max_abs_error = float(np.max(abs_diff))
    
    denom = np.maximum(np.abs(J_analytical), 1e-6)
    rel_diff = abs_diff / denom
    max_rel_error = float(np.max(rel_diff))

    passed = bool(max_abs_error < tolerance or max_rel_error < tolerance)

    return {
        "verified": passed,
        "max_absolute_error": round(max_abs_error, 9),
        "max_relative_error": round(max_rel_error, 9),
        "tolerance": tolerance,
        "analytical_jacobian": np.round(J_analytical, 6).tolist(),
        "numerical_jacobian": np.round(J_numerical, 6).tolist(),
        "status": "PASS (Analytical matches Numerical)" if passed else "FAIL"
    }
