from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class VariantData(BaseModel):
    alt: str | None = None
    cdot: str | None = None
    cdot_alt: str | None = None
    cdot_ins: str | None = None
    cdot_pos: str | None = None
    cdot_pos2: str | None = None
    cdot_pos3: str | None = None
    cdot_pos4: str | None = None
    cdot_ref: str | None = None
    cdot_type: str | None = None
    pdot: str | None = None
    pdot_from: str | None = None
    pdot_pos: str | None = None
    pdot_to: str | None = None
    ref: str | None = None
    transcript: str | None = None
    transcript_number: str | None = None
    transcript_version: str | None = None
    chr: str | None = None
    clingen_id: str | None = None
    clingen_url: str | None = None
    gene: str | None = None
    pos: str | None = None
    rs: str | None = None
    rs_url: str | None = None
    to: str | None = None


class VariantDataScheme(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    search_term: str = Field(index=True)

    gene: str | None = Field(default=None, index=True)
    transcript: str | None = Field(default=None, index=True)
    transcript_number: str | None = Field(default=None)
    transcript_version: str | None = Field(default=None)
    chr: str | None = Field(default=None, index=True)
    pos: str | None = Field(default=None, index=True)
    ref: str | None = Field(default=None)
    alt: str | None = Field(default=None)

    cdot: str | None = Field(default=None, index=True)
    cdot_pos: str | None = Field(default=None)
    cdot_ref: str | None = Field(default=None)
    cdot_alt: str | None = Field(default=None)
    cdot_type: str | None = Field(default=None)
    cdot_ins: str | None = Field(default=None)
    cdot_pos2: str | None = Field(default=None)
    cdot_pos3: str | None = Field(default=None)
    cdot_pos4: str | None = Field(default=None)

    pdot: str | None = Field(default=None)
    pdot_pos: str | None = Field(default=None)
    pdot_from: str | None = Field(default=None)
    pdot_to: str | None = Field(default=None)

    rs: str | None = Field(default=None, index=True)
    rs_url: str | None = Field(default=None)
    clingen_id: str | None = Field(default=None)
    clingen_url: str | None = Field(default=None)
    to: str | None = Field(default=None)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Europe/Amsterdam")),
        nullable=False,
    )

    iupdated_at: datetime = Field(
        default_factory=lambda: datetime.now(ZoneInfo("Europe/Amsterdam")),
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(ZoneInfo("Europe/Amsterdam"))
        },
    )

    sources: list["VariantSource"] = Relationship(back_populates="variant")

class VariantSource(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    variant_id: int = Field(foreign_key="variantdatascheme.id", index=True)
    field_name: str = Field(index=True)  # 'gene', 'cdot', 'alt', etc.
    field_value: str
    source_name: str = Field(index=True)  # 'ClinVar', 'search', etc.

    variant: VariantDataScheme = Relationship(back_populates="sources")
