import typing_extensions

from deci_platform_client.apis.tags import TagValues
from deci_platform_client.apis.tags.platform_api import PlatformApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.PLATFORM: PlatformApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.PLATFORM: PlatformApi,
    }
)
