"""
#
# JSON Schema utilities
#
# Copyright(c) 2019, Carium, Inc. All rights reserved.
#
"""
import inspect
import json
import typing as t
from collections import OrderedDict
from typing import Any, Dict, Iterable, List, Optional, Set, Union

from cariutils.typing import JsonDict


#
# DSL for simpler json schema definitions
#
class Definition:
    """A re-usable JSON schema definition"""

    schema = {}

    @classmethod
    def get_all(cls) -> Dict[str, t.Type["Definition"]]:
        """
        Return a mapping of all definition names to their definition.
        There is not really anything to inherit, so we don't worry about nested subclasses.
        """
        d = {}
        for sub in cls.__subclasses__():
            if sub.__name__ in d:
                existing = d[sub.__name__]
                prev = f"{existing.__module__}.{existing.__name__}"
                dupe = f"{sub.__module__}.{sub.__name__}"
                raise Exception(f'Duplicate Definition "{dupe}" previously defined here: "{prev}"')
            d[sub.__name__] = sub
        return OrderedDict((key, d[key]) for key in sorted(d.keys()))


def AnyOf(*args: Union[JsonDict, t.Type[Definition]]) -> JsonDict:
    return {"anyOf": [*args]}


def AllOf(*args: Union[JsonDict, t.Type[Definition]]) -> JsonDict:
    return {"allOf": [*args]}


def OneOf(*args: Union[JsonDict, t.Type[Definition]]) -> JsonDict:
    return {"oneOf": [*args]}


def Not(schema: Union[JsonDict, t.Type[Definition]]) -> JsonDict:
    return {"not": schema}


def Type(type: str, description: str = "", title: str = "") -> JsonDict:
    d = dict(type=type)

    if description:
        d["description"] = description

    if title:
        d["title"] = title

    return d


def Array(
    type: Union[JsonDict, t.Type[Definition], List[Union[JsonDict, t.Type[Definition]]]],
    description: str = "",
    title: str = "",
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    default: Optional[List[Any]] = None,
    additional: Optional[bool] = None,
    deprecated: bool = False,
) -> JsonDict:
    """Construct an 'array' type json schema definition with the given type"""
    d = Type(type="array", description=description, title=title)
    d["items"] = type

    if min_items is not None:
        if min_items < 0:
            raise TypeError("min_items must be non-negative")
        d["minItems"] = min_items

    if max_items is not None:
        if max_items < 0:
            raise TypeError("max_items must be non-negative")
        d["maxItems"] = max_items

    if default is not None:
        d["default"] = default

    if additional is not None:
        d["additionalItems"] = additional

    if deprecated:
        d["deprecated"] = deprecated

    return d


def Boolean(
    default: Optional[bool] = None,
    description: str = "",
    title: str = "",
    deprecated: bool = False,
) -> JsonDict:
    """Construct a 'boolean' type json schema definition"""

    d = Type(type="boolean", description=description, title=title)

    if default is not None:
        d["default"] = default

    if deprecated:
        d["deprecated"] = deprecated

    return d


def Const(value: Union[bool, float, int, str]) -> JsonDict:
    # NOTE: Not actually using JSON schema "const" since it isn't supported by Swagger. "const" is just syntactic
    # sugar for an "enum" anyways, so we'll allow using Const() while actually generating an enum under the hood.
    return {"enum": [value]}


def File(description: str = "", max_size: Optional[int] = None, title: str = "") -> JsonDict:
    """Construct a 'file' type json schema definition"""

    d = Type(type="file", description=description, title=title)

    if max_size is not None:
        if max_size < 1:
            raise TypeError("max_size must be at least one")

        d["maxsize"] = max_size

    return d


def Null(description: str = "", title: str = "") -> JsonDict:
    """Construct a 'null' type json schema definition"""

    return Type(type="null", description=description, title=title)


def Number(
    default: Optional[float] = None,
    exclusive_maximum: Optional[float] = None,
    exclusive_minimum: Optional[float] = None,
    maximum: Optional[float] = None,
    minimum: Optional[float] = None,
    multiple_of: Optional[int] = None,
    description: str = "",
    title: str = "",
    deprecated: bool = False,
    enum: Optional[Iterable[int | float]] = None,
) -> JsonDict:
    """Construct a 'number' type json schema definition with the given options"""

    d = Type(type="number", description=description, title=title)
    if default is not None:
        d["default"] = default

    if exclusive_maximum is not None:
        d["exclusiveMaximum"] = exclusive_maximum

    if exclusive_minimum is not None:
        d["exclusiveMinimum"] = exclusive_minimum

    if maximum is not None:
        d["maximum"] = maximum

    if minimum is not None:
        d["minimum"] = minimum

        if maximum is not None and maximum < minimum:
            raise TypeError("maximum must be greater than or equal to minimum")

    if multiple_of is not None:
        d["multipleOf"] = multiple_of

    if deprecated:
        d["deprecated"] = deprecated

    if enum is not None:
        d["enum"] = sorted(set(enum))

    return d


def Integer(
    default: Optional[int] = None,
    exclusive_maximum: Optional[int] = None,
    exclusive_minimum: Optional[int] = None,
    maximum: Optional[int] = None,
    minimum: Optional[int] = None,
    multiple_of: Optional[int] = None,
    description: str = "",
    title: str = "",
    deprecated: bool = False,
    enum: Optional[Iterable[int]] = None,
) -> JsonDict:
    """Construct an 'integer' type json schema definition with the given options"""
    d = Number(
        default=default,
        exclusive_maximum=exclusive_maximum,
        exclusive_minimum=exclusive_minimum,
        maximum=maximum,
        minimum=minimum,
        multiple_of=multiple_of,
        description=description,
        title=title,
        enum=enum,
    )

    d["type"] = "integer"

    if deprecated:
        d["deprecated"] = deprecated

    return d


