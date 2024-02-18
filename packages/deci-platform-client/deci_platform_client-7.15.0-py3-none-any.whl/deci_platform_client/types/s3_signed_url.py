from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class S3SignedUrl:
    def __init__(self, url: str, fields: "dict[Any, str]"):
        self.url = url
        self.fields = fields
