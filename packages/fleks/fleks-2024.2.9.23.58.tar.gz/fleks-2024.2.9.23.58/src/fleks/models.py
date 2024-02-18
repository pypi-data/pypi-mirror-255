""" fleks.models
"""

import json
import pathlib

from fleks.util import lme, typing

LOGGER = lme.get_logger(__name__)


class JSONEncoder(json.JSONEncoder):
    """ """

    encoders = {}

    @classmethod
    def register_encoder(kls, type=None, fxn=None):
        """ """
        kls.encoders[type] = fxn

    def encode(self, obj):
        """ """
        result = None
        if callable(getattr(obj, "json", None)):
            return obj.json()
        for _type, fxn in self.encoders.items():
            if isinstance(obj, (_type,)):
                LOGGER.warning(f"{obj} matches {_type}, using {fxn}")
                return fxn(obj)
        return super().encode(obj)

    def default(self, obj):
        """ """
        # FIXME: use multimethod
        if callable(getattr(obj, "dict", None)):
            return obj.dict()
        if callable(getattr(obj, "as_dict", None)):
            return obj.as_dict()
        else:
            enc = self.encoders.get(type(obj), str)
            return enc(obj)


def to_json(obj, cls=None, minified=False, indent: int = 2) -> str:
    """
    custom version of `json.dumps` to always use custom JSONEncoder
    """
    indent = None if minified else indent
    cls = cls if cls is not None else JSONEncoder
    return json.dumps(obj, indent=indent, cls=cls)


JSONEncoder.register_encoder(type=map, fxn=list)
JSONEncoder.register_encoder(type=pathlib.Path, fxn=lambda v: str(v))
JSONEncoder.register_encoder(type=pathlib.PosixPath, fxn=lambda v: str(v))


class BaseModel(typing.BaseModel):
    """
    Extends pydantic's BaseModel with better support for
    things like serialization & dynamic values from properties
    """

    class Config:
        arbitrary_types_allowed = True
        # https://github.com/pydantic/pydantic/discussions/5159
        frozen = True
        include: typing.Set[str] = set()
        exclude: typing.Set[str] = set()

    def json(self, **kwargs):
        """Overrides pydantic for better serialization"""
        return to_json(self.dict(**kwargs))

    def items(self):
        """dictionary compatability"""
        return self.dict().items()

    @classmethod
    def get_properties(cls):
        return [
            prop
            for prop in dir(cls)
            if isinstance(getattr(cls, prop), property)
            and prop not in ("__values__", "fields")
        ]

    def _dict(
        self,
        *,
        include=None,
        exclude=None,
        by_alias: bool = True,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ):
        """ """
        # -> "DictStrAny":
        # Include and exclude properties
        include = include or set()
        include = include.union(getattr(self.Config, "include", set()))
        if len(include) == 0:
            include = None

        exclude = exclude or set()
        exclude = exclude.union(getattr(self.Config, "exclude", set()))
        if len(exclude) == 0:
            exclude = None
        attribs = super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
        props = self.get_properties()

        if include:
            props = [prop for prop in props if prop in include]
        if exclude:
            props = [prop for prop in props if prop not in exclude]

        # Update the attribute dict with the properties
        if props:
            attribs.update({prop: getattr(self, prop) for prop in props})
        for key, val in attribs.items():
            if isinstance(val, (BaseModel,)):
                attribs[key] = val.dict(
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    skip_defaults=skip_defaults,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                )
        return attribs

    def dict(self, *args, **kwargs):
        """Overrides pydantic for better serialization"""
        return self._dict(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__}[..]>"

    __str__ = __repr__
