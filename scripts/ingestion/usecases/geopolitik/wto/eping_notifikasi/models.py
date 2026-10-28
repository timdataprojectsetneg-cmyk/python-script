"""Pydantic schema for Notifikasi ePing (WTO SPS/TBT notifications)."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotifikasiEPingRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str = Field(alias="id", description="ID unik notifikasi di ePing. Kunci dedup antar-pengambilan.")
    area: Optional[str] = Field(default=None, alias="area", description="Jenis notifikasi WTO: SPS atau TBT.")
    notificationtype: Optional[str] = Field(
        default=None,
        alias="notificationType",
        description="Regular notification, Emergency notification, Addendum, Corrigendum, Revision.",
    )
    distributiondate: Optional[date] = Field(
        default=None, alias="distributionDate", description="Tanggal notifikasi diedarkan WTO."
    )
    commentdeadlinedate: Optional[date] = Field(
        default=None, alias="commentDeadlineDate", description="Batas waktu negara anggota mengirim komentar."
    )
    proposedadoptiondate: Optional[date] = Field(
        default=None, alias="proposedAdoptionDate", description="Rencana tanggal adopsi aturan."
    )
    proposedentryintoforcedate: Optional[date] = Field(
        default=None, alias="proposedEntryIntoForceDate", description="Rencana tanggal mulai berlaku."
    )
    documentsymbol: Optional[str] = Field(
        default=None, alias="documentSymbol", description="Simbol dokumen WTO, mis. G/SPS/N/MEX/477 (sudah di-trim)."
    )
    notifyingmember: Optional[str] = Field(
        default=None, alias="notifyingMember", description="Anggota WTO yang menerbitkan aturan (negara mitra)."
    )
    notifyingmembercode: Optional[str] = Field(
        default=None, alias="notifyingMemberCode", description="Kode anggota ePing (C + kode numerik ISO 3166)."
    )
    titleplain: Optional[str] = Field(default=None, alias="titlePlain", description="Judul notifikasi tanpa HTML.")
    descriptionplain: Optional[str] = Field(
        default=None, alias="descriptionPlain", description="Ringkasan isi aturan tanpa HTML."
    )
    productsfreetextplain: Optional[str] = Field(
        default=None, alias="productsFreeTextPlain", description="Produk yang diatur (teks bebas)."
    )
    hscodetext: Optional[str] = Field(default=None, alias="hsCodeText", description="Daftar kode HS terdampak.")
    icscodetext: Optional[str] = Field(default=None, alias="icsCodeText", description="Kode standar ICS terkait.")
    keywords: Optional[str] = Field(default=None, alias="keywords", description="Kata kunci ePing, digabung '; '.")
    objectives: Optional[str] = Field(default=None, alias="objectives", description="Tujuan aturan, digabung '; '.")
    alltradingpartners: Optional[bool] = Field(
        default=None, alias="allTradingPartners", description="True = berlaku untuk semua mitra dagang."
    )
    countriesaffected: Optional[str] = Field(
        default=None, alias="countriesAffected", description="Negara terdampak, digabung '; '."
    )
    conformstandardyes: Optional[bool] = Field(
        default=None, alias="conformStandardYes", description="True = aturan sesuai standar internasional."
    )
    tradefacilitatingmeasure: Optional[bool] = Field(
        default=None, alias="tradeFacilitatingMeasure", description="True = notifikasi memfasilitasi perdagangan."
    )
    parentid: Optional[int] = Field(
        default=None, alias="parentId", description="ID notifikasi induk untuk addendum/revisi."
    )
    linktonotification: Optional[str] = Field(
        default=None, alias="linkToNotification", description="Tautan dokumen notifikasi resmi WTO."
    )
    notifieddocumentlink: Optional[str] = Field(
        default=None, alias="notifiedDocumentLink", description="Tautan dokumen aturan dari negara penerbit."
    )


Record = NotifikasiEPingRecord
