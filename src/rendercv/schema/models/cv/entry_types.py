import dataclasses
import difflib
import functools
import re
import types
from collections.abc import Callable, Mapping
from datetime import date as Date
from typing import Annotated, Any, Literal, cast

import phonenumbers
import pydantic
import pydantic_core
import pydantic_extra_types.phone_numbers as pydantic_phone_numbers

from rendercv.exception import RenderCVUserError

from ...yaml_reader import TypstString
from ..base import BaseModelWithoutExtraKeys
from ..validation_context import ValidationContext

type FieldKind = Literal[
    "markdown",
    "text",
    "date",
    "url",
    "email",
    "phone",
    "number",
    "bool",
    "choice",
    "list",
    "bullets",
    "entries",
]
available_field_kinds: tuple[str, ...] = FieldKind.__value__.__args__

# The key an entry may use to name its type explicitly. No field may use it.
entry_type_key = "type"


@dataclasses.dataclass(frozen=True, kw_only=True)
class FieldDeclaration:
    """One field of an entry type, as declared in Typst with `field(...)`.

    Why:
        Entry types are defined in Typst so that anyone can create them, but the
        YAML is validated in Python. Declarations are the bridge: RenderCV reads
        them from the Typst files and builds validation from them.
    """

    kind: FieldKind
    optional: bool = False
    doc: str | None = None
    of: FieldKind | None = None
    choices: tuple[str, ...] | None = None
    pattern: str | None = None
    allow_text: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class EntryTypeDeclaration:
    """An entry type, as declared in Typst with `entry-type(...)`.

    Why:
        Validation needs each entry type's fields to check the YAML and to
        detect which type an entry is when it doesn't say so explicitly.
    """

    name: str
    doc: str | None
    fields: Mapping[str, FieldDeclaration]

    @functools.cached_property
    def required_fields(self) -> frozenset[str]:
        """Names of the fields an entry of this type must have."""
        return frozenset(
            name for name, field in self.fields.items() if not field.optional
        )


def parse_entry_type_declarations(
    declarations: Mapping[str, Any],
) -> dict[str, EntryTypeDeclaration]:
    """Build entry type declarations from the JSON Typst reports.

    Why:
        RenderCV queries a Typst module for its entry types and gets plain JSON
        back. This checks it once, so everything after can rely on well-formed
        declarations.

    Args:
        declarations: Entry type names mapped to `{doc, fields}` as produced by
            the Typst package's `declarations` function.

    Returns:
        Entry type names mapped to declarations, in declaration order.

    Raises:
        RenderCVUserError: If a declaration uses an unknown field kind or a
            reserved field name.
    """
    entry_types: dict[str, EntryTypeDeclaration] = {}
    for name, declaration in declarations.items():
        fields: dict[str, FieldDeclaration] = {}
        for field_name, field in declaration["fields"].items():
            if field_name == entry_type_key:
                message = (
                    f"The entry type `{name}` declares a field named"
                    f" `{entry_type_key}`, but that name is reserved for choosing"
                    " an entry's type in the YAML."
                )
                raise RenderCVUserError(message)
            for kind in (field["kind"], field.get("of")):
                if kind is not None and kind not in available_field_kinds:
                    message = (
                        f"The field `{field_name}` of the entry type `{name}` has"
                        f" the unknown kind `{kind}`. Available kinds:"
                        f" {', '.join(available_field_kinds)}."
                    )
                    raise RenderCVUserError(message)
            choices = field.get("choices")
            fields[field_name] = FieldDeclaration(
                kind=field["kind"],
                optional=field.get("optional", False),
                doc=field.get("doc"),
                of=field.get("of"),
                choices=tuple(choices) if choices is not None else None,
                pattern=field.get("pattern"),
                allow_text=field.get("allow-text", False),
            )
        entry_types[name] = EntryTypeDeclaration(
            name=name, doc=declaration.get("doc"), fields=fields
        )
    return entry_types


@dataclasses.dataclass(frozen=True, kw_only=True)
class DateValue:
    """A validated value of a `date` field.

    Why:
        Dates are written as YYYY-MM-DD, YYYY-MM, YYYY, "present", or free text.
        Keeping which of these it was lets Typst write the date in the CV's
        language without parsing it again.
    """

    year: int | None = None
    month: int | None = None
    day: int | None = None
    present: bool = False
    text: str | None = None

    def to_date(self, current_date: Date) -> Date | None:
        """Return the date as a Python date, or None for free text.

        Args:
            current_date: The date "present" stands for.

        Returns:
            The date, with missing month and day as 1.
        """
        if self.present:
            return current_date
        if self.year is None:
            return None
        return Date(self.year, self.month or 1, self.day or 1)


