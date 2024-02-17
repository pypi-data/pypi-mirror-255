"""Diff util for dataclasses."""
import io
import os
import re
import sys
from collections.abc import Callable
from enum import Enum
from typing import Any, TextIO

import deepdiff

from classdiff.diff_object import Format
from classdiff.utils import Font

# https://stackoverflow.com/a/14693789/2274551
ansi_escape = re.compile(
    r"""
   \x1B  # ESC
   (?:   # 7-bit C1 Fe (except CSI)
       [@-Z\\-_]
   |     # or [ for CSI, followed by a control sequence
       \[
       [0-?]*  # Parameter bytes
       [ -/]*  # Intermediate bytes
       [@-~]   # Final byte
   )
""",
    re.VERBOSE,
)


class DiffType(Enum):
    """
    Types of diff.

    DiffType is an enum class for change types that maps to a string
    representation of how to represent each diff type.
    """

    ADDED = "+"
    REMOVED = "-"
    CHANGED = "~"
    TYPECHANGED = "!"
    UNCHANGED = " "

    @staticmethod
    def from_types(old: Any, new: Any) -> "DiffType":
        """
        Generate diff type from two types.

        Compare two objects and return the matching diff type based on the
        values.
        """
        if old == new:
            return DiffType.UNCHANGED

        if old is not None and new is None:
            return DiffType.REMOVED

        if old is None and new is not None:
            return DiffType.ADDED

        if type(old) != type(new):
            return DiffType.TYPECHANGED

        return DiffType.CHANGED

    def color(self) -> str:
        """Get the ansi code for the color used for the diff type."""
        match self:
            case DiffType.ADDED:
                return Font.GREEN
            case DiffType.REMOVED:
                return Font.RED
            case DiffType.CHANGED | DiffType.TYPECHANGED:
                return Font.YELLOW
            case DiffType.UNCHANGED:
                return Font.ENDC

        raise Exception("Unknown diff type")

    def prefix(self) -> str:
        """The prefix to use when printing the start of line."""
        return f"{self.color()}{self.value} "


def enum_name(value: Enum) -> str:
    """Return the name of the enum."""
    return value.name


def enum_value(value: Enum) -> str:
    """Return the value of the enum."""
    return value.value


def enum_full(value: Enum) -> str:
    """Return full enum name including class."""
    return f"{value.__class__.__name__}.{value.name}"


def spaces(indent: int) -> str:
    """Return a string with the correct number of indented spaces."""
    return " " * 2 * indent


# ruff: noqa: PLR0913,PLR0915
def diff(
    old_object: Any,
    new_object: Any,
    enum_formatter: Callable[[Enum], str] = enum_full,
    changes_only: bool = False,
    object_name: str | None = None,
    no_color: bool = os.environ.get("NO_COLOR") is not None,
) -> str:
    """
    Diff two objects.

    Will compute the diff between two passed objects and return a string
    representing the diff.

    :param old_object: The original object
    :param new_object: The new or latest version of the object
    :param enum_formatter: A function on how to format enum values
    :param changes_only: Only return potentially changed lines, omitting
        everything unchanged
    :param object_name: Set a custom prefix for the original object.
    :param no_color: Don't use colors
    """
    deep_diff = deepdiff.DeepDiff(old_object, new_object)

    output = io.StringIO()
    _build_diff(
        old_object,
        new_object,
        indent=0,
        path="root",
        deep_diff=deep_diff,
        enum_formatter=enum_formatter,
        output=output,
        object_name=object_name,
    )

    full_diff = output.getvalue().rstrip("\n")

    if changes_only:
        full_diff = "\n".join(
            [x for x in full_diff.splitlines() if not x.startswith(Font.ENDC)]
        )

    if no_color:
        full_diff = ansi_escape.sub("", full_diff)

    return full_diff


