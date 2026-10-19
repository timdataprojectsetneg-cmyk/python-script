"""Unit tests for Setpres Matriks Risiko Kunjungan Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.kunjungan_presiden.setpres.matriks_risiko_kunjungan.models import (
    Record,
    SetpresMatriksRisikoKunjunganRecord,
)
from ingestion.usecases.kunjungan_presiden.setpres.matriks_risiko_kunjungan.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.kunjungan_presiden.setpres.matriks_risiko_kunjungan.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated risk matrix record passes Pydantic validation."""
    data = {
        "id_risiko": "RSK-2026-01",
        "kategori_risiko": "Cuaca",
        "deskripsi_ancaman": "Hujan deras berpotensi menggenangi lapangan parkir luar lokasi acara",
        "tingkat_probabilitas": "Sedang",
        "tingkat_dampak": "Signifikan",
        "rencana_mitigasi": "Siapkan paviliun tenda tertutup dan rute drop-off beratap darurat",
        "penanggung_jawab_pic": "Satgas Pemda & Kodim",
    }
    rec = Record(**data)
    assert rec.id_risiko == "RSK-2026-01"
    assert rec.kategori_risiko == "Cuaca"
    assert rec.tingkat_probabilitas == "Sedang"
    assert rec.tingkat_dampak == "Signifikan"
    assert rec.penanggung_jawab_pic == "Satgas Pemda & Kodim"
    assert "Sekretariat Presiden RI" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_risiko="RSK-TEST-01",
        kategori_risiko="Protokoler",
        deskripsi_ancaman="Kendala alur kedatangan",
    )
    assert rec.id_risiko == "RSK-TEST-01"
    assert rec.kategori_risiko == "Protokoler"
    assert rec.tingkat_probabilitas == "Sedang"
    assert rec.tingkat_dampak == "Signifikan"
    assert rec.rencana_mitigasi is None


def test_clean_str_helper():
    """Verify clean_str helper function."""
    assert clean_str("  Paspampres  ") == "Paspampres"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Risiko": "RSK-2026-02",
        "Kategori": "Medis",
        "Deskripsi Ancaman": "Kemacetan rute rujukan darurat saat jam pulang kerja",
        "Probabilitas": "Tinggi",
        "Dampak": "Kritis",
        "Rencana Mitigasi": "Sterilisasi jalur evakuasi oleh Ditlantas dan siagakan helikopter medis",
        "PIC Satgas": "Paspampres & Ditlantas",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_risiko"] == "RSK-2026-02"
    assert item["kategori_risiko"] == "Medis"
    assert item["tingkat_probabilitas"] == "Tinggi"
    assert item["tingkat_dampak"] == "Kritis"
    assert item["penanggung_jawab_pic"] == "Paspampres & Ditlantas"


def test_extractor_offline_fallback():
    """Verify extractor returns reference presidential visit risk records."""
    ext = Extractor({"url": "http://invalid-setneg.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_risiko"] == "RSK-2026-01"
    assert records[0]["kategori_risiko"] == "Cuaca"
    assert records[1]["kategori_risiko"] == "Medis"
