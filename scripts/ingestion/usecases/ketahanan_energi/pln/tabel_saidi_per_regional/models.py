"""Pydantic schema — Tabel Saidi Per Regional (mirrors the Data Dictionary)."""

from pydantic import BaseModel, Field


class Record(BaseModel):
    regional: str | None = Field(default=None, alias="Regional", description="Kelompok regional: Sumatera dan Kalimantan, Jawa Madura dan Bali, Sulawesi Maluku Papua dan Nusa Tenggara, atau baris total (Jumlah SAIDI)")
    tipe_baris: str | None = Field(default=None, alias="Tipe_Baris", description="Regional atau Nasional")
    saidi_2023: str | None = Field(default=None, alias="SAIDI_2023", description="Rata-rata lama pemadaman per pelanggan tahun 2023")
    saidi_2024: str | None = Field(default=None, alias="SAIDI_2024", description="Rata-rata lama pemadaman per pelanggan tahun 2024")
    saidi_2025: str | None = Field(default=None, alias="SAIDI_2025", description="Rata-rata lama pemadaman per pelanggan tahun 2025")
    selisih_2024_2025: str | None = Field(default=None, alias="Selisih_2024_2025", description="SAIDI_2025 dikurangi SAIDI_2024. Negatif berarti durasi pemadaman menurun")
    perubahan_persen: str | None = Field(default=None, alias="Perubahan_Persen", description="Selisih_2024_2025 dibagi SAIDI_2024. Negatif berarti membaik")
    sample_data: str | None = Field(default=None, alias="Sample Data")
    regional: str | None = Field(default=None, alias="Regional", description="SAIDI_2024")
    sumatera_dan_kalimantan: str | None = Field(default=None, alias="Sumatera dan Kalimantan", description="626.67")
    jawa_madura_dan_bali: str | None = Field(default=None, alias="Jawa, Madura, dan Bali", description="158.34")
    sulawesi_maluku_papua_dan_nusa_tenggara: str | None = Field(default=None, alias="Sulawesi, Maluku, Papua, dan Nusa Tenggara", description="466.89")
    jumlah_saidi: str | None = Field(default=None, alias="Jumlah SAIDI", description="320.24")

    model_config = {"populate_by_name": True, "extra": "ignore"}