def Object(
    properties: JsonDict,
    additional: Union[bool, JsonDict, None, t.Type[Definition]] = None,
    extends: Optional[dict] = None,
    required: Optional[Union[str, Iterable[str]]] = None,
    description: str = "",
    title: str = "",
    optional: Optional[Iterable[str]] = None,
    pattern_properties: Optional[JsonDict] = None,
    deprecated: bool = False,
) -> JsonDict:
    """Construct an 'object' type json schema definition with the given properties"""
    if extends is None:
        extends = {}

    if required and optional:
        raise TypeError("You may only set required or optional, not both")

    if required == "All":
        required = list(properties.keys())
    else:
        if required is not None:
            required = list(required)  # Force required to be a list

    additional = additional if additional is not None else extends.get("additionalProperties", False)

    if optional:
        optional = set(optional)
        required = extends.get("required", []) + [k for k in properties.keys() if k not in optional]
    else:
        required = extends.get("required", []) + (required or [])

    d = Type(type="object", description=description, title=title)
    d["additionalProperties"] = additional
    d["properties"] = properties

    if "properties" in extends:
        d["properties"] = {**extends["properties"], **properties}

    if len(required):
        d["required"] = sorted(set(required))

    if pattern_properties and "patternProperties" in extends:
        d["patternProperties"] = {**extends["patternProperties"], **pattern_properties}
    elif pattern_properties:
        d["patternProperties"] = pattern_properties

    if "patternProperties" not in d:
        for req in d.get("required", []):
            if req not in d["properties"]:
                props = json.dumps(sorted(d["properties"].keys()))
                raise ValueError(f'You cannot require "{req}" as it is not one of {props}')
        for each in optional or set():
            if each not in d["properties"]:
                props = json.dumps(sorted(d["properties"].keys()))
                raise ValueError(f'You cannot have optional "{each}" as it is not one of {props}')

    if deprecated:
        d["deprecated"] = deprecated

    return d


def Ref(ref: str) -> JsonDict:
    """Construct a reference to another schema defined elsewhere"""
    return {"$ref": ref}


# Examples by format to use in swagger-ui
STRING_EXAMPLES = {"uuid": "11111111-1111-1111-1111-111111111111"}


def String(
    format: Optional[str] = None,
    default: Optional[str] = None,
    example: Optional[str] = None,
    enum: Optional[Iterable[str]] = None,
    description: str = "",
    title: str = "",
    pattern: Optional[str] = None,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    format_minimum: Optional[str] = None,
    deprecated: bool = False,
) -> JsonDict:
    """Construct a 'string' type json schema definition with the given options"""

    d = Type(type="string", description=description, title=title)
    if example is not None:
        d["example"] = example

    if format is not None:
        d["format"] = format
        if example is None and format in STRING_EXAMPLES:
            d["example"] = STRING_EXAMPLES[format]

    if enum is not None:
        d["enum"] = sorted(set(enum))

    if default is not None:
        d["default"] = default
        if ("enum" in d) and (default not in d["enum"]):
            raise ValueError(f"Invalid default {default}")

    if pattern is not None:
        d["pattern"] = pattern

    if max_length is not None:
        d["maxLength"] = max_length

    if min_length is not None:
        d["minLength"] = min_length

    if format_minimum is not None:
        d["formatMinimum"] = format_minimum

    if deprecated:
        d["deprecated"] = deprecated

    return d


class DefinitionCollector:
    """Collects list of encountered Definition classes during definition expansion"""

    def __init__(self):
        self.definitions: Set[t.Type[Definition]] = set()


def expand_defs(
    schema: Union[JsonDict, t.Type[Definition], Any],
    root: str = "definitions",
    full: bool = False,
    collector: Optional[DefinitionCollector] = None,
) -> JsonDict:
    """
    Take a schema definition that might include Definition references and expand them.
    if full is set, expand them into their full schema
    else expand them into references.
    """

    if isinstance(schema, dict):
        expanded = {}

        for k, v in schema.items():
            if isinstance(v, dict):
                expanded[k] = expand_defs(v, root=root, full=full, collector=collector)
            elif isinstance(v, list):
                expanded[k] = [expand_defs(item, root=root, full=full, collector=collector) for item in v]
            elif inspect.isclass(v) and issubclass(v, Definition):
                expanded[k] = expand_defs(v, root=root, full=full, collector=collector)
            else:
                expanded[k] = v

        return expanded
    if inspect.isclass(schema) and issubclass(schema, Definition):
        if full:
            return expand_defs(schema.schema, root=root, full=full, collector=collector)
        if collector is not None:
            already_seen = schema in collector.definitions
            collector.definitions.add(schema)
            if not already_seen:  # explore Definition's components, in case referencing other Definitions
                expand_defs(schema.schema, root=root, full=full, collector=collector)  # take a reference
        return Ref(f"#/{root}/{schema.__name__}")
    # else Raw value (for enum, etc)
    return schema


def expand_refs(schema: JsonDict, definitions: JsonDict) -> JsonDict:
    """Take a schema definition that might include $ref references and expand them."""
    if isinstance(schema, dict):
        expanded = {}

        for k, v in schema.items():
            if k == "$ref":
                ref = definitions
                for part in v.split("/")[1:]:
                    ref = ref[part]
                expanded.update(expand_refs(schema=ref, definitions=definitions))
            elif isinstance(v, dict):
                expanded[k] = expand_refs(schema=v, definitions=definitions)
            elif isinstance(v, list):
                expanded[k] = [expand_refs(schema=item, definitions=definitions) for item in v]
            else:
                expanded[k] = v

        return expanded
    # else Raw value (for enum, etc)
    return schema
