from deci_platform_client.paths.conversion_model_id.get import ApiForget
from deci_platform_client.paths.conversion_model_id.post import ApiForpost
from deci_platform_client.paths.conversion_model_id.delete import ApiFordelete


class ConversionModelId(
    ApiForget,
    ApiForpost,
    ApiFordelete,
):
    pass
