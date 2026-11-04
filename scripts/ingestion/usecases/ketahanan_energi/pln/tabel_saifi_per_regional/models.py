"""Pydantic schema — Tabel SAIFI Per Regional (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIFI)")
    tipe_baris: str | None = Field(default=None, alias="Tipe_Baris", description="Regional atau Nasional")
    saifi_2023: str | None = Field(default=None, alias="SAIFI_2023", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2023")
    saifi_2024: str | None = Field(default=None, alias="SAIFI_2024", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2024")
    saifi_2025: str | None = Field(default=None, alias="SAIFI_2025", description="Rata-rata frekuensi pemadaman per pelanggan tahun 2025")
    selisih_2024_2025: str | None = Field(default=None, alias="Selisih_2024_2025", description="SAIFI_2025 dikurangi SAIFI_2024. Negatif berarti frekuensi pemadaman menurun")
    perubahan_persen: str | None = Field(default=None, alias="Perubahan_Persen", description="Selisih_2024_2025 dibagi SAIFI_2024. Negatif berarti membaik")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    regional: str | None = Field(default=None, alias="Regional", description="SAIFI_2024")
    sumatera_dan_kalimantan: str | None = Field(default=None, alias="Sumatera dan Kalimantan", description="5.04")
    jawa_madura_dan_bali: str | None = Field(default=None, alias="Jawa, Madura, dan Bali", description="2.12")
    sulawesi_maluku_papua_dan_nusa_tenggara: str | None = Field(default=None, alias="Sulawesi, Maluku, Papua, dan Nusa Tenggara", description="4.87")
    jumlah_saifi: str | None = Field(default=None, alias="Jumlah SAIFI", description="3.23")

    model_config = {"populate_by_name": True, "extra": "ignore"}
