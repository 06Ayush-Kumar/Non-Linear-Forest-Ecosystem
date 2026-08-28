"""
Species Taxonomy Normalization & Canonical Resolver.
Standardizes scientific names, handles synonyms, author citations, and vernacular names.
Resolves taxonomic ambiguities to authoritative canonical taxa (IPNI, POWO, BSI, GBIF Backbone).
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple


TAXONOMY_SYNONYMS: Dict[str, str] = {
    # Lantana
    "lantana camara l.": "Lantana camara",
    "lantana aculeata": "Lantana camara",
    "lantana camara var. aculeata": "Lantana camara",
    "lantana": "Lantana camara",
    "wild sage": "Lantana camara",
    "unni chedi": "Lantana camara",

    # Senna
    "senna spectabilis (dc.) h.s.irwin & barneby": "Senna spectabilis",
    "cassia spectabilis": "Senna spectabilis",
    "cassia spectabilis dc.": "Senna spectabilis",
    "senna": "Senna spectabilis",

    # Prosopis
    "prosopis juliflora (sw.) dc.": "Prosopis juliflora",
    "mimosa juliflora": "Prosopis juliflora",
    "vilayati babool": "Prosopis juliflora",
    "seemai karuvelam": "Prosopis juliflora",

    # Parthenium
    "parthenium hysterophorus l.": "Parthenium hysterophorus",
    "congress grass": "Parthenium hysterophorus",
    "gajar ghas": "Parthenium hysterophorus",

    # Native timber species
    "tectona grandis l.f.": "Tectona grandis",
    "teak": "Tectona grandis",
    "sagwan": "Tectona grandis",

    "shorea robusta roxb. ex gaertn.f.": "Shorea robusta",
    "sal": "Shorea robusta",
    "sakhu": "Shorea robusta",

    "dalbergia latifolia roxb.": "Dalbergia latifolia",
    "rosewood": "Dalbergia latifolia",
    "shisham": "Dalbergia latifolia",
    "beete": "Dalbergia latifolia",

    "terminalia tomentosa (roxb. ex dc.) wight & arn.": "Terminalia tomentosa",
    "terminalia alata": "Terminalia tomentosa",
    "terminalia elliptica": "Terminalia tomentosa",
    "asna": "Terminalia tomentosa",
    "karimarudu": "Terminalia tomentosa"
}


def resolve_canonical_taxon(name_input: str) -> Tuple[str, str]:
    """
    Resolves input query to (canonical_scientific_name, resolution_status).
    Resolution status: 'EXACT_MATCH', 'SYNONYM_RESOLVED', 'GENUS_FALLBACK', 'UNRESOLVED'.
    """
    clean_name = name_input.strip()
    lookup = clean_name.lower()

    if lookup in TAXONOMY_SYNONYMS:
        return TAXONOMY_SYNONYMS[lookup], "SYNONYM_RESOLVED"

    # Exact case-insensitive matching in known database
    for syn_key, canonical in TAXONOMY_SYNONYMS.items():
        if lookup == canonical.lower():
            return canonical, "EXACT_MATCH"

    # If simple binomial format
    parts = clean_name.split()
    if len(parts) >= 2:
        canonical = f"{parts[0].capitalize()} {parts[1].lower()}"
        return canonical, "CANONICAL_PARSED"

    return clean_name, "UNRESOLVED"
