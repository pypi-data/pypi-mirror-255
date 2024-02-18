""" fleks.meta.oop """

import functools
import collections

from fleks.util import lme, typing

from .namespace import namespace

LOGGER = lme.get_logger(__name__)
VLOGGER = lme.get_logger("fleks::validation")

type_spec = collections.namedtuple("type_spec", "name bases namespace")


class ClassMalformed(TypeError):
    """ """


def filter_by_type(namespace=None, kls=None, type=None):
    """ """
    assert type is not None
    namespace = (
        namespace if namespace is not None else {k: getattr(kls, k) for k in dir(kls)}
    )
    return [k for k, v in namespace.items() if isinstance(v, type)]


def get_class_properties(namespace=None, kls=None) -> typing.List[str]:
    """ """
    return filter_by_type(namespace=namespace, kls=kls, type=typing.classproperty)


def get_properties(namespace=None, kls=None) -> typing.List[str]:
    """ """
    return filter_by_type(namespace=namespace, kls=kls, type=property)


def aggregate_across_bases(
    var: str = "",
    tspec: type_spec = None,
    name=None,
    bases=None,
    namespace=None,
):
    """aggregates values at `var` across all bases"""
    namespace = namespace if namespace is not None else tspec.namespace
    bases = bases if bases is not None else tspec.bases
    name = name if name is not None else tspec.name
    tracked = namespace.get(var, [])
    for b in bases:
        bval = getattr(b, var, [])
        assert isinstance(bval, list), bval
        tracked += bval
    return tracked


class ValidationResults(typing.NamedTuple, metaclass=namespace):
    suite: str = "default"
    warnings: typing.Dict[str, typing.List[typing.Any]] = collections.defaultdict(list)
    errors: typing.Dict = collections.defaultdict(dict)


class Meta(type):
    """ """

    NAMES = []

    def __new__(mcls: type, name: str, bases: typing.List, namespace: typing.Dict):
        """

        :param mcls: type:
        :param name: str:
        :param bases: typing.List:
        :param namespace: typing.Dict:
        :param mcls: type:
        :param name: str:
        :param bases: typing.List:
        :param namespace: typing.Dict:

        """
        tspec = type_spec(name=name, bases=bases, namespace=namespace)
        mcls.register(tspec)
        namespace = mcls.annotate(tspec)
        namespace = mcls.install_validation_protocol(tspec)
        kls = super().__new__(mcls, name, bases, namespace)
        kls.__validate_class__(kls)
        return kls

    @classmethod
    def register(
        mcls: type,
        tspec: type_spec = None,
    ) -> None:
        """

        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)
        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)

        """
        name, bases, namespace = tspec.name, tspec.bases, tspec.namespace
        this_name = namespace.get("name", None)
        this_name and Meta.NAMES.append(this_name)

    @classmethod
    def install_validation_protocol(
        mcls: type,
        tspec: type_spec = None,
    ) -> typing.Dict:
        """

        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)
        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)

        """

        name, bases, namespace = tspec.name, tspec.bases, tspec.namespace  # noqa

        def run_validators(kls, validators: typing.List = [], self=None, suite=None):
            vdata = ValidationResults(suite=suite)
            for validator in validators:
                validator(kls, self=self, vdata=vdata)
            return vdata

        def validation_results_hook(kls, vdata, quiet=False, strict=True):
            errors, warnings = vdata.errors, vdata.warnings
            suite = vdata.suite
            lname = f"flex::validation::{suite}"
            logger = lme.get_logger(lname)
            if errors and strict:
                raise ClassMalformed(errors)
            if warnings and not quiet:
                for msg, offenders in warnings.items():
                    logger.warning(f"{msg}")
                    logger.warning(f"  offenders: {offenders}")
                # if strict: raise Exception(warnings)

        def __validate_class__(kls, quiet=True):
            vdata = run_validators(
                kls, validators=kls.__class_validators__, suite="class"
            )
            advice = validation_results_hook(kls, vdata, quiet=quiet)
            return advice

        # FIXME: aggregate_across_bases?
        __class_validators__ = namespace.get("__class_validators__", [])
        __instance_validators__ = namespace.get("__instance_validators__", [])

        def validate_instance(kls, self=None):
            """requires: __instance_validators__
            provides: __instance_validation_results__

            :param kls: param self:  (Default value = None)
            :param self:  (Default value = None)

            """
            vdata = run_validators(
                kls,
                validators=kls.__instance_validators__,
                self=self,
                suite="instance",
            )
            advice = validation_results_hook(kls, vdata)
            kls.__instance_validation_results__ = vdata
            return advice

        namespace.update(
            __class_validators__=__class_validators__,
            __validate_class__=__validate_class__,
            __instance_validators__=__instance_validators__,
        )

        original_init = namespace.get("__init__", None)
        if __instance_validators__ and original_init:

            @functools.wraps(original_init)
            def wrapped_init(self, *args, **kwargs):
                skip_instance_validation = kwargs.pop("skip_instance_validation", False)
                result = original_init(self, *args, **kwargs)
                skip_instance_validation or validate_instance(self.__class__, self=self)
                return result

            namespace.update(__init__=wrapped_init)
        return namespace

    @classmethod
    def annotate(
        mcls: type,
        tspec: type_spec = None,
    ) -> typing.Dict:
        """Classes that are created by this metaclass will track
        various extra state by default; mostly this is for defining
        protocols that help with reflection

        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)
        :param mcls: type:
        :param tspec: type_spec:  (Default value = None)

        """
        name, bases, namespace = tspec.name, tspec.bases, tspec.namespace
        # __class_properties__ tracks class-properties[1]
        # from this class, and inherents them from all bases
        class_props = aggregate_across_bases(
            var="__class_properties__",
            name=name,
            bases=bases,
            namespace=namespace,
            # tspec=tspec,
        )
        class_props += get_class_properties(namespace=namespace)
        class_props = list(set(class_props))
        namespace.update({"__class_properties__": class_props})
        # __methods__ tracks instance-methods[1]
        # from this class, and inherents them from all bases
        # NB: this won't inherit private names (i.e. `_*')
        instance_methods = aggregate_across_bases(var="__methods__", tspec=tspec)
        instance_methods += [
            k
            for k, v in namespace.items()
            if not k.startswith("_") and isinstance(v, typing.FunctionType)
        ]
        instance_methods = list(set(instance_methods))
        namespace.update({"__methods__": instance_methods})
        # __properties__ tracks instance-properties[1]
        # for this class, and inherents them from all bases
        # NB: this won't inherit private names (i.e. `_*')
        instance_properties = aggregate_across_bases(
            var="__properties__",
            tspec=tspec,
        )
        instance_properties += [
            k
            for k, v in namespace.items()
            if not k.startswith("_") and isinstance(v, property)
        ]
        namespace.update({"__properties__": instance_properties})
        # namespace.update({'__method_tags__':dict(
        #     [[mname, tagging.TAGGER[mname]],
        #     for mname in instance_methods])})
        # namespace.update({'__class_tags__': .. })
        # namespace.update({'__static_methods__': .. })
        # namespace.update({'__properties__': .. })
        # LOGGER.debug(f'mcls for {name} returns')

        # assert (
        #     '__validate_class__' not in namespace
        # ), 'cannot override Meta validation-protocol'
        # namespace.update(
        #     __validate_class__=__validate_class__,
        #     # Malformed=ClassMalformed,
        # )

        return namespace
