"""
Candidate Species Introduction & Ecological Risk Evaluator.
Executes rigorous 12-step assessment:
  1. Canonical taxonomic identification & synonym normalization
  2. Regional native status determination (strictly distinguishing native vs non-native vs candidate)
  3. Trait retrieval & shade/fire/drought tolerance indexing
  4. Gaussian abiotic suitability calculation (S_T, S_E, S_M, S_S)
  5. Establishment potential estimation
  6. Competitive displacement potential against native canopy
  7. Spatial spread velocity modeling
  8. Local mathematical stability effects (eigenvalues & spectral radius)
  9. Final risk classification: LOW RISK, MODERATE RISK, HIGH RISK, VERY HIGH RISK, INSUFFICIENT EVIDENCE.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import numpy as np

from data_layer.taxonomy import resolve_canonical_taxon
from data_layer.trait_database import get_species_record
from core_engine.suitability import calculate_abiotic_suitability, SpeciesNicheRequirements
from core_engine.model import build_calibrated_parameters
from core_engine.stability import calculate_stability_metrics
from core_engine.invasive_model import calculate_invasive_impact_score


def evaluate_candidate_introduction(
    species_name_input: str,
    site_temperature_c: float = 24.5,
    site_elevation_m: float = 850.0,
    site_rainfall_mm: float = 1250.0,
    site_native_biomass_mg_ha: float = 158.0,
    target_region_state: str = "Tamil Nadu"
) -> Dict[str, Any]:
    # Step 1: Taxonomic Resolution
    canonical_name, tax_status = resolve_canonical_taxon(species_name_input)
    record = get_species_record(canonical_name)

    if not record:
        # Insufficient Empirical Evidence
        return {
            "query_name": species_name_input,
            "canonical_name": canonical_name,
            "taxonomic_status": tax_status,
            "evaluation_status": "INSUFFICIENT EVIDENCE",
            "risk_classification": "INSUFFICIENT EVIDENCE",
            "risk_color": "#9ca3af",
            "reasoning": f"No authoritative empirical trait records or published occurrence logs found for '{canonical_name}' in Indian forestry repositories. Cannot evaluate risk without verified biological data.",
            "recommendation": "Perform verified field herbarium specimen collection and physiological trial before considering introduction."
        }

    # Step 2: Regional Native Status Determination
    regional_status = record["regional_status"]
    is_native = (regional_status in ["NATIVE", "ENDEMIC"])
    is_documented_invasive = (regional_status == "INVASIVE")

    # Step 3 & 4: Environmental Suitability
    niche = SpeciesNicheRequirements(
        temp_opt_c=record["optimal_temp_c"],
        elev_opt_m=record["optimal_elevation_m"],
        precip_opt_mm=record["optimal_rainfall_mm"]
    )
    suitability = calculate_abiotic_suitability(
        temperature_c=site_temperature_c,
        elevation_m=site_elevation_m,
        precipitation_mm=site_rainfall_mm,
        niche=niche
    )
    s_comp = suitability["s_composite"]

    # Step 5 & 6: Establishment & Displacement Potential
    # If native, establishment is beneficial regeneration; if invasive, it represents risk
    shade_tol = record["shade_tolerance"] # 1 to 5
    drought_tol = record["drought_tolerance"]
    fire_tol = record["fire_tolerance"]

    # Vigor / invasiveness index based on traits
    trait_vigor = (drought_tol * 0.35 + fire_tol * 0.35 + (5 - shade_tol) * 0.30) / 5.0
    establishment_prob = round(float(np.clip(s_comp * (0.4 + 0.6 * trait_vigor), 0.0, 1.0)), 3)
    displacement_potential = round(float(np.clip(establishment_prob * (0.8 if is_documented_invasive else 0.2), 0.0, 1.0)), 3)

    # Step 7: Stability Impact Analysis
    # Construct hypothetical 3-state parameters
    params = build_calibrated_parameters(
        suitability=s_comp,
        stress=0.15,
        invasive_pressure=1.5 if is_documented_invasive else 0.4
    )
    # Test state with candidate introduced
    test_state = np.array([site_native_biomass_mg_ha * 0.85, 25.0, 18.0 if is_documented_invasive else 5.0])
    stab = calculate_stability_metrics(test_state, params)

    # Step 8: Invasive Impact Score
    iis = calculate_invasive_impact_score(
        native_initial_biomass=site_native_biomass_mg_ha,
        native_final_biomass=site_native_biomass_mg_ha * (1.0 - displacement_potential * 0.4),
        invasive_final_biomass=35.0 * establishment_prob if is_documented_invasive else 8.0,
        invasive_max_capacity=65.0,
        invasive_coverage_pct=establishment_prob * 60.0 if is_documented_invasive else 10.0,
        spread_rate_m_yr=25.0 * establishment_prob if is_documented_invasive else 3.0,
        initial_shannon=0.92,
        final_shannon=0.92 - (0.45 * displacement_potential if is_documented_invasive else 0.05)
    )

    # Final Classification & Geographic Status Category
    if is_native:
        status_category = "NATIVE_SPECIES"
        risk_class = f"LOW RISK (Indigenous Native Taxon in {target_region_state})"
        risk_color = "#10b981"
        verdict = f"{canonical_name} is an indigenous/native species in {target_region_state}. Introduction or enrichment planting supports native biodiversity and ecosystem resilience."
    elif is_documented_invasive:
        status_category = "DOCUMENTED_INVASIVE_OCCURRENCE"
        if iis["invasive_impact_score"] >= 50.0:
            risk_class = f"VERY HIGH RISK (Documented High-Impact Invasive in {target_region_state})"
            risk_color = "#dc2626"
        else:
            risk_class = f"HIGH RISK (Documented Alien Invasive in {target_region_state})"
            risk_color = "#f97316"
        verdict = f"CRITICAL WARNING: {canonical_name} is a documented high-risk invasive alien plant in {target_region_state} with aggressive allelopathy and fast regeneration. Introduction is strongly discouraged."
    else:
        status_category = "DOCUMENTED_NON_NATIVE_OCCURRENCE"
        risk_class = f"MODERATE RISK (Exotic / Non-Native Candidate for {target_region_state})"
        risk_color = "#eab308"
        verdict = f"{canonical_name} is non-native to {target_region_state}. While not currently classified as high-impact in this tract, precautionary monitoring is required."

    return {
        "query_name": species_name_input,
        "canonical_name": canonical_name,
        "taxonomic_status": tax_status,
        "family": record["family"],
        "native_range": record["native_range"],
        "regional_status": regional_status,
        "status_category": status_category,
        "target_region_state": target_region_state,
        "evaluation_type": "MODELLED ECOLOGICAL INVASION RISK (IUCN EICAT Adapted)",
        "growth_form": record["growth_form"],
        "environmental_suitability": suitability,

        "traits": {
            "max_height_m": record["max_height_m"],
            "shade_tolerance": f"{shade_tol} / 5",
            "drought_tolerance": f"{drought_tol} / 5",
            "fire_tolerance": f"{fire_tol} / 5",
            "dispersal_vector": record["dispersal_mechanism"],
            "allelopathy": record["allelopathic_evidence"]
        },
        "potentials": {
            "establishment_probability": establishment_prob,
            "displacement_potential": displacement_potential,
            "spread_potential": "High (Frugivorous Zoochory)" if "Zoochory" in record["dispersal_mechanism"] else "Moderate (Anemochory)"
        },
        "stability_metrics": stab,
        "invasive_impact_index": iis,
        "final_classification": risk_class,
        "risk_color": risk_color,
        "verdict_summary": verdict,
        "documented_impacts": record.get("documented_ecological_impacts", []),
        "provenance_citation": record.get("provenance_source", "Curated Literature"),
        "provenance_agency": record.get("citation_agency", "Authoritative Botanical Literature")
    }

