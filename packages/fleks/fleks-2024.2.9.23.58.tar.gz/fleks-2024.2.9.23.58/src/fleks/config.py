""" fleks.config
"""

import pydash

from fleks import models
from fleks.util import typing


class Config(models.BaseModel):
    """ """

    config_key: typing.ClassVar[str] = None
    # debug = False
    # parent = None
    # priority = 100
    # override_from_base = True

    def __init__(self, **this_config) -> None:
        """ """
        kls_defaults = getattr(self.__class__, "defaults", {})
        super().__init__(**{**kls_defaults, **this_config})
        # conflicts = []
        # for pname in self.__class__.__properties__:
        #     if pname in called_defaults or pname in kls_defaults:
        #         conflicts.append(pname)
        #         continue
        #     else:
        #         self[pname] = getattr(self, pname)
        # self.resolve_conflicts(conflicts)

    def __getitem__(
        self,
        key,
    ):
        if isinstance(key, (slice,)):
            start, stop, step = key.start, key.stop, key.step
            raise Exception("niy")
        tmp = self.dict(
            # exclude_unset=True,
            by_alias=True
        )
        try:
            return tmp[key]
        except (KeyError, TypeError) as exc:
            return pydash.get(tmp, key)

    def __repr__(self):
        return f"<{self.__class__.__name__}['{self.__class__.config_key}']>"

    # def as_dict(self, **kwargs):
    #     kwargs.update(
    #         # exclude_unset=True,
    #         by_alias=True
    #     )
    #     return self.dict(**kwargs)

    # @typing.classproperty
    # def logger(kls):
    #     """
    #
    #     :param kls:
    #
    #     """
    #     return lme.get_logger(f"{kls._logging_name}")

    # def resolve_conflicts(self, conflicts: typing.List) -> None:
    #     """
    #
    #     :param conflicts: typing.List:
    #     :param conflicts: typing.List:
    #
    #     """
    #     conflicts and LOGGER.info(
    #         f"'{self.config_key}' is resolving {len(conflicts)} conflicts.."
    #     )
    #
    #     record = collections.defaultdict(list)
    #     for pname in conflicts:
    #         prop = getattr(self.__class__, pname)
    #         strategy = tags.get(prop, {}).get("conflict_strategy", "user_wins")
    #         if strategy == "user_wins":
    #             record[strategy].append(f"{self.config_key}.{pname}")
    #         elif strategy == "override":
    #             val = getattr(self, pname)
    #             self[pname] = val
    #             record[strategy] += [pname]
    #         else:
    #             LOGGER.critical(f"unsupported conflict-strategy! {strategy}")
    #             raise SystemExit(1)
    #
    #     overrides = record["override"]
    #     if overrides:
    #         pass
    #
    #     user_wins = record["user_wins"]
    #     if user_wins:
    #         msg = "these keys have defaults, but user-provided config wins: "
    #         tmp = text.to_json(user_wins)
    #         self.logger.info(f"{msg}\n  {tmp}")
    # def __iter__(self):
    #     return iter(self.as_dict())

    # def __rich__(self):
    #     return self.as_dict()
