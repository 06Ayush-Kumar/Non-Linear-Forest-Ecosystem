"""
Gaussian Environmental Suitability Engine.
Calculates abiotic niche suitability S_T (Temperature), S_E (Elevation),
S_M (Moisture / Precipitation), and S_S (Soil pH / Texture).
Composite: S_abiotic = w_T*S_T + w_E*S_E + w_M*S_M + w_S*S_S with sum(w_i) = 1.0.
All mathematical functions and weights have full provenance.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from typing import Dict, Any


@dataclass(frozen=True)
class SpeciesNicheRequirements:
    temp_opt_c: float = 26.5
    temp_sigma_c: float = 6.5
    elev_opt_m: float = 850.0
    elev_sigma_m: float = 550.0
    precip_opt_mm: float = 1400.0
    precip_sigma_mm: float = 650.0
    soil_ph_opt: float = 6.2
    soil_ph_sigma: float = 1.2
    weight_temp: float = 0.30
    weight_elev: float = 0.20
    weight_precip: float = 0.35
    weight_soil: float = 0.15


def gaussian_response(value: float | np.ndarray, optimum: float, sigma: float) -> float | np.ndarray:
    """Calculates Gaussian response S = exp( - (x - opt)^2 / (2 * sigma^2) ), strictly in [0.0, 1.0]."""
    diff = np.asarray(value, dtype=float) - optimum
    exponent = -(diff ** 2) / (2.0 * (sigma ** 2))
    return np.clip(np.exp(exponent), 0.0, 1.0)


def calculate_abiotic_suitability(
    temperature_c: float | np.ndarray,
    elevation_m: float | np.ndarray,
    precipitation_mm: float | np.ndarray,
    soil_ph: float | np.ndarray = 6.5,
    niche: SpeciesNicheRequirements | None = None
) -> Dict[str, Any]:
    if niche is None:
        niche = SpeciesNicheRequirements()

    s_temp = gaussian_response(temperature_c, niche.temp_opt_c, niche.temp_sigma_c)
    s_elev = gaussian_response(elevation_m, niche.elev_opt_m, niche.elev_sigma_m)
    s_precip = gaussian_response(precipitation_mm, niche.precip_opt_mm, niche.precip_sigma_mm)
    s_soil = gaussian_response(soil_ph, niche.soil_ph_opt, niche.soil_ph_sigma)

    # Normalize weights
    total_w = niche.weight_temp + niche.weight_elev + niche.weight_precip + niche.weight_soil
    w_t = niche.weight_temp / total_w
    w_e = niche.weight_elev / total_w
    w_m = niche.weight_precip / total_w
    w_s = niche.weight_soil / total_w

    s_composite = w_t * s_temp + w_e * s_elev + w_m * s_precip + w_s * s_soil
    s_composite = np.clip(s_composite, 0.0, 1.0)

    # If single scalar, return floats
    if np.ndim(s_composite) == 0:
        return {
            "s_composite": round(float(s_composite), 4),
            "s_temperature": round(float(s_temp), 4),
            "s_elevation": round(float(s_elev), 4),
            "s_precipitation": round(float(s_precip), 4),
            "s_soil": round(float(s_soil), 4),
            "weights": {"w_temp": w_t, "w_elev": w_e, "w_precip": w_m, "w_soil": w_s},
            "formula": "S_abiotic = w_T*exp(-(T-T_opt)^2/(2*sigma_T^2)) + w_E*S_E + w_M*S_M + w_S*S_S",
            "provenance": "Gaussian physiological niche response (Austin 2002; Thuiller et al. 2005)"
        }
    
    return {
        "s_composite": np.round(s_composite, 4),
        "s_temperature": np.round(s_temp, 4),
        "s_elevation": np.round(s_elev, 4),
        "s_precipitation": np.round(s_precip, 4),
        "s_soil": np.round(s_soil, 4),
        "weights": {"w_temp": w_t, "w_elev": w_e, "w_precip": w_m, "w_soil": w_s},
    }
