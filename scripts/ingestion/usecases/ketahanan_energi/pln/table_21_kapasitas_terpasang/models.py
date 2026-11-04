"""Pydantic schema — Table 21: Kapasitas Terpasang (MW) (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    unit_pln: str | None = Field(default=None, alias="Unit_PLN", description="Nama unit PLN (UID, UIW, UIP3B, UIK, PLN Indonesia Power, PLN Nusantara Power, dan seterusnya) atau baris agregat (Luar Jawa, Jawa, Proyek Pembangkitan, Indonesia)")
    tipe_baris: str | None = Field(default=None, alias="tipe_baris", description="Jenis baris: \"unit\", \"sub_unit\", \"subtotal_wilayah\", \"proyek\", \"total\", atau \"persentase\" (baris \"%\" di bawah Indonesia)")
    tahun: int | None = Field(default=None, alias="tahun", description="Tahun data (2025)")
    unit_pln: str | None = Field(default=None, alias="unit_pln", description="Nama unit PLN, baris agregat \"Luar Jawa\" dan \"Jawa\", \"Proyek Pembangkitan\", \"Indonesia\", atau \"% terhadap total\"")

    induk_unit: str | None = Field(default=None, alias="induk_unit", description="Nama unit induk untuk baris \"sub_unit\". Bernilai null untuk baris lain")
    kelompok_wilayah: str | None = Field(default=None, alias="kelompok_wilayah", description="Kelompok wilayah: \"Luar Jawa\" atau \"Jawa\". Bernilai null untuk baris proyek, total, dan persentase")
    plta_hydro_mw: float | None = Field(default=None, alias="plta_hydro_mw", description="Kapasitas PLTA (Hydro). Null jika \"-\"")
    pltm_mini_hydro_mw: float | None = Field(default=None, alias="pltm_mini_hydro_mw", description="Kapasitas PLTM (Mini Hydro). Null jika \"-\"")
    pltmh_micro_hydro_mw: float | None = Field(default=None, alias="pltmh_micro_hydro_mw", description="Kapasitas PLTMH (Micro Hydro). Null jika \"-\"")
    pltu_steam_mw: float | None = Field(default=None, alias="pltu_steam_mw", description="Kapasitas PLTU (Steam). Null jika \"-\"")
    pltg_gas_mw: float | None = Field(default=None, alias="pltg_gas_mw", description="Kapasitas PLTG (Gas). Null jika \"-\"")
    pltgu_combined_cycle_mw: float | None = Field(default=None, alias="pltgu_combined_cycle_mw", description="Kapasitas PLTGU (Combined Cycle). Null jika \"-\"")
    pltp_geothermal_mw: float | None = Field(default=None, alias="pltp_geothermal_mw", description="Kapasitas PLTP (Geothermal). Null jika \"-\"")
    pltd_diesel_mw: float | None = Field(default=None, alias="pltd_diesel_mw", description="Kapasitas PLTD (Diesel). Null jika \"-\"")
    pltmg_gas_engine_mw: float | None = Field(default=None, alias="pltmg_gas_engine_mw", description="Kapasitas PLTMG (Gas Engine). Null jika \"-\"")
    plt_surya_solar_mw: float | None = Field(default=None, alias="plt_surya_solar_mw", description="Kapasitas PLT Surya (Solar). Null jika \"-\"")
    plt_bayu_wind_mw: float | None = Field(default=None, alias="plt_bayu_wind_mw", description="Kapasitas PLT Bayu (Wind). Null jika \"-\"")
    plt_biomassa_mw: float | None = Field(default=None, alias="plt_biomassa_mw", description="Kapasitas PLT Biomassa (Biomass). Null jika \"-\"")
    sub_jumlah_mw: float | None = Field(default=None, alias="sub_jumlah_mw", description="Sub jumlah kapasitas dari seluruh jenis pembangkit milik PLN. Null jika \"-\"")
    sub_jumlah_persen: float | None = Field(default=None, alias="sub_jumlah_persen", description="Persentase sub jumlah terhadap total Indonesia. Null jika \"-\"")
    sewa_mw: float | None = Field(default=None, alias="sewa_mw", description="Kapasitas pembangkit sewa (Leased). Null jika \"-\"")
    ipp_mw: float | None = Field(default=None, alias="ipp_mw", description="Kapasitas pembangkit IPP. Null jika \"-\"")
    jumlah_mw: float | None = Field(default=None, alias="jumlah_mw", description="Jumlah total kapasitas (sub jumlah + sewa + IPP). Null jika \"-\"")
    jumlah_persen: float | None = Field(default=None, alias="jumlah_persen", description="Persentase jumlah terhadap total Indonesia. Null jika \"-\"")
    model_config = {"populate_by_name": True, "extra": "ignore"}
