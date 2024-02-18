# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from deci_platform_client.paths.serving_demo_model_name_generate_stream import Api

from deci_platform_client.paths import PathValues

path = PathValues.SERVING_DEMO_MODEL_NAME_GENERATE_STREAM