def _build_diff(
    old_object: Any,
    new_object: Any,
    *,
    deep_diff: deepdiff.DeepDiff,
    enum_formatter: Callable[[Enum], str],
    indent: int,
    path: str,
    list_context: bool = False,
    object_name: str | None = None,
    output: TextIO = sys.stdout,
    context: DiffType | None = None,
) -> None:
    context = context or DiffType.from_types(old_object, new_object)

    object_type = Format(
        identifier=object_name, old_object=old_object, new_object=new_object
    )

    if (
        not isinstance(new_object, dict)
        and not isinstance(new_object, Enum)
        and hasattr(new_object, "__dict__")
    ):
        new_object = new_object.__dict__

    if (
        not isinstance(old_object, dict)
        and not isinstance(old_object, Enum)
        and hasattr(old_object, "__dict__")
    ):
        old_object = old_object.__dict__

    if isinstance(new_object, dict) or isinstance(old_object, dict):
        if list_context:
            prefix = f"{context.prefix()}{spaces(indent)}"
        elif path == "root":
            prefix = context.prefix()
        else:
            prefix = context.color()

        print(f"{prefix}{object_type.prefix()}", file=output)

        # Iterate over all keys in the new object, they might be unchanged,
        # changed or added.
        if isinstance(new_object, dict):
            for k, v in new_object.items():
                path_key = f"'{k}'" if isinstance(k, str) else k

                if list_context:
                    key_context = context

                elif old_object is None or (
                    isinstance(old_object, dict) and k not in old_object
                ):
                    key_context = DiffType.ADDED

                elif old_object == new_object or (
                    isinstance(old_object, dict) and old_object.get(k) == v
                ):
                    key_context = DiffType.UNCHANGED

                elif (
                    isinstance(old_object, dict)
                    and old_object.get(k) is not None
                    and v is not None
                    and type(old_object.get(k)) != type(v)
                ):
                    key_context = DiffType.TYPECHANGED

                else:
                    key_context = DiffType.CHANGED

                print(
                    f"{key_context.prefix()}{spaces(indent + 1)}{k}{Font.ENDC} = ",
                    end="",
                    file=output,
                )

                _build_diff(
                    old_object.get(k) if isinstance(old_object, dict) else None,
                    v,
                    indent=indent + 1,
                    path=f"{path}[{path_key}]"
                    if object_type._object_type == "dict"
                    else f"{path}.{k}",
                    deep_diff=deep_diff,
                    enum_formatter=enum_formatter,
                    output=output,
                    context=key_context,
                )

        # Iterate over all keys in the old object that we didn't already pass.
        # This means all the keys that are no longer a part of the new object.
        if isinstance(old_object, dict):
            for k, v in old_object.items():
                if new_object is not None and k in new_object:
                    continue

                path_key = f"'{k}'" if isinstance(k, str) else k
                key_context = DiffType.REMOVED

                print(
                    f"{key_context.prefix()}{spaces(indent + 1)}{k}{Font.ENDC} = ",
                    end="",
                    file=output,
                )

                _build_diff(
                    v,
                    None,
                    indent=indent + 1,
                    path=f"{path}[{path_key}]"
                    if object_type._object_type == "dict"
                    else f"{path}.{k}",
                    deep_diff=deep_diff,
                    enum_formatter=enum_formatter,
                    output=output,
                    context=key_context,
                )

        print(
            f"{context.prefix()}{spaces(indent)}{object_type.suffix()}{Font.ENDC}",
            file=output,
        )

    elif isinstance(new_object, list) or isinstance(old_object, list):
        prefix = context.prefix() if path == "root" else context.color()
        print(f"{prefix}[", file=output)

        new_object = new_object or []
        old_object = old_object or []
        longest_object = old_object if len(old_object) > len(new_object) else new_object
        iterable_added = deep_diff.get("iterable_item_added", {})
        iterable_removed = deep_diff.get("iterable_item_removed", {})
        values_changed = deep_diff.get("values_changed", {})
        type_changed = deep_diff.get("type_changes", {})

        for i, o in enumerate(longest_object):
            i_path = f"{path}[{i}]"

            if i_path in iterable_added:
                i_context = DiffType.ADDED
                (old, new) = (None, iterable_added.get(i_path))

                # Insert a placeholder `None` in the old list where the new one
                # is added to get the proper offset later in the iteration where
                # we compare objects.
                old_object.insert(i, None)

            elif i_path in iterable_removed:
                i_context = DiffType.REMOVED
                (old, new) = (iterable_removed.get(i_path), None)

                # Insert a placeholder `None` in the new list where the old one
                # is removed to get the proper offset later in the iteration
                # where we compare objects.
                new_object.insert(i, None)

            elif i_path in values_changed:
                i_context = DiffType.CHANGED
                old = values_changed.get(i_path, {}).get("old_value")
                new = values_changed.get(i_path, {}).get("new_value")

            elif i_path in type_changed:
                i_context = DiffType.TYPECHANGED
                old = type_changed.get(i_path, {}).get("old_value")
                new = type_changed.get(i_path, {}).get("new_value")

            # Enums are a bit special since they're obejct, they will end up as
            # with a `.name` and `.value` suffix in the deep diff.
            # If an enum has changed it will exist in both the old and new
            # object so we should be safe to grab them.
            elif isinstance(o, Enum) and f"{i_path}.name" in values_changed:
                (old, new) = (old_object[i], new_object[i])
                i_context = DiffType.UNCHANGED if old == new else DiffType.CHANGED

            # If nothing else matches we must be the same value even though we
            # might be pushed regarding our indexes. If we're in add or delete
            # context that means that the whole list is removed and if so we
            # should keep the context, otherwise this row should be considered
            # unchanged.
            else:
                old = old_object[i] if i < len(old_object) else None
                new = new_object[i] if i < len(new_object) else None

                if context in [DiffType.ADDED, DiffType.REMOVED]:
                    i_context = context
                else:
                    i_context = DiffType.UNCHANGED

            _build_diff(
                old,
                new,
                indent=indent + 1,
                path=i_path,
                list_context=True,
                deep_diff=deep_diff,
                enum_formatter=enum_formatter,
                output=output,
                context=i_context,
            )

        print(f"{context.prefix()}{spaces(indent)}]{Font.ENDC}", file=output)

    else:
        prefix = context.prefix() if list_context else context.color()
        indent = indent if list_context else 0

        if context == DiffType.CHANGED:
            old_value = _maybe_enum(old_object, enum_formatter)
            new_value = _maybe_enum(new_object, enum_formatter)
            obj = f"{Font.RED}{old_value}{Font.ENDC} => {Font.GREEN}{new_value}"
        elif context == DiffType.REMOVED:
            obj = _maybe_enum(old_object, enum_formatter)
        else:
            obj = _maybe_enum(new_object, enum_formatter)

        maybe_spaces = (
            "" if old_object == new_object and not list_context else spaces(indent)
        )
        print(f"{prefix}{maybe_spaces}{obj}{Font.ENDC}", file=output)


def _maybe_enum(e, enum_formatter: Callable[[Enum], str]):
    return enum_formatter(e) if isinstance(e, Enum) else e
