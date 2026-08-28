"""
Stability & Eigenvalue Analysis Engine.
Calculates eigenvalues (lambda_1, lambda_2, lambda_3) and spectral radius rho(J_map).

Interpretation:
  - rho(J_map) < 1.0: Locally asymptotically stable for the discrete-time map.
  - rho(J_map) > 1.0: Locally unstable (perturbations grow).
  - rho(J_map) ≈ 1.0: Near critical / bifurcation transition boundary.

IMPORTANT SCIENTIFIC DISTINCTION:
  "Local mathematical stability of the model state" must NOT be conflated with
  overall "ecological resilience" or biodiversity health.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, Any, List
from .model import EcologicalParameters
from .jacobian import analytical_continuous_jacobian, discrete_jacobian_map, verify_jacobian


def calculate_stability_metrics(
    state: np.ndarray,
    params: EcologicalParameters,
    dt: float = 0.1
) -> Dict[str, Any]:
    state = np.asarray(state, dtype=float)
    J_cont = analytical_continuous_jacobian(state, params)
    J_map = discrete_jacobian_map(state, params, dt)

    # Continuous eigenvalues (Re(lambda) < 0 => stable continuous ODE)
    eig_cont = np.linalg.eigvals(J_cont)
    
    # Discrete eigenvalues ( |lambda| < 1 => stable discrete map )
    eig_map = np.linalg.eigvals(J_map)
    moduli = np.abs(eig_map)
    spectral_radius = float(np.max(moduli))

    # Classification
    if spectral_radius < 0.98:
        class_key = "stable"
        class_label = "Locally Stable (Asymptotically Convergent)"
        risk_color = "#10b981"
    elif spectral_radius <= 1.02:
        class_key = "critical"
        class_label = "Near Critical / Transition Boundary (Marginal Stability)"
        risk_color = "#f59e0b"
    else:
        class_key = "unstable"
        class_label = "Locally Unstable (Perturbations Amplify)"
        risk_color = "#ef4444"

    # Finite difference verification
    verification = verify_jacobian(state, params)

    return {
        "spectral_radius": round(spectral_radius, 5),
        "continuous_eigenvalues": [
            {"real": round(float(e.real), 5), "imag": round(float(e.imag), 5)} for e in eig_cont
        ],
        "discrete_eigenvalues": [
            {"real": round(float(e.real), 5), "imag": round(float(e.imag), 5), "modulus": round(float(m), 5)}
            for e, m in zip(eig_map, moduli)
        ],
        "stability_class": class_key,
        "stability_label": class_label,
        "risk_color": risk_color,
        "jacobian_continuous": np.round(J_cont, 5).tolist(),
        "jacobian_discrete": np.round(J_map, 5).tolist(),
        "dt": dt,
        "verification": verification,
        "scientific_note": "Reflects local mathematical stability of the 3-state system; ecological resilience incorporates spatial heterogeneity and functional diversity."
    }


def find_system_equilibria(params: EcologicalParameters) -> List[Dict[str, Any]]:
    """Identifies feasible non-negative equilibria F(x*) = 0."""
    k1, k2, k3 = params.carrying_capacities
    a = params.competition_matrix

    eqs = []

    # 1. Barren / Extinction Equilibrium (0, 0, 0)
    eqs.append({
        "name": "Extinction / Barren Equilibrium",
        "state": [0.0, 0.0, 0.0],
        "type": "Trivial Unstable",
        "description": "Total absence of all vegetation layers."
    })

    # 2. Native Monoculture Equilibrium (K1, 0, 0)
    eqs.append({
        "name": "Native Climax Dominant Equilibrium",
        "state": [round(float(k1), 2), 0.0, 0.0],
        "type": "Native Dominant",
        "description": "Intact native forest canopy at full carrying capacity without understory or invasives."
    })

    # 3. Native + Understory Coexistence (Invasive-Free)
    # x + a12*y = K1 and y + a21*x = K2
    det = 1.0 - a[0, 1] * a[1, 0]
    if abs(det) > 1e-4:
        x_co = (k1 - a[0, 1] * k2) / det
        y_co = (k2 - a[1, 0] * k1) / det
        if x_co > 0 and y_co > 0:
            eqs.append({
                "name": "Natural Forest-Understory Coexistence",
                "state": [round(float(x_co), 2), round(float(y_co), 2), 0.0],
                "type": "Natural Coexistence",
                "description": "Stable equilibrium between native timber canopy and healthy native understory."
            })

    # 4. Invasive Monoculture (0, 0, K3)
    eqs.append({
        "name": "Invasive Dominated Monoculture",
        "state": [0.0, 0.0, round(float(k3), 2)],
        "type": "Degraded Invasive State",
        "description": "Complete canopy loss with dense monospecific invasive thicket (e.g. Lantana/Prosopis)."
    })

    # 5. Three-Species Coexistence (if matrix invertible and positive)
    try:
        sol = np.linalg.solve(a, np.array([k1, k2, k3]))
        if np.all(sol > 0):
            eqs.append({
                "name": "Three-State Coexistence Equilibrium",
                "state": [round(float(s), 2) for s in sol],
                "type": "Mixed Multi-Species Equilibrium",
                "description": "Long-term coexistence between native canopy, understory, and candidate species."
            })
    except Exception:
        pass

    return eqs
