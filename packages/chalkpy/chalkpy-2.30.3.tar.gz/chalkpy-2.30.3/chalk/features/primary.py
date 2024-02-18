from typing import TYPE_CHECKING, Any, Protocol, Type, TypeVar, overload

from typing_extensions import Annotated

from chalk.features.feature_wrapper import unwrap_feature

T = TypeVar("T")

if TYPE_CHECKING:

    class Primary(Protocol[T]):
        """Marks a feature as the primary feature for a feature class.

        Features named `id` on feature classes without an explicit primary
        feature are declared primary keys by default, and don't need to be
        marked with `Primary`.

        If you have primary key feature with a name other than `id`,
        you can use this marker to indicate the primary key.

        Examples
        --------
        >>> @features
        ... class User:
        ...     uid: Primary[int]
        """

        @overload
        def __get__(self, instance: None, owner: Any) -> Type[T]:
            ...

        @overload
        def __get__(self, instance: object, owner: Any) -> T:
            ...

        def __set__(self, instance: Any, value: T) -> None:
            ...

        def __delete__(self, instance: Any) -> None:
            ...

else:

    class Primary:
        """Marks a feature as the primary feature for a feature class.

        Features named `id` on feature classes without an explicit primary
        feature are declared primary keys by default, and don't need to be
        marked with `Primary`.

        If you have primary key feature with a name other than `id`,
        you can use this marker to indicate the primary key.

        Examples
        --------
        >>> @features
        ... class User:
        ...     uid: Primary[int]
        """

        def __class_getitem__(cls, item: Type):
            """
            Parameters
            ----------
            item
                The type of the feature value.

            Returns
            -------
            Annotated[item, "__chalk_primary__"]
                The type, with a special annotation indicating that it is a
                primary key.
            """
            return Annotated[item, "__chalk_primary__"]


def is_primary(f: Any) -> bool:
    """Determine whether a feature is a primary key.

    Parameters
    ----------
    f
        A feature (i.e. `User.email`)

    Raises
    ------
    TypeError
        If `f` is not a feature.

    Returns
    -------
    bool
        `True` if `f` is primary and `False` otherwise.

    Examples
    --------
    >>> from chalk.features import features
    >>> @features
    ... class User:
    ...     uid: Primary[int]
    ...     email: str
    >>> assert is_primary(User.uid)
    >>> assert not is_primary(User.email)
    """
    return unwrap_feature(f).primary
