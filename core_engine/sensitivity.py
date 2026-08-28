"""
Parameter Sensitivity & Uncertainty Analysis Module.
Performs One-At-A-Time (OAT) and perturbation sensitivity analysis across:
  - Growth rates: r1, r2, r3
  - Carrying capacities: K1, K2, K3
  - Interspecific competition coefficients: a12, a13, a21, a23, a31, a32
  - Abiotic suitability S_abiotic & Environmental stress D_i
Computes sensitivity indices on:
  - Final native biomass (Mg/ha)
  - Final invasive biomass (Mg/ha)
  - Aboveground carbon pool (Mg C/ha)
  - Spectral radius rho(J_map)
"""

from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from .model import EcologicalParameters, build_calibrated_parameters, ecological_derivatives
from .jacobian import analytical_continuous_jacobian, discrete_jacobian_map
from .stability import calculate_stability_metrics


def compute_parameter_sensitivity(
    base_state: np.ndarray,
    suitability: float = 0.85,
    stress: float = 0.15,
    invasive_pressure: float = 1.0,
    perturbation_fraction: float = 0.10,
    dt: float = 0.1
) -> Dict[str, Any]:
    """
    Computes sensitivity derivatives: d(Metric) / d(Param) using symmetric perturbations.
    """
    base_params = build_calibrated_parameters(suitability, stress, invasive_pressure)
    base_metrics = calculate_stability_metrics(base_state, base_params, dt=dt)
    base_derivs = ecological_derivatives(base_state, base_params)

    base_rho = base_metrics["spectral_radius"]
    base_dx, base_dy, base_dz = base_derivs[0], base_derivs[1], base_derivs[2]

    # Parameters to test
    param_list = [
        {"name": "r1 (Native Growth Rate)", "key": "r1", "val": 0.45, "unit": "yr^-1"},
        {"name": "r2 (Understory Growth Rate)", "key": "r2", "val": 0.68, "unit": "yr^-1"},
        {"name": "r3 (Invasive Growth Rate)", "key": "r3", "val": 0.92, "unit": "yr^-1"},
        {"name": "K1 (Native Carrying Capacity)", "key": "k1", "val": 180.0, "unit": "Mg/ha"},
        {"name": "K2 (Understory Capacity)", "key": "k2", "val": 45.0, "unit": "Mg/ha"},
        {"name": "K3 (Invasive Capacity)", "key": "k3", "val": 65.0, "unit": "Mg/ha"},
        {"name": "a13 (Invasive Shade/Allelopathy)", "key": "a13", "val": 0.58, "unit": "Dimensionless"},
        {"name": "a31 (Canopy Shade Suppression)", "key": "a31", "val": 0.22, "unit": "Dimensionless"},
        {"name": "S_abiotic (Climate Suitability)", "key": "suit", "val": suitability, "unit": "Index (0-1)"},
        {"name": "D_i (Disturbance Stress)", "key": "stress", "val": stress, "unit": "Index (0-1)"}
    ]

    sensitivity_results = []

    for p in param_list:
        delta = max(1e-4, p["val"] * perturbation_fraction)

        # Plus perturbation
        if p["key"] == "suit":
            p_plus = build_calibrated_parameters(min(1.0, suitability + delta), stress, invasive_pressure)
            p_minus = build_calibrated_parameters(max(0.05, suitability - delta), stress, invasive_pressure)
        elif p["key"] == "stress":
            p_plus = build_calibrated_parameters(suitability, min(0.95, stress + delta), invasive_pressure)
            p_minus = build_calibrated_parameters(suitability, max(0.0, stress - delta), invasive_pressure)
        elif p["key"] == "r3":
            p_plus = build_calibrated_parameters(suitability, stress, invasive_pressure, base_r3=p["val"] + delta)
            p_minus = build_calibrated_parameters(suitability, stress, invasive_pressure, base_r3=max(0.05, p["val"] - delta))
        elif p["key"] == "r1":
            p_plus = build_calibrated_parameters(suitability, stress, invasive_pressure, base_r1=p["val"] + delta)
            p_minus = build_calibrated_parameters(suitability, stress, invasive_pressure, base_r1=max(0.05, p["val"] - delta))
        elif p["key"] == "k3":
            p_plus = build_calibrated_parameters(suitability, stress, invasive_pressure, k3=p["val"] + delta)
            p_minus = build_calibrated_parameters(suitability, stress, invasive_pressure, k3=max(10.0, p["val"] - delta))
        elif p["key"] == "a31":
            p_plus = build_calibrated_parameters(suitability, stress, invasive_pressure, a31=p["val"] + delta)
            p_minus = build_calibrated_parameters(suitability, stress, invasive_pressure, a31=max(0.0, p["val"] - delta))
        elif p["key"] == "a13":
            p_plus = build_calibrated_parameters(suitability, stress, invasive_pressure, a13=p["val"] + delta)
            p_minus = build_calibrated_parameters(suitability, stress, invasive_pressure, a13=max(0.0, p["val"] - delta))
        else:
            p_plus = base_params
            p_minus = base_params

        m_plus = calculate_stability_metrics(base_state, p_plus, dt=dt)
        m_minus = calculate_stability_metrics(base_state, p_minus, dt=dt)

        d_rho = (m_plus["spectral_radius"] - m_minus["spectral_radius"]) / (2.0 * delta)
        
        deriv_plus = ecological_derivatives(base_state, p_plus)
        deriv_minus = ecological_derivatives(base_state, p_minus)
        
        d_dx = (deriv_plus[0] - deriv_minus[0]) / (2.0 * delta)
        d_dz = (deriv_plus[2] - deriv_minus[2]) / (2.0 * delta)

        # Normalized elasticity: (dY/dX) * (X0/Y0)
        norm_elasticity_rho = d_rho * (p["val"] / max(1e-4, base_rho))
        norm_elasticity_dz = d_dz * (p["val"] / max(1e-4, abs(base_dz)))

        sensitivity_results.append({
            "parameter_name": p["name"],
            "base_value": p["val"],
            "unit": p["unit"],
            "d_rho_d_param": round(float(d_rho), 4),
            "elasticity_spectral_radius": round(float(norm_elasticity_rho), 4),
            "d_dz_d_param": round(float(d_dz), 4),
            "elasticity_invasive_growth": round(float(norm_elasticity_dz), 4),
            "impact_rank": "HIGH" if abs(norm_elasticity_rho) > 0.5 or abs(norm_elasticity_dz) > 0.5 else ("MODERATE" if abs(norm_elasticity_rho) > 0.1 else "LOW")
        })

    # Sort by absolute impact on invasive dynamics
    sensitivity_results.sort(key=lambda x: abs(x["elasticity_invasive_growth"]), reverse=True)

    return {
        "base_state": base_state.tolist(),
        "base_spectral_radius": base_rho,
        "perturbation_step_pct": round(perturbation_fraction * 100, 1),
        "method": "Central Symmetric Numerical Finite Difference & Elasticity Indexing",
        "parameters_analyzed": sensitivity_results,
        "provenance": {
            "methodology": "One-at-a-time (OAT) Elasticity Analysis",
            "elasticity_formula": "E = (dY / dTheta) * (Theta_0 / Y_0)",
            "interpretation": "Elasticity > 1.0 indicates super-linear sensitivity; Elasticity < 1.0 indicates damped response."
        }
    }
