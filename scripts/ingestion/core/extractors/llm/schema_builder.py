"""Translate optional metadata into an output contract and JSON Schema.

`metadata` may be a plain dict, a JSON path/string, a Pydantic model class, or a
:class:`~ingestion.core.extractors.pdf.models.Dictionary`. The resulting
:class:`OutputSchema` is used both for the LLM prompt and for Python-side
validation. When metadata is omitted the schema is permissive (the model proposes
the structure, and validation only requires objects).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Literal, Union, get_args, get_origin

from ....exceptions import ConfigError

__all__ = [
    "OutputField",
    "OutputSchema",
    "build_schema",
    "schema_to_json",
]

_TYPE_ALIASES = {
    "str": "string",
    "string": "string",
    "text": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "decimal": "number",
    "num": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "date": "date",
    "datetime": "datetime",
    "timestamp": "datetime",
    "object": "object",
    "dict": "object",
    "map": "object",
    "json": "object",
    "array": "array",
    "list": "array",
    "any": "any",
}

_NULL_TYPES = {"null", "none"}


@dataclass(frozen=True)
class OutputField:
    name: str
    type: str = "string"
    description: str = ""
    enum: tuple[Any, ...] | None = None
    required: bool = False
    nullable: bool = True

    def json_schema(self) -> Dict[str, Any]:
        if self.type == "any":
            node: Dict[str, Any] = {}
        else:
            node = {"type": self.type if self.type not in ("date", "datetime") else "string"}
            if self.type in ("date", "datetime"):
                node["format"] = "date" if self.type == "date" else "date-time"
        if self.description:
            node["description"] = self.description
        if self.enum:
            values = list(self.enum)
            if self.nullable and None not in values:
                values.append(None)
            node["enum"] = values
        if self.nullable and self.type != "any" and "type" in node:
            node["type"] = [node["type"], "null"]
        return node


@dataclass
class OutputSchema:
    name: str = "Record"
    fields: list[OutputField] = field(default_factory=list)

    @property
    def names(self) -> list[str]:
        return [field.name for field in self.fields]

    def field(self, name: str) -> OutputField | None:
        return next((field for field in self.fields if field.name == name), None)

    def json_schema(self) -> Dict[str, Any]:
        properties = {field.name: field.json_schema() for field in self.fields}
        required = [field.name for field in self.fields if field.required]
        node: Dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "additionalProperties": False,
        }
        if required:
            node["required"] = required
        return node


def _normalise_type(value: Any) -> tuple[str, bool]:
    """Return ``(json_type, nullable)`` from a type value or list of values."""
    nullable = False
    if isinstance(value, (list, tuple, set)):
        nullable = any(str(item).strip().lower() in _NULL_TYPES for item in value)
        values = [item for item in value if str(item).strip().lower() not in _NULL_TYPES]
        if not values:
            return "any", True
        if len(values) > 1:
            # A union of concrete types is kept permissive.
            return "any", nullable
        value = values[0]
    text = str(value or "string").strip().lower()
    parts = [part.strip() for part in re.split(r"[|,]", text) if part.strip()]
    nullable = nullable or any(part in _NULL_TYPES for part in parts)
    parts = [part for part in parts if part not in _NULL_TYPES]
    if not parts:
        return "any", True
    if len(parts) > 1:
        return "any", nullable
    normalised = _TYPE_ALIASES.get(parts[0])
    if normalised is None:
        raise ConfigError(f"Unsupported metadata type: {value!r}")
    return normalised, nullable


def _field_from_spec(name: str, spec: Any) -> OutputField:
    if isinstance(spec, str):
        type_name, nullable = _normalise_type(spec)
        return OutputField(name=name, type=type_name, nullable=nullable)
    if not isinstance(spec, dict):
        raise ConfigError(f"Metadata field {name!r} must be a dict or type string")

    type_name, nullable = _normalise_type(spec.get("type", "string"))
    required = bool(spec.get("required", False))
    if "nullable" not in spec:
        # Missing values are represented as null (FR-08); required fields are
        # the exception because validation rejects null for them.
        nullable = not required
    enum = spec.get("enum")
    if enum is not None:
        if not isinstance(enum, (list, tuple)):
            raise ConfigError(f"Metadata enum for {name!r} must be a list")
        enum = tuple(enum)
        if any(value is None for value in enum):
            nullable = True
    if "nullable" in spec:
        nullable = bool(spec["nullable"])
    return OutputField(
        name=name,
        type=type_name,
        description=str(spec.get("description") or ""),
        enum=enum,
        required=required,
        nullable=nullable,
    )


def _from_dict(metadata: Dict[str, Any]) -> OutputSchema | None:
    if "properties" in metadata and isinstance(metadata["properties"], dict):
        fields = [
            _field_from_spec(name, spec)
            for name, spec in metadata["properties"].items()
        ]
        required = set(metadata.get("required") or [])
        if required:
            fields = [
                OutputField(
                    name=field.name,
                    type=field.type,
                    description=field.description,
                    enum=field.enum,
                    required=True,
                    nullable=field.nullable,
                )
                for field in fields
            ]
        return OutputSchema(name=str(metadata.get("title") or "Record"), fields=fields)

    if isinstance(metadata.get("fields"), list):
        fields = []
        for entry in metadata["fields"]:
            if not isinstance(entry, dict) or not entry.get("name"):
                continue
            spec = {key: value for key, value in entry.items() if key not in ("name", "aliases")}
            fields.append(_field_from_spec(str(entry["name"]), spec))
        return OutputSchema(name=str(metadata.get("name") or "Record"), fields=fields)

    if isinstance(metadata.get("fields"), dict):
        return OutputSchema(
            name=str(metadata.get("name") or "Record"),
            fields=[_field_from_spec(name, spec) for name, spec in metadata["fields"].items()],
        )

    # Flat mapping: {"tahun": {"type": "integer"}, "nilai": "number"}.
    if metadata and all(isinstance(value, (dict, str)) for value in metadata.values()):
        return OutputSchema(
            name=str(metadata.get("name") or "Record") if isinstance(metadata.get("name"), str) else "Record",
            fields=[
                _field_from_spec(name, spec)
                for name, spec in metadata.items()
                if name != "name"
            ],
        )
    return None


def _annotation_type(annotation: Any, default: Any) -> tuple[str, bool]:
    """Map a Python/Pydantic annotation to ``(type, nullable)``."""
    nullable = default is None
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, getattr(__import__("types"), "UnionType", Union)):
        non_none = [arg for arg in args if arg is not type(None)]
        nullable = nullable or any(arg is type(None) for arg in args)
        if len(non_none) == 1:
            return _annotation_type(non_none[0], default)
        return "any", True
    if origin in (list, tuple, set):
        return "array", nullable
    if origin is dict:
        return "object", nullable
    if origin is Literal:
        return "string", nullable

    if annotation is str:
        return "string", nullable
    if annotation is int:
        return "integer", nullable
    if annotation is float:
        return "number", nullable
    if annotation is bool:
        return "boolean", nullable
    if annotation is date:
        return "date", nullable
    if annotation in (datetime,) or getattr(annotation, "__name__", "") == "datetime":
        return "datetime", nullable
    if annotation in (list, tuple, set):
        return "array", nullable
    if annotation is dict:
        return "object", nullable
    if annotation is Any:
        return "any", True
    enum_values = getattr(annotation, "__members__", None)
    if enum_values:
        return "string", nullable
    return "string", nullable


def _from_pydantic(model: type) -> OutputSchema:
    fields: list[OutputField] = []
    for name, info in getattr(model, "model_fields", {}).items():
        type_name, nullable = _annotation_type(info.annotation, info.default)
        enum = None
        args = get_args(info.annotation)
        for arg in args:
            if get_origin(arg) is Literal:
                enum = tuple(get_args(arg))
                break
            members = getattr(arg, "__members__", None)
            if members:
                enum = tuple(member.value for member in members.values())
                break
        if enum is None:
            members = getattr(info.annotation, "__members__", None)
            if members:
                enum = tuple(member.value for member in members.values())
        fields.append(
            OutputField(
                name=name,
                type=type_name,
                description=info.description or "",
                enum=enum,
                required=info.is_required(),
                nullable=nullable or not info.is_required(),
            )
        )
    return OutputSchema(name=getattr(model, "__name__", "Record"), fields=fields)


def _from_dictionary(dictionary: Any) -> OutputSchema:
    fields = [
        OutputField(
            name=field.name,
            type=_normalise_type(field.type)[0],
            description=field.description or "",
            required=bool(getattr(field, "required", False)),
            nullable=True,
        )
        for field in getattr(dictionary, "fields", [])
    ]
    return OutputSchema(name=getattr(dictionary, "name", "Record"), fields=fields)


def build_schema(metadata: Any) -> OutputSchema | None:
    """Build the output contract, or ``None`` for a permissive extraction."""
    if metadata is None:
        return None
    if isinstance(metadata, OutputSchema):
        return metadata
    if isinstance(metadata, str):
        text = metadata.strip()
        if not text:
            return None
        if text.startswith(("{", "[")):
            metadata = json.loads(text)
        else:
            path = Path(text).expanduser()
            if not path.exists():
                raise ConfigError(f"Metadata file not found: {metadata}")
            metadata = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(metadata, dict):
        schema = _from_dict(metadata)
        if schema is None:
            raise ConfigError("Metadata must define fields, properties, or a type map")
        return schema
    if isinstance(metadata, type) and hasattr(metadata, "model_fields"):
        return _from_pydantic(metadata)
    if hasattr(metadata, "fields"):
        return _from_dictionary(metadata)
    raise ConfigError("Unsupported metadata: use a dict, JSON path/string, Pydantic model, or Dictionary")


def schema_to_json(schema: OutputSchema | None) -> Dict[str, Any] | None:
    return schema.json_schema() if schema is not None else None
