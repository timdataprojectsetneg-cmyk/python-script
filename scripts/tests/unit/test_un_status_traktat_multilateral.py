"""Unit tests for UN Status Traktat Multilateral Ingestion Module."""

import pytest
from pydantic import ValidationError

from ingestion.usecases.geopolitik.un.status_traktat_multilateral.models import (
    Record,
    UnStatusTraktatMultilateralRecord,
)
from ingestion.usecases.geopolitik.un.status_traktat_multilateral.normalizer import (
    Normalizer,
    clean_str,
    normalize_single,
)
from ingestion.usecases.geopolitik.un.status_traktat_multilateral.extractor import (
    Extractor,
    OFFLINE_FALLBACK_DATA,
)


def test_models_validation_valid():
    """Verify that a properly populated multilateral treaty record passes Pydantic validation."""
    data = {
        "id_traktat": "UNTC-XXVII-7",
        "nama_konvensi_internasional": "Paris Agreement under UNFCCC (Perubahan Iklim)",
        "organisasi_penyimpan_depository": "Sekjen PBB",
        "tanggal_adopsi_dunia": "2015-12-12",
        "status_keikutsertaan_indonesia": "Pihak (Diratifikasi)",
        "dokumen_pengesahan_uu_ri": "UU No. 16 Tahun 2016",
        "tanggal_penyerahan_instrumen": "2016-10-31",
        "catatan_reservasi_deklarasi": "Deklarasi kedaulatan kepulauan dan komitmen NDC",
    }
    rec = Record(**data)
    assert rec.id_traktat == "UNTC-XXVII-7"
    assert rec.nama_konvensi_internasional == "Paris Agreement under UNFCCC (Perubahan Iklim)"
    assert rec.organisasi_penyimpan_depository == "Sekjen PBB"
    assert rec.status_keikutsertaan_indonesia == "Pihak (Diratifikasi)"
    assert rec.dokumen_pengesahan_uu_ri == "UU No. 16 Tahun 2016"
    assert "United Nations Treaty Collection" in rec.data_source


def test_models_validation_minimal():
    """Verify minimal field validation and default fallback values."""
    rec = Record(
        id_traktat="UNTC-TEST-01",
        nama_konvensi_internasional="International Health Regulations",
    )
    assert rec.id_traktat == "UNTC-TEST-01"
    assert rec.organisasi_penyimpan_depository == "Sekjen PBB"
    assert rec.status_keikutsertaan_indonesia == "Pihak (Diratifikasi)"
    assert rec.dokumen_pengesahan_uu_ri is None
    assert rec.catatan_reservasi_deklarasi is None


def test_clean_str_helper():
    """Verify clean_str helper function."""
    assert clean_str("  Sekjen PBB  ") == "Sekjen PBB"
    assert clean_str("..") is None
    assert clean_str("-") is None
    assert clean_str("NA") is None
    assert clean_str(None) is None


def test_normalizer_flow():
    """Verify normalizer maps dictionary into validated payload."""
    raw = {
        "ID Traktat": "UNTC-XVIII-14",
        "Nama Konvensi": "Traktat Pelarangan Senjata Nuklir (TPNW)",
        "Depository": "Sekjen PBB",
        "Tanggal Adopsi": "2017-07-07",
        "Status RI": "Pihak (Diratifikasi)",
        "UU Ratifikasi": "UU No. 22 Tahun 2023",
        "Tanggal Deposit": "2023-11-24",
        "Reservasi/Deklarasi": "Tanpa reservasi",
    }
    norm = Normalizer()
    results = list(norm.normalize(iter([raw])))
    assert len(results) == 1
    item = results[0]
    assert item["id_traktat"] == "UNTC-XVIII-14"
    assert item["dokumen_pengesahan_uu_ri"] == "UU No. 22 Tahun 2023"
    assert item["status_keikutsertaan_indonesia"] == "Pihak (Diratifikasi)"


def test_extractor_offline_fallback():
    """Verify extractor returns reference multilateral treaty records."""
    ext = Extractor({"url": "http://invalid-untc-domain.local", "max_records": 3, "timeout": 1})
    records = list(ext.extract())
    assert len(records) == 3
    assert records[0]["id_traktat"] == "UNTC-XXVII-7"
    assert "Paris Agreement" in records[0]["nama_konvensi_internasional"]
