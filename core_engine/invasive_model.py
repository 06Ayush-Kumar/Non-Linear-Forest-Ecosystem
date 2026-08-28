"""
Invasive Impact & Ecological Consequence Assessment Module.
Calculates the Model-Derived Invasive Impact Score (IIS) normalized to 0-100:
  IIS = 100 * (w1*Coverage + w2*BiomassRatio + w3*NativeDisplacement + w4*SpreadVelocity + w5*DiversityLoss)

Distinguishes:
  - DIRECTLY MODELLED EFFECTS (biomass loss, spatial occupancy, regeneration inhibition)
  - DOCUMENTED / POTENTIAL ECOLOGICAL CONSEQUENCES (fire regime shifts, allelopathy, soil nitrogen)
"""

from __future__ import annotations
from typing import Dict, Any, List
import numpy as np


def calculate_invasive_impact_score(
    native_initial_biomass: float,
    native_final_biomass: float,
    invasive_final_biomass: float,
    invasive_max_capacity: float,
    invasive_coverage_pct: float,
    spread_rate_m_yr: float,
    initial_shannon: float,
    final_shannon: float
) -> Dict[str, Any]:
    # 1. Spatial Coverage Factor (0.0 to 1.0)
    f_coverage = np.clip(invasive_coverage_pct / 100.0, 0.0, 1.0)

    # 2. Biomass Density Ratio (0.0 to 1.0)
    f_biomass = np.clip(invasive_final_biomass / max(1e-4, invasive_max_capacity), 0.0, 1.0)

    # 3. Native Canopy Displacement (0.0 to 1.0)
    native_loss = max(0.0, native_initial_biomass - native_final_biomass)
    f_displacement = np.clip(native_loss / max(1e-4, native_initial_biomass), 0.0, 1.0)

    # 4. Spatial Spread Rate Factor (0.0 to 1.0, benchmark 100m/yr max)
    f_spread = np.clip(spread_rate_m_yr / 100.0, 0.0, 1.0)

    # 5. Biodiversity Shannon Loss Factor (0.0 to 1.0)
    div_loss = max(0.0, initial_shannon - final_shannon)
    f_diversity = np.clip(div_loss / max(1e-4, initial_shannon), 0.0, 1.0)

    # Component weights
    w_cov = 0.25
    w_bio = 0.20
    w_disp = 0.25
    w_sprd = 0.15
    w_div = 0.15

    iis_raw = (w_cov * f_coverage + w_bio * f_biomass + w_disp * f_displacement + w_sprd * f_spread + w_div * f_diversity)
    iis_score = round(float(iis_raw * 100.0), 1)

    # Risk Tier
    if iis_score >= 65.0:
        risk_category = "VERY HIGH RISK"
        risk_color = "#dc2626"
    elif iis_score >= 40.0:
        risk_category = "HIGH RISK"
        risk_color = "#f97316"
    elif iis_score >= 20.0:
        risk_category = "MODERATE RISK"
        risk_color = "#eab308"
    else:
        risk_category = "LOW RISK"
        risk_color = "#10b981"

    return {
        "invasive_impact_score": iis_score,
        "risk_category": risk_category,
        "risk_color": risk_color,
        "classification": "PROJECT-DEFINED MULTI-CRITERIA DECISION INDEX",
        "weight_derivation": "Project-defined heuristic weighting scheme informed by IUCN EICAT (2020) qualitative impact categories (not statistically fitted via parameter optimization)",
        "components": {
            "spatial_coverage": {"value_pct": round(invasive_coverage_pct, 1), "normalized": round(float(f_coverage), 3), "weight": w_cov, "rationale": "High weight (0.25): Spatial occupancy directly limits native regeneration area."},
            "biomass_accumulation": {"value_mg_ha": round(invasive_final_biomass, 1), "normalized": round(float(f_biomass), 3), "weight": w_bio, "rationale": "Moderate weight (0.20): Fuel loading and standing resource monopolization."},
            "native_displacement": {"loss_pct": round(float(f_displacement * 100.0), 1), "normalized": round(float(f_displacement), 3), "weight": w_disp, "rationale": "High weight (0.25): Direct loss of native overstory/understory structural integrity."},
            "spread_velocity": {"rate_m_yr": round(spread_rate_m_yr, 1), "normalized": round(float(f_spread), 3), "weight": w_sprd, "rationale": "Moderate weight (0.15): Frontline migration velocity across neighboring habitat patches."},
            "biodiversity_reduction": {"shannon_loss": round(float(div_loss), 3), "normalized": round(float(f_diversity), 3), "weight": w_div, "rationale": "Moderate weight (0.15): Understory floristic homogenization and Shannon diversity decline."}
        },
        "formula": "IIS = 100 * (0.25*Coverage + 0.20*BiomassRatio + 0.25*Displacement + 0.15*SpreadVelocity + 0.15*DiversityLoss)",
        "provenance": "Project-defined multi-attribute ecological risk framework adapted from EICAT (IUCN 2020) and FSI invasive vulnerability criteria."
    }

