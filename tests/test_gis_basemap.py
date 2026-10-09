"""
Tests for GIS Basemap Configuration and Tile Provider Verification.
Verifies:
1. /api/gis/areas returns carto_api_key field and protected areas.
2. CARTO_API_KEY environment variable is properly propagated.
3. Esri World Dark Gray Canvas base and reference tiles return valid map imagery (HTTP 200, valid image content, no watermark).
4. Verifies CARTO tile watermark behavior when unauthenticated.
"""

import os
import urllib.request
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_gis_areas_payload_has_carto_key_field(client):
    """Verifies that /api/gis/areas returns areas and the optional carto_api_key field."""
    res = client.get("/api/gis/areas")
    assert res.status_code == 200
    data = res.get_json()
    assert "areas" in data
    assert len(data["areas"]) >= 8
    assert "carto_api_key" in data


def test_gis_areas_propagates_env_carto_key(client, monkeypatch):
    """Verifies that CARTO_API_KEY environment variable is passed down to client."""
    monkeypatch.setenv("CARTO_API_KEY", "test_carto_key_abc123")
    res = client.get("/api/gis/areas")
    assert res.status_code == 200
    data = res.get_json()
    assert data["carto_api_key"] == "test_carto_key_abc123"


def test_esri_dark_gray_basemap_tiles_return_valid_imagery():
    """Verifies that the alternative Esri World Dark Gray Canvas tile returns valid geographic imagery."""
    # Test tile for Indian subcontinent at zoom 5 (x=23, y=14)
    base_url = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/5/14/23"
    req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0 FORESTDYN-GIS/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        content_type = resp.headers.get("Content-Type", "")
        assert "image" in content_type
        content = resp.read()
        assert len(content) > 1000
        # Check JPEG header SOI marker (0xFFD8)
        assert content[:2] == b"\xff\xd8"
        etag = resp.headers.get("ETag", "")
        assert not etag.startswith('"wm-')


def test_esri_dark_gray_reference_tiles_return_valid_imagery():
    """Verifies that the Esri World Dark Gray Reference (labels) tile returns valid transparent PNG imagery."""
    ref_url = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/5/14/23"
    req = urllib.request.Request(ref_url, headers={"User-Agent": "Mozilla/5.0 FORESTDYN-GIS/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        content_type = resp.headers.get("Content-Type", "")
        assert "image/png" in content_type
        content = resp.read()
        assert len(content) > 500
        # Check PNG header magic bytes
        assert content[:4] == b"\x89PNG"
        etag = resp.headers.get("ETag", "")
        assert not etag.startswith('"wm-')


def test_carto_unauthenticated_watermark_detection():
    """Confirms that unauthenticated CARTO requests return the warning watermark tile (wm- ETag)."""
    carto_url = "https://a.basemaps.cartocdn.com/dark_all/9/364/240.png"
    req = urllib.request.Request(carto_url, headers={"User-Agent": "Mozilla/5.0 FORESTDYN-GIS/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        assert resp.status == 200
        etag = resp.headers.get("ETag", "")
        # CARTO unauthenticated returns ETag starting with "wm-"
        assert "wm-" in etag
