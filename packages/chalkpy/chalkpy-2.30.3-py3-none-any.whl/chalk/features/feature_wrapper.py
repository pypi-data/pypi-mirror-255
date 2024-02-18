from __future__ import annotations

import copy
from collections.abc import Iterable
from typing import Any, Literal, TypeVar, Union, TYPE_CHECKING

from chalk.features._chalkop import op
from chalk.features.filter import Filter
from chalk.serialization.parsed_annotation import ParsedAnnotation
from chalk.streams import get_name_with_duration
from chalk.utils.collections import ensure_tuple

if TYPE_CHECKING:
    from chalk.features.feature_field import Feature


T = TypeVar("T")


class FeatureWrapper:
    """
    FeatureWrapper emulates DataFrames and
    nested has-one relationships when used
    as a type annotation or within a filter.
    """

    def __init__(self, feature: Feature) -> None:
        # Binding as a private variable as not to have naming conflicts user's use of __getattr__
        super().__init__()
        self._chalk_feature = feature

    def __add__(self, other: object):
        if not isinstance(other, FeatureWrapper):
            return NotImplemented
        f_self = unwrap_feature(self)

        f_other = unwrap_feature(other)
        if f_other.is_scalar and f_self.is_scalar:
            if str == f_other.converter.rich_type == f_self.converter.rich_type:
                return op.concat_str(self, other)
            else:
                return op.sum(self, other)

    def __matmul__(self, other: int):
        return FeatureWrapper(self._chalk_feature.for_version(other))

    def __hash__(self):
        return hash(self._chalk_feature)

    def __gt__(self, other: object):
        return Filter(self._chalk_feature, ">", other)

    def __ge__(self, other: object):
        return Filter(self._chalk_feature, ">=", other)

    def __lt__(self, other: object):
        return Filter(self._chalk_feature, "<", other)

    def __le__(self, other: object):
        return Filter(self._chalk_feature, "<=", other)

    # len_registry: ClassVar[dict[int, FeatureWrapper]] = {}
    #
    # def __len__(self):
    #     r = randint(0, 100_000_000_000_000)
    #     self.len_registry[r] = self
    #     return r

    def _cmp(self, op: str, other: object):
        from chalk.features.feature_field import Feature

        if isinstance(other, Feature):
            # If comparing against a feature directly, then we know it's not being used in a join condition
            # Since join conditions would be against another FeatureWrapper or a literal value
            is_eq = self._chalk_feature == other
            # They are the same feature. Short-circuit and return a boolean
            if op == "==" and is_eq:
                return True
            if op == "!=" and not is_eq:
                return False
            return NotImplemented  # GT / LT doesn't really make sense otherwise
        if isinstance(other, type):
            return False
        return Filter(self._chalk_feature, op, other)

    def __ne__(self, other: object):
        return self._cmp("!=", other)

    def __eq__(self, other: object):
        return self._cmp("==", other)

    def __and__(self, other: object):
        return self._cmp("and", other)

    def __or__(self, other: object):
        if other is None:
            other = type(None)
        if isinstance(other, type):
            # The FeatureWrapper appears as a UnionType in a type annotation -- e.g.
            # def my_resolver(name: User.name | None = None, ...)
            return Union[other, self]  # type: ignore
        return self._cmp("or", other)

    def __repr__(self):
        return f"FeatureWrapper(fqn={self._chalk_feature.root_fqn}, typ={self._chalk_feature.typ})"

    def __str__(self):
        return str(self._chalk_feature)

    def in_(self, examples: Iterable):
        return self._cmp("in", examples)

    def __call__(self, *args: Any, **kwargs: Any):
        # Using a generic signature since this signature must support all types of features
        # Currently, though, only windowed features are callable
        if self._chalk_feature.is_windowed:
            return self._chalk_get_windowed_feature(*args, **kwargs)
        raise TypeError(f"Feature {self} is not callable")

    def _chalk_get_windowed_feature(self, window: Union[str, int]):
        if not isinstance(window, (str, int)):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("Window duration must be a string or an int")

        from chalk.features import FeatureSetBase

        parent = (
            FeatureSetBase.registry[self._chalk_feature.namespace]
            if len(self._chalk_feature.path) == 0
            else FeatureWrapper(self._chalk_feature.path[-1].parent)
        )
        desired_attribute_name = get_name_with_duration(self._chalk_feature.attribute_name, window)
        if not hasattr(parent, desired_attribute_name):
            formatted_window_durations = [f"'{x}s'" for x in self._chalk_feature.window_durations]
            raise TypeError(
                (
                    f"Unsupported window duration '{window}' for '{self._chalk_feature.root_fqn}'. "
                    f"Durations {', '.join(formatted_window_durations)} are supported."
                )
            )
        return getattr(parent, desired_attribute_name)

    def __getitem__(self, item: Any):
        from chalk.features.feature_field import get_distance_feature_name, Feature
        from chalk.features.pseudofeatures import Distance
        from chalk.features.feature_set import FeatureSetBase

        if len(self._chalk_feature.window_durations) > 0:
            return self._chalk_get_windowed_feature(*ensure_tuple(item))

        dataframe_typ = self._chalk_feature.typ.as_dataframe()
        if dataframe_typ is not None:
            item = list(ensure_tuple(item))
            for i, x in enumerate(item):
                if x is Distance:
                    # If requesting a distance, we need to replace it with the distance pseudofeature
                    filter = self._chalk_feature.join
                    if filter is None:
                        raise ValueError("The `Distance` feature can only be used with has-many relationship")
                    if not filter.operation.startswith("is_near_"):
                        raise ValueError("The `Distance` feature can only be used with a nearest neighbor join")
                    assert isinstance(filter.lhs, Feature)
                    assert isinstance(filter.rhs, Feature)
                    local_feature = filter.lhs if filter.lhs.namespace == self._chalk_feature.namespace else filter.rhs
                    foreign_feature = (
                        filter.lhs if filter.lhs.namespace != self._chalk_feature.namespace else filter.rhs
                    )
                    assert local_feature != foreign_feature, "The local and foreign features must be different"
                    key = get_distance_feature_name(
                        local_namespace=local_feature.namespace,
                        local_name=local_feature.name,
                        local_hm_name=self._chalk_feature.name,
                        op=filter.operation,
                        foreign_name=foreign_feature.name,
                    )
                    x = next(f for f in FeatureSetBase.registry[foreign_feature.namespace].features if f.name == key)
                    item[i] = x
            item = tuple(item)

            f_copy = FeatureWrapper(copy.copy(self._chalk_feature))
            f_copy._chalk_feature.typ = ParsedAnnotation(underlying=dataframe_typ[item])
            if (
                hasattr(f_copy._chalk_feature, "path")
                and len(f_copy._chalk_feature.path) > 0
            ):
                f_copy._chalk_feature.path[-1].child = unwrap_feature(f_copy)

            return f_copy

        from chalk.df.ast_parser import parse_feature_iter

        if item == 0:
            return parse_feature_iter(self)
        elif isinstance(item, int):
            raise StopIteration(f"Cannot subscript feature '{self}' past 0. Attempting to subscript with '{item}'")
        raise TypeError(f"Feature '{self}' does not support subscripting. Attempted to subscript with '{item}'")

    def __getattr__(self, item: str):
        from chalk.features.feature_field import Feature

        # Passing through __getattr__ on has_one features, as users can use getattr
        # notation in annotations for resolvers
        if item.startswith("__") and not item.startswith("__chalk"):
            # Short-circuiting on the dunders to be compatible with copy.copy
            raise AttributeError(item)

        if self._chalk_feature.joined_class is not None:
            for f in self._chalk_feature.joined_class.features:
                assert isinstance(f, Feature), f"HasOne feature {f} does not inherit from FeaturesBase"
                if f.attribute_name == item:
                    return FeatureWrapper(self._chalk_feature.copy_with_path(f))

            assert self._chalk_feature.features_cls is not None
            self._chalk_feature.features_cls.__chalk_error_builder__.invalid_attribute(
                self._chalk_feature.joined_class.namespace,
                item=item,
                candidates=[f.name for f in self._chalk_feature.joined_class.features],
                back=1,
            )

        assert self._chalk_feature.features_cls is not None
        self._chalk_feature.features_cls.__chalk_error_builder__.invalid_attribute(
            self._chalk_feature.features_cls.namespace,
            item=item,
            candidates=[],
            back=1,
        )

    def is_near(self, item: Any, metric: Literal["l2", "cos", "ip"] = "l2") -> Filter:
        other = unwrap_feature(item)
        self_vector = self._chalk_feature.typ.as_vector()
        if self_vector is None:
            raise TypeError(
                f"Nearest neighbor relationships are only supported for vector features. Feature '{self._chalk_feature.root_fqn}' is not a vector."
            )
        other_vector = other.typ.as_vector()
        if other_vector is None:
            raise TypeError(
                f"Nearest neighbor relationships are only supported for vector features. Feature '{other.root_fqn}' is not a vector."
            )
        if self._chalk_feature.converter.pyarrow_dtype != other.converter.pyarrow_dtype:
            raise TypeError(
                (
                    f"Nearest neighbor relationships are only supported if both vectors have the same data type and dimensions. "
                    f"Feature '{self._chalk_feature.root_fqn}' is of type `{self._chalk_feature.converter.pyarrow_dtype}` "
                    f" while feature '{other.root_fqn}' is `{other.converter.pyarrow_dtype}`."
                )
            )
        return Filter(self._chalk_feature, f"is_near_{metric}", other)


