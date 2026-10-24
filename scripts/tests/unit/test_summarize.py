"""Tests for heuristic title summarisation and its use in catalog slugs."""

from __future__ import annotations

import pytest

from ingestion.catalog.metadata_parser import derive_module_name
from ingestion.catalog.summarize import summarize_context


def test_summarize_keeps_table_title_after_report_prefix():
    text = (
        "PLN - Sustainability Report | "
        "Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan"
    )
    assert summarize_context(text, max_words=8) == (
        "Volume Pemakaian Sumber Energi Sesuai Sumber Energi Digunakan"
    )


def test_summarize_caps_words_at_eight():
    text = "satu dua tiga empat lima enam tujuh delapan sembilan sepuluh"
    assert summarize_context(text, max_words=8) == (
        "Satu Dua Tiga Empat Lima Enam Tujuh Delapan"
    )


def test_summarize_removes_trailing_qualifier():
    assert summarize_context("Konsumsi Energi dari Pemakaian Sumber Energi") == "Konsumsi Energi"


def test_summarize_removes_leading_table_noise():
    assert summarize_context("Tabel 1.2 Konsumsi Energi Nasional") == "1.2 Konsumsi Energi Nasional"


def test_summarize_validates_max_words():
    with pytest.raises(ValueError):
        summarize_context("teks", max_words=0)
    with pytest.raises(TypeError):
        summarize_context(None)  # type: ignore[arg-type]


def test_short_names_are_not_summarized():
    name = "HEESI 2025 Executive Summary- Natural Gas and Products"
    assert derive_module_name(name) == (
        "heesi_2025_executive_summary_natural_gas_and_products"
    )


def test_long_names_are_summarized_before_slugging():
    name = (
        "Tabel Konsumsi Energi Nasional dari Pemakaian Sumber Energi "
        "Tahun 2025 Menurut Sektor"
    )
    assert derive_module_name(name) == "konsumsi_energi_nasional"


def test_leading_section_numbers_are_removed():
    assert derive_module_name("6.2.9 LPG Supply and Demand") == "lpg_supply_and_demand"
    assert derive_module_name("6_2_9_lpg_supply_and_demand") == "lpg_supply_and_demand"
    assert derive_module_name("6.5.1 Geothermal Resources and Reserves") == (
        "geothermal_resources_and_reserves"
    )
    assert derive_module_name("2 Energy Balance Table") == "energy_balance_table"
    assert derive_module_name("5.1.2 Energy Consumption in Industrial Sector") == (
        "energy_consumption_in_industrial_sector"
    )


def test_leading_year_is_removed():
    assert derive_module_name("2025 Laporan Tahunan") == "laporan_tahunan"


def test_non_leading_numbers_are_preserved():
    assert derive_module_name("HEESI 2025 Executive Summary- Natural Gas and Products") == (
        "heesi_2025_executive_summary_natural_gas_and_products"
    )
    assert derive_module_name("3M Indonesia") == "3m_indonesia"
