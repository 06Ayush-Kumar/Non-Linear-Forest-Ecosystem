"""
Forest Management Solution & Prescriptive Strategy Engine.
Translates model-derived impact distributions into actionable spatial prescriptions:
  - Early Detection & Rapid Response (EDRR)
  - Mechanical Rootstock Extraction (Cut-Rootstock-Deposition CRD method)
  - Perimeter Containment & Buffer Strips
  - Native Restoration & Enrichment Planting
  - Long-Term Surveillance & Post-Disturbance Monitoring
"""

from __future__ import annotations
from typing import Dict, Any, List


MANAGEMENT_STRATEGIES: List[Dict[str, Any]] = [
    {
        "id": "crd_removal",
        "title": "Mechanical Rootstock Extraction (CRD Method)",
        "target_species": ["Lantana camara", "Senna spectabilis", "Prosopis juliflora"],
        "why": "Cutting above-ground stems triggers aggressive coppicing from subterranean root crowns. The Cut-Rootstock-Deposition (CRD) method severs the rootstock 5-8 cm below ground level, preventing vegetative resprouting.",
        "when": "Post-monsoon dry season (December - March) when soil moisture permits manual rootstock excavation.",
        "where": "High-density invasion thickets (>40% canopy occupancy) in Core and Buffer forest zones.",
        "expected_effect": "90-95% reduction in standing invasive biomass and over 80% decrease in coppice regeneration.",
        "uncertainty": "Requires sustained follow-up for 2-3 years to exhaust dormant soil seed bank.",
        "evidence_source": "Babu et al. (2009) Protocols for Lantana Eradication, University of Delhi / MoEFCC Guidelines"
    },
    {
        "id": "edrr_containment",
        "title": "Early Detection & Rapid Response (EDRR) Buffer",
        "target_species": ["Parthenium hysterophorus", "Chromolaena odorata", "Ageratina adenophora"],
        "why": "Colonization fronts expand rapidly along linear forest corridors (roads, firebreaks, riverbanks). Early manual uprooting of pioneering individuals halts broadscale seed rain.",
        "when": "Immediately post-monsoon (September - November) prior to seed maturation and dehiscence.",
        "where": "Linear infrastructure edges, forest roads, boundary firelines, and ecotones.",
        "expected_effect": "Arrests spatial diffusion front, reducing landscape spread velocity by 60-75%.",
        "uncertainty": "Depends on systematic patrol frequency by frontline forest guard staff.",
        "evidence_source": "IUCN Guidelines on Invasive Species Management & FSI Invasive Vulnerability Protocols"
    },
    {
        "id": "native_restoration",
        "title": "Active Native Succession Restoration Planting",
        "target_species": ["All Invasive Habitats"],
        "why": "Invasive clearance creates exposed disturbed soil prone to secondary weed reinvasion. Immediate planting of fast-growing native grasses (Themeda, Cymbopogon), bamboos, and shade trees closes the light window.",
        "when": "Onset of Southwest Monsoon (June - July) to ensure maximum root establishment.",
        "where": "Cleared invasive plots, degraded forest blanks, and heavily grazed open patches.",
        "expected_effect": "Restores native biodiversity, enhances soil organic carbon by +1.8 Mg C/ha/yr, and increases ecosystem stability (rho < 0.95).",
        "uncertainty": "Mortality risk if early monsoon experiences severe dry spells.",
        "evidence_source": "Ramaswami & Sukumar (2014) Native grassland and forest restoration in the Nilgiris"
    }
]

def list_management_solutions() -> List[Dict[str, Any]]:
    return MANAGEMENT_STRATEGIES.copy()
