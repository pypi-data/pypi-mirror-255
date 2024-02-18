# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from deci_platform_client.paths.managed_inference_generate_model_name import Api

from deci_platform_client.paths import PathValues

path = PathValues.MANAGEDINFERENCE_GENERATE_MODEL_NAME