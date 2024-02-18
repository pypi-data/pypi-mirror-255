from typing import Any

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


from chalk.streams.base import StreamSource


class FileSource(BaseModel, StreamSource, frozen=True):
    path: str
    key_separator: str = "|"

    def _config_to_json(self) -> Any:
        return self.json()
