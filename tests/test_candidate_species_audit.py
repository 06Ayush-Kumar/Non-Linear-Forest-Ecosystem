"""
Automated Test Suite for Candidate Species Introduction Assessment,
Taxonomy Canonical Resolution, and Forest Context Synchronization.
"""

import pytest
from data_layer.trait_database import list_all_species, get_species_record, SPECIES_DB
from data_layer.taxonomy import resolve_canonical_taxon, TAXONOMY_SYNONYMS
from data_layer.external_adapters import fetch_gbif_species_occurrences
from decision_support.candidate_evaluator import evaluate_candidate_introduction
from data_layer.forest_baseline import construct_forest_baseline
from decision_support.report_generator import generate_scientific_markdown_report
from core_engine.stability import calculate_stability_metrics
from core_engine.model import build_calibrated_parameters
import numpy as np


class TestCandidateSpeciesAndTaxonomy:
    """Test suite ensuring data integrity, taxonomic canonical resolution, and zero stale candidate leakage."""

    def test_canonical_species_database_completeness(self):
        """Verify all 10 canonical Indian forest taxa are present with verified traits."""
        all_spp = list_all_species()
        assert len(all_spp) == 10
        canonical_names = {s["canonical_name"] for s in all_spp}
        expected_taxa = {
            "Lantana camara",
            "Senna spectabilis",
            "Prosopis juliflora",
            "Parthenium hysterophorus",
            "Chromolaena odorata",
            "Tectona grandis",
            "Shorea robusta",
            "Dalbergia latifolia",
            "Terminalia tomentosa",
            "Bambusa bambos"
        }
        assert canonical_names == expected_taxa

        for sp in all_spp:
            assert sp["canonical_name"] in SPECIES_DB
            assert sp["regional_status"] in ["NATIVE", "INVASIVE"]
            assert sp["max_height_m"] > 0
            assert 1 <= sp["shade_tolerance"] <= 5
            assert 1 <= sp["fire_tolerance"] <= 5
            assert 1 <= sp["drought_tolerance"] <= 5
            assert sp["optimal_temp_c"] > 0
            assert sp["optimal_rainfall_mm"] > 0
            assert sp["optimal_elevation_m"] > 0
            assert "provenance" in sp
            assert sp["citation_agency"] != ""

    def test_taxonomic_synonym_resolution(self):
        """Verify synonyms and vernacular names resolve strictly to canonical binomials."""
        cases = [
            ("Lantana camara L.", "Lantana camara"),
            ("lantana", "Lantana camara"),
            ("wild sage", "Lantana camara"),
            ("unni chedi", "Lantana camara"),
            ("Senna spectabilis (DC.) H.S.Irwin & Barneby", "Senna spectabilis"),
            ("cassia spectabilis", "Senna spectabilis"),
            ("Prosopis juliflora (Sw.) DC.", "Prosopis juliflora"),
            ("vilayati babool", "Prosopis juliflora"),
            ("seemai karuvelam", "Prosopis juliflora"),
            ("Parthenium hysterophorus L.", "Parthenium hysterophorus"),
            ("congress grass", "Parthenium hysterophorus"),
            ("Tectona grandis L.f.", "Tectona grandis"),
            ("teak", "Tectona grandis"),
            ("sagwan", "Tectona grandis"),
            ("Shorea robusta Roxb. ex Gaertn.f.", "Shorea robusta"),
            ("sal", "Shorea robusta"),
            ("Dalbergia latifolia Roxb.", "Dalbergia latifolia"),
            ("rosewood", "Dalbergia latifolia"),
            ("beete", "Dalbergia latifolia"),
            ("Terminalia tomentosa (Roxb. ex DC.) Wight & Arn.", "Terminalia tomentosa"),
            ("karimarudu", "Terminalia tomentosa")
        ]
        for query, expected_canonical in cases:
            resolved, status = resolve_canonical_taxon(query)
            assert resolved == expected_canonical
            assert status in ["EXACT_MATCH", "SYNONYM_RESOLVED", "CANONICAL_PARSED"]

    def test_dalbergia_latifolia_native_evaluation(self):
        """Verify Dalbergia latifolia evaluates as indigenous native with low risk and zero Lantana leakage."""
        eval_res = evaluate_candidate_introduction(
            species_name_input="Dalbergia latifolia",
            site_temperature_c=24.2,
            site_elevation_m=900.0,
            site_rainfall_mm=1250.0,
            site_native_biomass_mg_ha=158.4,
            target_region_state="Tamil Nadu"
        )
        assert eval_res["canonical_name"] == "Dalbergia latifolia"
        assert eval_res["family"] == "Fabaceae"
        assert eval_res["regional_status"] == "NATIVE"
        assert eval_res["status_category"] == "NATIVE_SPECIES"
        assert "LOW RISK" in eval_res["final_classification"]
        assert eval_res["risk_color"] == "#10b981"
        assert "Lantana" not in eval_res["verdict_summary"]
        assert "indigenous/native" in eval_res["verdict_summary"]
        assert eval_res["traits"]["allelopathy"] == "ABSENT"

    def test_lantana_camara_invasive_evaluation(self):
        """Verify Lantana camara evaluates as documented invasive with high/very high risk and allelopathy."""
        eval_res = evaluate_candidate_introduction(
            species_name_input="Lantana camara",
            site_temperature_c=24.2,
            site_elevation_m=900.0,
            site_rainfall_mm=1250.0,
            site_native_biomass_mg_ha=158.4,
            target_region_state="Tamil Nadu"
        )
        assert eval_res["canonical_name"] == "Lantana camara"
        assert eval_res["family"] == "Verbenaceae"
        assert eval_res["regional_status"] == "INVASIVE"
        assert eval_res["status_category"] == "DOCUMENTED_INVASIVE_OCCURRENCE"
        assert "HIGH RISK" in eval_res["final_classification"]
        assert eval_res["traits"]["allelopathy"] == "DOCUMENTED"
        assert eval_res["invasive_impact_index"]["invasive_impact_score"] > 30.0

    def test_tectona_grandis_evaluation_in_central_and_south_india(self):
        """Verify Tectona grandis (Teak) evaluates as indigenous timber species."""
        eval_res = evaluate_candidate_introduction(
            species_name_input="Teak",
            site_temperature_c=25.5,
            site_elevation_m=600.0,
            site_rainfall_mm=1400.0,
            site_native_biomass_mg_ha=174.2,
            target_region_state="Madhya Pradesh"
        )
        assert eval_res["canonical_name"] == "Tectona grandis"
        assert eval_res["regional_status"] == "NATIVE"
        assert "LOW RISK" in eval_res["final_classification"]
        assert eval_res["traits"]["fire_tolerance"] == "5 / 5"

    def test_forest_context_environmental_variation(self):
        """Verify candidate assessment yields distinct environmental suitability when evaluated under different forest baselines."""
        # Mudumalai (Tamil Nadu): Temp 24.2 C, Rain 1250 mm, Elev 900 m
        mudu_base = construct_forest_baseline("mudumalai")
        eval_mudu = evaluate_candidate_introduction(
            species_name_input="Senna spectabilis",
            site_temperature_c=mudu_base["climatology"]["mean_annual_temp_c"]["value"],
            site_elevation_m=900.0,
            site_rainfall_mm=mudu_base["climatology"]["annual_rainfall_mm"]["value"],
            site_native_biomass_mg_ha=mudu_base["vegetation_state"]["native_canopy_biomass_mg_ha"]["value"],
            target_region_state=mudu_base["state"]
        )

        # Gir (Gujarat): Temp 27.5 C, Rain 650 mm, Elev 300 m
        gir_base = construct_forest_baseline("gir")
        eval_gir = evaluate_candidate_introduction(
            species_name_input="Senna spectabilis",
            site_temperature_c=gir_base["climatology"]["mean_annual_temp_c"]["value"],
            site_elevation_m=300.0,
            site_rainfall_mm=gir_base["climatology"]["annual_rainfall_mm"]["value"],
            site_native_biomass_mg_ha=gir_base["vegetation_state"]["native_canopy_biomass_mg_ha"]["value"],
            target_region_state=gir_base["state"]
        )

        assert eval_mudu["canonical_name"] == eval_gir["canonical_name"] == "Senna spectabilis"
        # Gaussian environmental suitability should differ between humid Mudumalai and semi-arid Gir
        s_mudu = eval_mudu["environmental_suitability"]["s_composite"]
        s_gir = eval_gir["environmental_suitability"]["s_composite"]
        assert abs(s_mudu - s_gir) > 0.05
        assert s_mudu > s_gir  # Senna spectabilis thrives better in moist/moderate rainfall (1500mm opt) than arid 650mm

    def test_gbif_query_does_not_mutate_species_database(self):
        """Verify GBIF queries return valid records without altering the curated Species Database."""
        orig_lantana = get_species_record("Lantana camara")
        gbif_data = fetch_gbif_species_occurrences("Lantana camara", country_code="IN", limit=3)
        assert gbif_data["available"] is True
        assert gbif_data["total_documented_occurrences_in_country"] > 0
        current_lantana = get_species_record("Lantana camara")
        assert current_lantana == orig_lantana

    def test_decision_report_with_custom_candidate(self):
        """Verify scientific markdown report dynamically incorporates the requested candidate species."""
        baseline = construct_forest_baseline("mudumalai")
        cand_eval = evaluate_candidate_introduction(
            species_name_input="Dalbergia latifolia",
            site_temperature_c=24.2,
            site_elevation_m=900.0,
            site_rainfall_mm=1250.0,
            site_native_biomass_mg_ha=158.4,
            target_region_state="Tamil Nadu"
        )
        params = build_calibrated_parameters(0.85, 0.15, 1.0)
        init_state = np.array([158.4, 26.8, 6.2])
        stab = calculate_stability_metrics(init_state, params)

        report_md = generate_scientific_markdown_report(
            baseline=baseline,
            candidate_eval=cand_eval,
            scenarios=[],
            stability_data=stab,
            mode="RESEARCH MODE (STRICT SCIENTIFIC INTEGRITY)"
        )
        assert "Dalbergia latifolia" in report_md
        assert "**Target Evaluated Taxon:** *Dalbergia latifolia*" in report_md

