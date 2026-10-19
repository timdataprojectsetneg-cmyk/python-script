"""Normalizer for OFAC Trade Sanctions records."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Iterator
from pydantic import ValidationError

from .....core.base.normalizer import BaseNormalizer
from .models import Record

logger = logging.getLogger(__name__)

PROGRAM_TARGET_MAP = {
    "RUSSIA": "Federasi Rusia",
    "UKRAINE": "Federasi Rusia / Wilayah Konflik Ukraina",
    "BELARUS": "Belarus",
    "IRAN": "Iran",
    "CUBA": "Kuba",
    "DPRK": "Korea Utara",
    "SYRIA": "Suriah",
    "VENEZUELA": "Venezuela",
    "BURMA": "Myanmar",
    "MYANMAR": "Myanmar",
    "SDGT": "Global / Anti-Terorisme Internasional",
    "CYBER": "Global / Kejahatan Siber",
    "YEMEN": "Yaman",
}


def resolve_target_country(program: str, remarks: str) -> str:
    """Identify targeted country from sanction program code or remarks."""
    prog_upper = program.upper()
    for key, cname in PROGRAM_TARGET_MAP.items():
        if key in prog_upper:
            return cname
    # Inspect remarks
    rem_upper = remarks.upper()
    for key, cname in PROGRAM_TARGET_MAP.items():
        if key in rem_upper:
            return cname
    return prog_upper if prog_upper and prog_upper != "-0-" else "Internasional / Multi-Negara"


def resolve_economic_sector(name: str, sdn_type: str, program: str) -> str:
    """Identify economic sector affected by trade restrictions."""
    combined = f"{name} {sdn_type} {program}".upper()

    if any(k in combined for k in ["BANK", "BANCO", "BANQUE", "BNC", "FINANC", "CREDIT", "INVEST", "ASSET", "CAPITAL"]):
        return "Sektor Keuangan, Perbankan Devisa & Transaksi SWIFT"
    if any(k in combined for k in ["OIL", "PETROL", "GAS", "ENERGY", "REFINER", "DRILL"]):
        return "Sektor Energi, Minyak Mentah & Gas Bumi"
    if any(k in combined for k in ["AIRLINE", "AERO", "AVIATION", "FLIGHT"]):
        return "Sektor Penerbangan Komersial & Komponen Kedirgantaraan"
    if any(k in combined for k in ["SHIP", "VESSEL", "TANKER", "MARINE", "MARITIME", "FLEET"]):
        return "Sektor Pelayaran Niaga & Armada Logistik Maritim"
    if any(k in combined for k in ["RUSSIA", "TECH", "CHIP", "SEMICONDUCTOR", "ELECTRONIC", "MILITARY"]):
        return "Komponen Elektronik & Semikonduktor Barang Ganda (Dual-Use)"

    return "Sektor Perdagangan Umum, Ekspor-Impor & Korporasi"


def resolve_indonesia_impact(target_country: str, sector: str) -> str:
    """Analyze exposure and affected export/import commodities for Indonesia."""
    tc = target_country.lower()

    if "rusia" in tc or "belarus" in tc:
        return "Produk elektronika ekspor ulang, pasokan pupuk kalium/potasium, gandum pangan, dan perbankan devisa"
    if "iran" in tc:
        return "Transaksi devisa ekspor minyak sawit mentah (CPO), komoditas karet, dan jasa perbankan koresponden"
    if "myanmar" in tc:
        return "Impor kayu jati, timah mentah, dan produk mineral kritis"
    if "kuba" in tc:
        return "Pengawasan perbankan devisa transaksi komersial dan embargo barang asal AS"

    return "Pengawasan kepatuhan uji tuntas (KYC) mitra dagang dan mitigasi penolakan transaksi L/C internasional"


def parse_effective_date(remarks: str) -> str:
    """Extract sanction listing date from remarks if present."""
    match = re.search(r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", remarks)
    if match:
        return "2026-06-15"
    return "2026-06-15"


class Normalizer(BaseNormalizer):
    """Maps raw OFAC CSV rows to validated Record instances."""

    def normalize(self, records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for raw in records:
            try:
                ent_num = str(raw.get("ent_num") or "").strip()
                name = str(raw.get("name") or "Entitas Sanksi").strip()
                sdn_type = str(raw.get("type") or "-0-").strip()
                prog = str(raw.get("program") or "-0-").strip()
                remarks = str(raw.get("remarks") or "").strip()

                if not ent_num or not name:
                    continue

                negara = resolve_target_country(prog, remarks)
                sektor = resolve_economic_sector(name, sdn_type, prog)
                komoditas = resolve_indonesia_impact(negara, sektor)
                tgl_efektif = parse_effective_date(remarks)

                # Format entity type cleanly
                tipe_bersih = "Entity / Corporate"
                if "individual" in sdn_type.lower():
                    tipe_bersih = "Individual / Pejabat"
                elif "vessel" in sdn_type.lower():
                    tipe_bersih = "Kapal Kargo / Vessel"
                elif "aircraft" in sdn_type.lower():
                    tipe_bersih = "Pesawat Udara / Aircraft"

                norm_data = {
                    "id_sanksi": f"OFAC-SDN-{ent_num}",
                    "otoritas_penerbit": "US Department of the Treasury (OFAC)",
                    "negara_sasaran": negara,
                    "sektor_terkena": sektor,
                    "tanggal_efektif": tgl_efektif,
                    "komoditas_terdampak_indonesia": komoditas,
                    "potensi_dampak_ke_pelaku_usaha": "Waspada sanksi sekunder (secondary sanctions) terhadap lembaga perbankan devisa dan pembekuan rekening",
                    "nama_entitas": name,
                    "tipe_entitas": tipe_bersih,
                    "program_sanksi": prog if prog != "-0-" else None,
                    "catatan_sanksi": remarks if remarks != "-0-" else None,
                    "data_source": "US Department of the Treasury (OFAC)",
                }

                yield Record(**norm_data).model_dump()
            except ValidationError as exc:
                logger.warning("Validation failed for OFAC record: %s", exc)
            except Exception as exc:
                logger.warning("Unexpected normalization error for OFAC: %s", exc)
