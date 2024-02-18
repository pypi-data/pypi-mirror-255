from typing import Type, TypeVar

from typing_extensions import Annotated

T = TypeVar("T")


class DocumentMeta(type):
    def __getitem__(self, item: Type[T]) -> Type[T]:
        return Annotated[item, "__chalk_document__"]


Document = DocumentMeta("Document", (object,), {})
