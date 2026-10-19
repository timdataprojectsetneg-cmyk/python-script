"""Unit tests for OFAC Trade Sanctions Database Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.ofac.sanksi_perdagangan.models import Record, OfacSanksiPerdaganganRecord
from ingestion.usecases.geopolitik.ofac.sanksi_perdagangan.normalizer import (
    Normalizer,
    resolve_target_country,
    resolve_economic_sector,
    resolve_indonesia_impact,
)
from ingestion.usecases.geopolitik.ofac.sanksi_perdagangan.extractor import Extractor


def test_models_validation_valid():
    """Verify that a properly populated OFAC record passes Pydantic validation."""
    data = {
        "id_sanksi": "OFAC-SDN-306",
        "otoritas_penerbit": "US Department of the Treasury (OFAC)",
        "negara_sasaran": "Kuba",
        "sektor_terkena": "Sektor Keuangan, Perbankan Devisa & Transaksi SWIFT",
        "tanggal_efektif": "2026-06-15",
        "komoditas_terdampak_indonesia": "Pengawasan perbankan devisa transaksi komersial dan embargo barang asal AS",
        "potensi_dampak_ke_pelaku_usaha": "Waspada sanksi sekunder terhadap lembaga perbankan devisa",
        "nama_entitas": "BANCO NACIONAL DE CUBA",
        "tipe_entitas": "Entity / Corporate",
        "program_sanksi": "CUBA",
        "catatan_sanksi": "a.k.a. 'BNC'",
        "data_source": "US Department of the Treasury (OFAC)"
    }
    rec = Record(**data)
    assert rec.id_sanksi == "OFAC-SDN-306"
    assert rec.negara_sasaran == "Kuba"
    assert "Keuangan" in rec.sektor_terkena


def test_models_validation_defaults():
    """Verify model default values for minimal fields."""
    rec = Record(
        id_sanksi="OFAC-SDN-999",
        negara_sasaran="Federasi Rusia",
        sektor_terkena="Sektor Energi",
        tanggal_efektif="2026-06-15",
        komoditas_terdampak_indonesia="Komoditas ekspor",
        potensi_dampak_ke_pelaku_usaha="Waspada sanksi sekunder",
        nama_entitas="RUSSIA TECH CORP"
    )
    assert rec.otoritas_penerbit == "US Department of the Treasury (OFAC)"
    assert rec.tipe_entitas == "Entity / Corporate"
    assert rec.data_source == "US Department of the Treasury (OFAC)"


def test_resolve_target_country():
    """Verify country resolution from sanction program code."""
    assert resolve_target_country("RUSSIA-EO14024", "") == "Federasi Rusia"
    assert resolve_target_country("IRAN", "") == "Iran"
    assert resolve_target_country("CUBA", "") == "Kuba"
    assert resolve_target_country("BURMA", "") == "Myanmar"
    assert resolve_target_country("SDGT", "") == "Global / Anti-Terorisme Internasional"


def test_resolve_economic_sector():
    """Verify economic sector detection from entity name and program."""
    assert "Keuangan" in resolve_economic_sector("GAZPROMBANK", "entity", "RUSSIA")
    assert "Minyak" in resolve_economic_sector("NATIONAL IRANIAN OIL COMPANY", "entity", "IRAN")
    assert "Pelayaran" in resolve_economic_sector("MARITIME FLEET VESSEL", "vessel", "RUSSIA")
    assert "Penerbangan" in resolve_economic_sector("AEROCARIBBEAN AIRLINES", "entity", "CUBA")


def test_resolve_indonesia_impact():
    """Verify Indonesian commodity impact analysis."""
    assert "pupuk" in resolve_indonesia_impact("Federasi Rusia", "Sektor Energi")
    assert "minyak sawit" in resolve_indonesia_impact("Iran", "Sektor Keuangan")
    assert "kayu jati" in resolve_indonesia_impact("Myanmar", "Sektor Komersial")


def test_normalizer_flow():
    """Verify normalization flow from raw CSV row dict."""
    raw_row = {
        "ent_num": "306",
        "name": "BANCO NACIONAL DE CUBA",
        "type": "-0-",
        "program": "CUBA",
        "remarks": "a.k.a. 'BNC'."
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw_row])))
    assert len(results) == 1
    item = results[0]
    assert item["id_sanksi"] == "OFAC-SDN-306"
    assert item["negara_sasaran"] == "Kuba"
    assert item["tipe_entitas"] == "Entity / Corporate"
    assert "Keuangan" in item["sektor_terkena"]


def test_extractor_init_defaults():
    """Verify extractor initialization with default URL."""
    ext = Extractor({})
    assert "sanctionslistservice.ofac.treas.gov" in ext.url
