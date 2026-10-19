"""Unit tests for Kemlu Rekapitulasi Kasus WNI Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.kemlu.kasus_wni.models import (
    Record,
    KemluKasusWniRecord,
)
from ingestion.usecases.geopolitik.kemlu.kasus_wni.normalizer import (
    Normalizer,
    clean_str,
    parse_int_safe,
    normalize_single,
)
from ingestion.usecases.geopolitik.kemlu.kasus_wni.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated Kasus WNI record passes Pydantic validation."""
    data = {
        "id_kasus": "PWNI-2026-MY-412",
        "negara_kejadian": "Malaysia",
        "kategori_kasus": "Gaji Tidak Dibayar & Paspor Ditahan",
        "jumlah_korban_terlibat": 3,
        "tanggal_pengaduan": "2026-09-12",
        "status_penanganan": "Mediasi Selesai & Repatriasi",
        "bantuan_hukum_diberikan": "Safe House KJRI Penang & Pelunasan Hak Gaji",
    }
    rec = Record(**data)
    assert rec.id_kasus == "PWNI-2026-MY-412"
    assert rec.negara_kejadian == "Malaysia"
    assert rec.kategori_kasus == "Gaji Tidak Dibayar & Paspor Ditahan"
    assert rec.jumlah_korban_terlibat == 3
    assert rec.status_penanganan == "Mediasi Selesai & Repatriasi"
    assert "Direktorat Pelindungan WNI" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and defaults."""
    rec = Record(
        id_kasus="PWNI-TEST-01",
        negara_kejadian="Kamboja",
        kategori_kasus="Online Scam",
    )
    assert rec.id_kasus == "PWNI-TEST-01"
    assert rec.negara_kejadian == "Kamboja"
    assert rec.jumlah_korban_terlibat == 1
    assert rec.status_penanganan == "Dalam Proses"
    assert rec.tanggal_pengaduan is None
    assert rec.bantuan_hukum_diberikan is None


def test_parse_helpers():
    """Verify clean_str and parse_int_safe helper functions."""
    assert clean_str("  Kamboja  ") == "Kamboja"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None

    assert parse_int_safe("12") == 12
    assert parse_int_safe("1,500") == 1500
    assert parse_int_safe("..") == 1
    assert parse_int_safe(None) == 1


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Kasus": "PWNI-2026-KH-105",
        "Negara": "Kamboja",
        "Kategori Kasus": "Dugaan TPPO / Penipuan Online Scam",
        "Korban (Jiwa)": "12",
        "Tanggal Lapor": "2026-09-25",
        "Status Penanganan": "Dalam Proses Repatriasi",
        "Bantuan Diberikan": "Penyelamatan gabungan bersama Kepolisian Kamboja & KBRI Phnom Penh",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_kasus"] == "PWNI-2026-KH-105"
    assert item["negara_kejadian"] == "Kamboja"
    assert item["jumlah_korban_terlibat"] == 12
    assert item["status_penanganan"] == "Dalam Proses Repatriasi"
    assert "KBRI Phnom Penh" in item["bantuan_hukum_diberikan"]


def test_extractor_offline_fallback():
    """Verify extractor returns reference records when URL is unreachable."""
    ext = Extractor({"url": "http://invalid-peduliwni.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_kasus"] == "PWNI-2026-MY-412"
    assert records[0]["negara_kejadian"] == "Malaysia"
    assert records[0]["jumlah_korban_terlibat"] == 3
