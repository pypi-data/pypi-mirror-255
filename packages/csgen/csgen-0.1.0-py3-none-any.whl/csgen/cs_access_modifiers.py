from __future__ import annotations

from enum import Flag


class CSharpModifierBase(Flag):
    def to_list(self) -> list[CSharpModifierBase]:
        # get flags that are set in order
        all_flags = [flag for flag in type(self) if self & flag]
        all_flags.sort(key=lambda flag: flag.value)
        return [flag for flag in all_flags if self & flag]

    def to_cs(self) -> str:
        return " ".join(flag.name.lower().replace("_", " ") for flag in self.to_list())


class PropertyModifier(CSharpModifierBase):
    PUBLIC = 1 << 10
    PRIVATE = 1 << 11
    PROTECTED = 1 << 12
    INTERNAL = 1 << 13
    FILE = 1 << 14
    PROTECTED_INTERNAL = PROTECTED | INTERNAL
    PRIVATE_PROTECTED = PRIVATE | PROTECTED
    PRIVATE_INTERNAL = PRIVATE | INTERNAL

    STATIC = 1 << 30
    EXTERN = 1 << 31
    NEW = 1 << 32
    VIRTUAL = 1 << 33
    ABSTRACT = 1 << 34
    SEALED = 1 << 35
    OVERRIDE = 1 << 36
    READONLY = 1 << 37
    UNSAFE = 1 << 38
    REQUIRED = 1 << 39
    VOLATILE = 1 << 40
    ASYNC = 1 << 41
    PARTIAL = 1 << 50


class ClassModifier(CSharpModifierBase):
    PUBLIC = 1 << 10
    PRIVATE = 1 << 11
    PROTECTED = 1 << 12
    INTERNAL = 1 << 13
    FILE = 1 << 14
    PROTECTED_INTERNAL = PROTECTED | INTERNAL
    PRIVATE_PROTECTED = PRIVATE | PROTECTED
    PRIVATE_INTERNAL = PRIVATE | INTERNAL

    STATIC = 1 << 30
    EXTERN = 1 << 31
    NEW = 1 << 32
    VIRTUAL = 1 << 33
    ABSTRACT = 1 << 34
    SEALED = 1 << 35
    OVERRIDE = 1 << 36
    READONLY = 1 << 37
    UNSAFE = 1 << 38
    REQUIRED = 1 << 39
    VOLATILE = 1 << 40
    ASYNC = 1 << 41
    PARTIAL = 1 << 50
