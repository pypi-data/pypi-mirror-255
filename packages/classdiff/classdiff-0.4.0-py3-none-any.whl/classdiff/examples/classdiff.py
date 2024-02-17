from dataclasses import dataclass
from enum import Enum

import classdiff


@dataclass
class OtherClass:
    name: str


@dataclass
class SomeResource:
    dangerous: bool
    name: str
    not_changed: OtherClass
    other: OtherClass
    price: float
    quantity: int


class E(Enum):
    VariantA = "A"
    VariantB = "B"
    VariantC = "C"


def main():
    added_removed_changed()
    changed_keys()
    missing_keys()
    with_dict()
    with_dataclasses()
    enum()
    lists()


def lists() -> None:
    @dataclass
    class First:
        name: str
        age: int

    @dataclass
    class Second:
        name: str
        data: dict[str, str] | None = None

    for a, b in [
        ([1, 2, 3], [1, 2]),
        ([1, 3], [1, 2, 2, 2, 3]),
        ([2, 3], [1, 2, 3]),
        ([1, 2], [1, 2, 3]),
        ([1, 4, 3], [1, 2, 3]),
        ([], [1, 2, 3]),
        (None, [1, 2, 3]),
        ([1, 2, 3], []),
        ([1, 2, 3], None),
        ([E.VariantA, E.VariantB, E.VariantB], [E.VariantA, E.VariantA, E.VariantB]),
        ([E.VariantA], [E.VariantA, E.VariantB]),
        ([E.VariantA, E.VariantB], [E.VariantA]),
        ([E.VariantA, E.VariantC], [E.VariantA, E.VariantB, E.VariantC]),
        (None, [Second(name="a", data={"one": "1"})]),
        (
            [Second(name="a", data={"one": "1"})],
            [Second(name="a", data={"one": "1", "two": "2"})],
        ),
        ([Second(name="a", data={"one": "1"})], [Second(name="a", data={"one": "!1"})]),
        ([First(name="a", age=3)], [Second(name="a")]),
        ({"a": First(name="a", age=3)}, {"a": Second(name="a")}),
    ]:
        print(classdiff.diff(a, b))
        print("-" * 40)


def added_removed_changed() -> None:
    a1 = {
        "parent": {
            "unchanged": "unchanged",
            "changed": 2,
            "changed_list": [4, 5, 6],
            "changed_dict": {
                "removed": "removed",
                "unchanged": "unchanged",
                "changed": "b",
            },
            "removed": "removed",
            "removed_list": [1, 2, 3],
            "removed_dict": {
                "second": 2,
            },
        }
    }
    a2 = {
        "parent": {
            "unchanged": "unchanged",
            "changed": 1,
            "changed_list": [1, 2, 3],
            "changed_dict": {
                "added": "added",
                "unchanged": "unchanged",
                "changed": "a",
            },
            "added": "added",
            "added_list": [1, 2, 3],
            "added_dict": {
                "first": 1,
            },
        }
    }

    print(classdiff.diff(a1, a2))
    print("-" * 40)


def enum() -> None:
    from enum import Enum

    class YesOrNo(Enum):
        YES = "y"
        NO = "n"

    @dataclass
    class A:
        a: str
        v: YesOrNo

    a1 = A(a="a1", v=YesOrNo.YES)
    a2 = A(a="a2", v=YesOrNo.NO)

    for fn in [classdiff.enum_name, classdiff.enum_value, classdiff.enum_full]:
        print(classdiff.diff(a1, a2, enum_formatter=fn))
        print("-" * 40)


def changed_keys() -> None:
    @dataclass
    class A:
        a: str

    @dataclass
    class B:
        b: str

    a = {"unchanged": 1, "type_change": {"unchanged": 1, "a_or_b": B(b="b")}}
    b = {"unchanged": 1, "type_change": {"unchanged": 1, "a_or_b": A(a="a")}}

    print(classdiff.diff(a, b))
    print("-" * 40)


def missing_keys() -> None:
    a = {"foo": {"x": 1, "biz": {"a": "biz-a", "b": "biz-b"}}}
    b = {"foo": {"x": 1, "baz": {"a": "baz-a", "b": "baz-b"}}}

    print(classdiff.diff(a, b))
    print("-" * 40)


def with_dict() -> None:
    class Bar:
        def __init__(self, b):
            self.a = "a"
            self.b = b

    class Foo:
        def __init__(self, n, b):
            self.a = 42
            self.b = {"cat": "rat", "b": {"f": {"cat": n, "hat": True}}}
            self.c = Bar(b)

    print(classdiff.diff(Foo(43, "b"), Foo(44, "c")))
    print("-" * 40)


def with_dataclasses() -> None:
    old_object = SomeResource(
        name="my-data",
        price=3.3,
        quantity=4,
        dangerous=False,
        other=OtherClass(name="OB"),
        not_changed=OtherClass(name="Same"),
    )

    new_object = SomeResource(
        name="my-data",
        price=2.3,
        quantity=4,
        dangerous=True,
        other=OtherClass(name="OA"),
        not_changed=OtherClass(name="Same"),
    )

    print(classdiff.diff(None, new_object))
    print("-" * 40)

    print(classdiff.diff(old_object, new_object))
    print("-" * 40)

    print(classdiff.diff(old_object, None))
    print("-" * 40)