@dataclasses.dataclass(frozen=True, kw_only=True)
class PhoneValue:
    """A validated value of a `phone` field, in every format a design may show."""

    e164: str
    international: str
    national: str
    uri: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Bullet:
    """One bullet point of a `bullets` field, with its nested bullets."""

    body: str
    children: tuple["Bullet", ...] = ()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Entry:
    """A validated entry: its type and its field values.

    Why:
        Entries are not Python classes anymore; their types are declared in
        Typst. After validation, an entry is just its type's name and its
        values, ready to be sent to Typst.
    """

    type_name: str
    values: Mapping[str, Any]


date_pattern = re.compile(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?")


def validate_date(value: Any, *, allow_text: bool) -> DateValue:
    """Validate a date: YYYY-MM-DD, YYYY-MM, YYYY, "present", or free text.

    Args:
        value: The date from the YAML.
        allow_text: Whether free text such as "Fall 2023" is accepted.

    Returns:
        The validated date.
    """
    if isinstance(value, bool):
        pass
    elif isinstance(value, int):
        # Years Python's dates can't hold (like 0) fall through to the error:
        if Date.min.year <= value <= Date.max.year:
            return DateValue(year=value)
    elif isinstance(value, Date):
        return DateValue(year=value.year, month=value.month, day=value.day)
    elif isinstance(value, str):
        if value.strip() == "present":
            return DateValue(present=True)
        match = date_pattern.fullmatch(value.strip())
        if match:
            year, month, day = (int(part) if part else None for part in match.groups())
            if year is None:
                raise pydantic_core.PydanticCustomError(
                    "rendercv_date", "This is not a valid date."
                )
            try:
                # Checks 0 too: "2020-00" is not January.
                Date(year, 1 if month is None else month, 1 if day is None else day)
            except ValueError as e:
                raise pydantic_core.PydanticCustomError(
                    "rendercv_date",
                    "This is not a valid date: {reason}.",
                    {"reason": str(e)},
                ) from e
            return DateValue(year=year, month=month, day=day)
        if allow_text and value.strip():
            return DateValue(text=value)
    raise pydantic_core.PydanticCustomError(
        "rendercv_date",
        "This is not a valid date. Use YYYY-MM-DD, YYYY-MM, YYYY, or"
        ' "present"{or_text}.',
        {"or_text": ", or any text like 'Fall 2023'" if allow_text else ""},
    )


def validate_markdown(value: Any) -> str:
    """Validate text: Markdown, or Typst markup if tagged `!typst`.

    Args:
        value: The text from the YAML. Numbers are accepted as text.

    Returns:
        The text; a `TypstString` if it was tagged `!typst`.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, int | float) and not isinstance(value, bool):
        return str(value)
    raise pydantic_core.PydanticCustomError("rendercv_text", "This should be text.")


def split_bullet(text: str) -> Bullet:
    """Split a bullet's text into the bullet and its nested bullets.

    Why:
        Nested bullets are written inside a bullet's text, separated by " - ".
        This is how existing CVs write them, and YAML folds a bullet's indented
        continuation lines into one line, so it's the one convention that
        survives YAML.

    Example:
        ```py
        bullet = split_bullet("Published papers - ICML 2022 - NeurIPS 2022")
        # Bullet(body="Published papers", children=(Bullet(body="ICML 2022"), ...))
        ```

    Args:
        text: The bullet's text.

    Returns:
        The bullet with its nested bullets.
    """
    if isinstance(text, TypstString):
        return Bullet(body=text)
    body, *children = text.split(" - ")
    return Bullet(body=body, children=tuple(Bullet(body=child) for child in children))


def validate_phone(value: Any) -> PhoneValue:
    """Validate a phone number and write it in every format.

    Args:
        value: The phone number from the YAML, with its country code.

    Returns:
        The phone number in E.164, international, national, and URI format.
    """
    number = pydantic.TypeAdapter(pydantic_phone_numbers.PhoneNumber).validate_python(
        str(value)
    )
    parsed = phonenumbers.parse(number, None)
    formats = phonenumbers.PhoneNumberFormat
    return PhoneValue(
        e164=phonenumbers.format_number(parsed, formats.E164),
        international=phonenumbers.format_number(parsed, formats.INTERNATIONAL),
        national=phonenumbers.format_number(parsed, formats.NATIONAL),
        uri=phonenumbers.format_number(parsed, formats.RFC3966),
    )


def validate_url(value: Any) -> str:
    """Validate a URL and return it as written.

    Args:
        value: The URL from the YAML.

    Returns:
        The URL, unchanged.
    """
    pydantic.TypeAdapter(pydantic.HttpUrl).validate_python(value)
    return str(value)


def validate_email(value: Any) -> str:
    """Validate an email address.

    Args:
        value: The email address from the YAML.

    Returns:
        The email address.
    """
    return pydantic.TypeAdapter(pydantic.EmailStr).validate_python(value)


string_schema: dict[str, Any] = {"type": "string"}

type MarkdownText = Annotated[
    str,
    pydantic.PlainValidator(validate_markdown),
    pydantic.WithJsonSchema(string_schema),
]
type PhoneNumber = Annotated[
    PhoneValue,
    pydantic.PlainValidator(validate_phone),
    pydantic.WithJsonSchema(string_schema),
]
type Url = Annotated[
    str,
    pydantic.PlainValidator(validate_url),
    pydantic.WithJsonSchema({"type": "string", "format": "uri"}),
]
date_schema: dict[str, Any] = {
    "anyOf": [
        {"type": "integer"},
        {"type": "string", "pattern": r"^\d{4}(-\d{2}){0,2}$"},
        {"const": "present"},
    ]
}


def kind_annotation(
    field: FieldDeclaration,
    kind: FieldKind,
    entry_type_models: Callable[[], Mapping[str, type[pydantic.BaseModel]]],
) -> Any:
    """Build the pydantic annotation that validates one field kind.

    Args:
        field: The field's declaration.
        kind: The kind to validate: the field's kind, or its item kind.
        entry_type_models: Returns the models of all entry types, for nested
            entries.

    Returns:
        An annotated type with the kind's validator and JSON schema.
    """
    match kind:
        case "markdown":
            return MarkdownText
        case "text":
            if field.pattern:
                return Annotated[str, pydantic.StringConstraints(pattern=field.pattern)]
            return str
        case "date":
            return Annotated[
                DateValue,
                pydantic.PlainValidator(
                    functools.partial(validate_date, allow_text=field.allow_text)
                ),
                pydantic.WithJsonSchema(
                    {"anyOf": [*date_schema["anyOf"], string_schema]}
                    if field.allow_text
                    else date_schema
                ),
            ]
        case "url":
            return Url
        case "email":
            return Annotated[
                str,
                pydantic.PlainValidator(validate_email),
                pydantic.WithJsonSchema({"type": "string", "format": "email"}),
            ]
        case "phone":
            return PhoneNumber
        case "number":
            return int | float
        case "bool":
            return bool
        case "choice":
            return Literal[*(field.choices or ())]  # ty: ignore[invalid-type-form]
        case "list":
            item_kind = field.of or "markdown"
            return types.GenericAlias(
                list, (kind_annotation(field, item_kind, entry_type_models),)
            )
        case "bullets":
            return Annotated[
                list[Bullet],
                pydantic.PlainValidator(
                    lambda value: [
                        split_bullet(validate_markdown(item))
                        for item in validate_list(value)
                    ]
                ),
                pydantic.WithJsonSchema({"type": "array", "items": string_schema}),
            ]
        case "entries":
            return Annotated[
                list[Entry],
                pydantic.PlainValidator(
                    lambda value, info: [
                        validate_nested_entry(item, entry_type_models(), info)
                        for item in validate_list(value)
                    ]
                ),
                pydantic.WithJsonSchema({"type": "array"}),
            ]


def validate_list(value: Any) -> list[Any]:
    """Check that a value is a list.

    Args:
        value: The value from the YAML.

    Returns:
        The list.
    """
    if not isinstance(value, list):
        raise pydantic_core.PydanticCustomError(
            "rendercv_list", "This should be a list of items."
        )
    return value


def build_entry_type_models(
    entry_types: Mapping[str, EntryTypeDeclaration],
) -> dict[str, type[pydantic.BaseModel]]:
    """Build a pydantic model for each entry type from its declaration.

    Why:
        Entry types are declared in Typst and can be anything a user or a
        design defines, so their models are built at runtime. Pydantic then
        validates the YAML with its usual error messages and JSON schema.

    Args:
        entry_types: The entry types.

    Returns:
        Entry type names mapped to pydantic models.
    """
    models: dict[str, type[pydantic.BaseModel]] = {}
    for name, entry_type in entry_types.items():
        field_definitions: dict[str, Any] = {}
        for field_name, field in entry_type.fields.items():
            annotation = kind_annotation(field, field.kind, lambda: models)
            if field.optional:
                field_definitions[field_name] = (
                    annotation | None,
                    pydantic.Field(default=None, description=field.doc),
                )
            else:
                field_definitions[field_name] = (
                    annotation,
                    pydantic.Field(description=field.doc),
                )
        models[name] = pydantic.create_model(
            name,
            __base__=BaseModelWithoutExtraKeys,
            __doc__=entry_type.doc,
            **field_definitions,
        )
    return models


def validate_nested_entry(
    value: Any,
    models: Mapping[str, type[pydantic.BaseModel]],
    info: pydantic.ValidationInfo,
) -> Entry:
    """Validate an entry inside an `entries` field.

    Args:
        value: The nested entry from the YAML.
        models: Entry type names mapped to pydantic models.
        info: Validation info, whose context holds the entry types.

    Returns:
        The validated entry.
    """
    context = cast(dict[str, Any], info.context)["context"]
    entry, errors = validate_entry(value, context.entry_types, models)
    if errors:
        raise pydantic_core.PydanticCustomError(
            "rendercv_nested_entry",
            "This entry has problems: {problems}",
            {"problems": "; ".join(error["msg"] for error in errors)},
        )
    return cast(Entry, entry)


def detect_entry_type(
    value: Mapping[str, Any], entry_types: Mapping[str, EntryTypeDeclaration]
) -> tuple[str | None, list[str]]:
    """Find which entry type an entry is.

    Why:
        CVs don't have to name each entry's type: an entry with `company` and
        `position` is obviously an experience. An entry may still name its type
        with the `type` key when its fields fit several types.

    Args:
        value: The entry from the YAML.
        entry_types: The entry types.

    Returns:
        The detected type's name (or None), and the names of all types the
        entry's fields fit.
    """
    explicit_type = value.get(entry_type_key)
    if explicit_type is not None:
        return (str(explicit_type) if explicit_type in entry_types else None), []
    keys = set(value)
    fits = [
        name
        for name, entry_type in entry_types.items()
        if entry_type.required_fields <= keys and keys <= set(entry_type.fields)
    ]
    if len(fits) == 1:
        return fits[0], fits
    return None, fits


def closest_entry_type(
    value: Mapping[str, Any], entry_types: Mapping[str, EntryTypeDeclaration]
) -> str:
    """Guess which entry type an entry that fits none was meant to be.

    Args:
        value: The entry from the YAML.
        entry_types: The entry types.

    Returns:
        The name of the type sharing the most fields with the entry.
    """
    keys = set(value)

    def closeness(name: str) -> tuple[int, float]:
        entry_type = entry_types[name]
        fields = set(entry_type.fields)
        # A misspelled key counts as the field it's closest to, so `bulet` is a
        # bullet rather than a `normal` entry missing its `name`:
        matches = {
            key: match
            for key in keys - fields
            for match in difflib.get_close_matches(key, fields - keys, n=1)
        }
        meant = set(matches.values())
        score = (
            len(keys & fields)
            + len(meant)
            - len(entry_type.required_fields - keys - meant)
        )
        # Among equals, the closer spelling wins, then the first declared type:
        similarity = sum(
            difflib.SequenceMatcher(None, key, match).ratio()
            for key, match in matches.items()
        )
        return score, similarity

    return max(entry_types, key=closeness)


def validate_entry(
    value: Any,
    entry_types: Mapping[str, EntryTypeDeclaration],
    models: Mapping[str, type[pydantic.BaseModel]],
) -> tuple[Entry | None, list[pydantic_core.ErrorDetails]]:
    """Validate one entry: detect its type, then check its fields.

    Why:
        Errors should say what the user most likely meant. An entry with a
        typo'd field matches no type exactly, so it's checked against the
        closest type, and unknown fields get a "did you mean" suggestion.

    Args:
        value: The entry from the YAML: a mapping, or text for a paragraph.
        entry_types: The entry types.
        models: Entry type names mapped to pydantic models.

    Returns:
        The validated entry (None if invalid) and the errors, with locations
        relative to the entry.
    """
    if isinstance(value, str | int | float) and not isinstance(value, bool):
        if "paragraph" not in entry_types:
            return None, [
                error_details(
                    (),
                    "An entry written as plain text is a paragraph, but there is"
                    " no `paragraph` entry type.",
                    value,
                )
            ]
        value = {"text": value}
    if not isinstance(value, Mapping):
        return None, [
            error_details((), "An entry should be a mapping of fields or text.", value)
        ]
    if not value:
        return None, [error_details((), "This entry is empty.", value)]

    explicit_type = value.get(entry_type_key)
    type_name, fits = detect_entry_type(value, entry_types)
    if explicit_type is not None and type_name is None:
        suggestion = difflib.get_close_matches(str(explicit_type), entry_types, n=1)
        hint = f" Did you mean `{suggestion[0]}`?" if suggestion else ""
        return None, [
            error_details(
                (entry_type_key,),
                f"There is no entry type `{explicit_type}`.{hint}",
                explicit_type,
            )
        ]
    if type_name is None and len(fits) > 1:
        return None, [
            error_details(
                (),
                "This entry's fields fit several entry types ("
                + ", ".join(f"`{name}`" for name in fits)
                + "). Add `type:` to choose one.",
                "...",
            )
        ]
    if type_name is None:
        if not entry_types:
            return None, [
                error_details(
                    (),
                    "There are no entry types to check this entry against."
                    " `entries.typ` should export at least one entry type.",
                    "...",
                )
            ]
        type_name = closest_entry_type(value, entry_types)
        keys = set(value)
        closest_fields = set(entry_types[type_name].fields)
        if not keys & closest_fields and not any(
            difflib.get_close_matches(key, closest_fields, n=1) for key in keys
        ):
            # Blaming the closest type's fields would only mislead:
            available = "; ".join(
                f"`{name}` ("
                + (
                    ", ".join(
                        field
                        for field in entry_type.fields
                        if field in entry_type.required_fields
                    )
                    or "no required fields"
                )
                + ")"
                for name, entry_type in entry_types.items()
            )
            return None, [
                error_details(
                    (),
                    "This entry fits no entry type. The entry types and their"
                    f" required fields: {available}.",
                    "...",
                )
            ]

    fields = {key: item for key, item in value.items() if key != entry_type_key}
    errors: list[pydantic_core.ErrorDetails] = []
    suggested_fields: set[str] = set()
    for key, item in fields.items():
        if key not in entry_types[type_name].fields:
            suggestion = difflib.get_close_matches(
                key,
                [name for name in entry_types[type_name].fields if name not in fields],
                n=1,
            )
            hint = f" Did you mean `{suggestion[0]}`?" if suggestion else ""
            suggested_fields.update(suggestion)
            errors.append(
                error_details(
                    (key,),
                    f"The entry type `{type_name}` has no field `{key}`.{hint}",
                    item,
                )
            )
    try:
        # `entries` fields validate their nested entries with the same types:
        model = models[type_name].model_validate(
            fields,
            context={
                "context": ValidationContext(
                    entry_types=entry_types, entry_type_models=models
                )
            },
        )
    except pydantic.ValidationError as e:
        known_locations = {error["loc"] for error in errors}
        errors.extend(
            error
            for error in e.errors()
            if error["type"] != "extra_forbidden"
            and error["loc"] not in known_locations
            # A misspelled field already explains why its correct name is missing:
            and not (error["type"] == "missing" and error["loc"][0] in suggested_fields)
        )
        return None, errors
    if errors:
        return None, errors

    values = dict(model)
    order_error = check_date_order(values)
    if order_error:
        return None, [order_error]
    return Entry(type_name=type_name, values=values), []


def check_date_order(values: Mapping[str, Any]) -> pydantic_core.ErrorDetails | None:
    """Check that an entry doesn't end before it starts.

    Args:
        values: The entry's validated values.

    Returns:
        An error at `start_date` if it's after `end_date`, otherwise None.
    """
    start = values.get("start_date")
    end = values.get("end_date")
    if not isinstance(start, DateValue) or not isinstance(end, DateValue):
        return None
    today = Date.today()
    start_date = start.to_date(today)
    end_date = end.to_date(today)
    if start_date is None or end_date is None or start_date <= end_date:
        return None
    return error_details(
        ("start_date",),
        "`start_date` cannot be after `end_date`.",
        f"{start_date} > {end_date}",
    )


def error_details(
    location: tuple[str | int, ...], message: str, value: Any
) -> pydantic_core.ErrorDetails:
    """Build an error in the shape pydantic reports errors.

    Args:
        location: Where the error is, relative to the entry.
        message: The error message.
        value: The value that caused the error.

    Returns:
        The error.
    """
    return {"type": "rendercv_entry", "loc": location, "msg": message, "input": value}