def unwrap_feature(maybe_feature_wrapper: Any) -> Feature:
    """Unwrap a class-annotated FeatureWrapper instance into the underlying feature.

    For example:

        @features
        class FooBar:
            foo: str
            bar: int

        type(FooBar.foo) is FeatureWrapper
        type(unwrap_feature(FooBar.foo)) is Feature
    """
    from chalk.features.feature_field import Feature

    if isinstance(maybe_feature_wrapper, FeatureWrapper):
        maybe_feature_wrapper = maybe_feature_wrapper._chalk_feature  # pyright: ignore[reportPrivateUsage]
    if isinstance(maybe_feature_wrapper, Feature):
        return maybe_feature_wrapper
    raise TypeError(
        f"{maybe_feature_wrapper} is of type {type(maybe_feature_wrapper).__name__}, expecting type FeatureWrapper"
    )


def ensure_feature(feature: Union[str, Feature, FeatureWrapper, Any]) -> Feature:
    from chalk.features.feature_field import Feature

    if isinstance(feature, str):
        return Feature.from_root_fqn(feature)
    if isinstance(feature, FeatureWrapper):
        return unwrap_feature(feature)
    if isinstance(feature, Feature):
        return feature
    raise TypeError(f"Feature identifier {feature} of type {type(feature).__name__} is not supported.")


__all__ = ["FeatureWrapper", "unwrap_feature", "ensure_feature"]
