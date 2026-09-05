"""Specialty modules. Adding a specialty = new folder + one line here."""

from __future__ import annotations

from types import ModuleType

from digidoc.specialist import diabetic_foot

MODULES: dict[str, ModuleType] = {
    "diabetic_foot": diabetic_foot,
}


def get(name: str) -> ModuleType:
    if name not in MODULES:
        raise KeyError(f"unknown specialist module: {name}")
    return MODULES[name]


def get_chunk(key: str, section_id: str) -> dict | None:
    for module in MODULES.values():
        getter = getattr(module, "get_chunk", None)
        if getter:
            found = getter(key, section_id)
            if found:
                return found
    return None
