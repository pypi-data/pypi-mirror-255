import typing_extensions

from deci_platform_client.paths import PathValues
from deci_platform_client.apis.paths.version import Version
from deci_platform_client.apis.paths.healthz import Healthz
from deci_platform_client.apis.paths.auth_logout import AuthLogout
from deci_platform_client.apis.paths.autonac_model_name_file_name import AutonacModelNameFileName
from deci_platform_client.apis.paths.autonac_run_id import AutonacRunId
from deci_platform_client.apis.paths.companies_stats import CompaniesStats
from deci_platform_client.apis.paths.conversion_model_id import ConversionModelId
from deci_platform_client.apis.paths.events_upgrade import EventsUpgrade
from deci_platform_client.apis.paths.events_support import EventsSupport
from deci_platform_client.apis.paths.events_buy_model import EventsBuyModel
from deci_platform_client.apis.paths.events_compare_models_in_model_zoo import EventsCompareModelsInModelZoo
from deci_platform_client.apis.paths.events_request_public_architecture import EventsRequestPublicArchitecture
from deci_platform_client.apis.paths.events_quota_increase import EventsQuotaIncrease
from deci_platform_client.apis.paths.events_type import EventsType
from deci_platform_client.apis.paths.events_ import Events
from deci_platform_client.apis.paths.experiments_ import Experiments
from deci_platform_client.apis.paths.experiments_experiment_id_upload_url import ExperimentsExperimentIdUploadUrl
from deci_platform_client.apis.paths.experiments_counter import ExperimentsCounter
from deci_platform_client.apis.paths.global_configuration_hardware import GlobalConfigurationHardware
from deci_platform_client.apis.paths.global_configuration_hardware_types import GlobalConfigurationHardwareTypes
from deci_platform_client.apis.paths.global_configuration_frameworks import GlobalConfigurationFrameworks
from deci_platform_client.apis.paths.global_configuration_architectures import GlobalConfigurationArchitectures
from deci_platform_client.apis.paths.global_configuration_deep_learning_tasks import GlobalConfigurationDeepLearningTasks
from deci_platform_client.apis.paths.global_configuration_performance_metrics import GlobalConfigurationPerformanceMetrics
from deci_platform_client.apis.paths.global_configuration_accuracy_metrics import GlobalConfigurationAccuracyMetrics
from deci_platform_client.apis.paths.global_configuration_batch_sizes import GlobalConfigurationBatchSizes
from deci_platform_client.apis.paths.global_configuration_quantization_levels import GlobalConfigurationQuantizationLevels
from deci_platform_client.apis.paths.global_configuration_feature_flags import GlobalConfigurationFeatureFlags
from deci_platform_client.apis.paths.infery_license_expiration import InferyLicenseExpiration
from deci_platform_client.apis.paths.invites_ import Invites
from deci_platform_client.apis.paths.managed_inference_generate_model_name import ManagedInferenceGenerateModelName
from deci_platform_client.apis.paths.model_repository_models import ModelRepositoryModels
from deci_platform_client.apis.paths.model_repository_models_name_name import ModelRepositoryModelsNameName
from deci_platform_client.apis.paths.model_repository_models_model_id import ModelRepositoryModelsModelId
from deci_platform_client.apis.paths.model_repository_models_verify_name import ModelRepositoryModelsVerifyName
from deci_platform_client.apis.paths.model_repository_models_verify import ModelRepositoryModelsVerify
from deci_platform_client.apis.paths.model_repository_v2_models import ModelRepositoryV2Models
from deci_platform_client.apis.paths.model_repository_models_public import ModelRepositoryModelsPublic
from deci_platform_client.apis.paths.model_repository_models_model_id_optimized import ModelRepositoryModelsModelIdOptimized
from deci_platform_client.apis.paths.model_repository_models_benchmark_benchmark_request_id import ModelRepositoryModelsBenchmarkBenchmarkRequestId
from deci_platform_client.apis.paths.model_repository_models_model_id_benchmark import ModelRepositoryModelsModelIdBenchmark
from deci_platform_client.apis.paths.model_repository_models_model_id_optimized_models import ModelRepositoryModelsModelIdOptimizedModels
from deci_platform_client.apis.paths.model_repository_models_model_id_autonac import ModelRepositoryModelsModelIdAutonac
from deci_platform_client.apis.paths.model_repository_models_model_id_optimize import ModelRepositoryModelsModelIdOptimize
from deci_platform_client.apis.paths.model_repository_models_model_id_gru import ModelRepositoryModelsModelIdGru
from deci_platform_client.apis.paths.model_repository_models_model_name_upload_url import ModelRepositoryModelsModelNameUploadUrl
from deci_platform_client.apis.paths.model_repository_models_model_name_copy_file import ModelRepositoryModelsModelNameCopyFile
from deci_platform_client.apis.paths.model_repository_models_model_id_download_url import ModelRepositoryModelsModelIdDownloadUrl
from deci_platform_client.apis.paths.model_repository_models_model_id_deploy_infery import ModelRepositoryModelsModelIdDeployInfery
from deci_platform_client.apis.paths.model_repository_model_zoo import ModelRepositoryModelZoo
from deci_platform_client.apis.paths.serving_ import Serving
from deci_platform_client.apis.paths.serving_start import ServingStart
from deci_platform_client.apis.paths.serving_load import ServingLoad
from deci_platform_client.apis.paths.serving_stop import ServingStop
from deci_platform_client.apis.paths.serving_demo_model_name_generate import ServingDemoModelNameGenerate
from deci_platform_client.apis.paths.serving_demo_model_name_generate_stream import ServingDemoModelNameGenerateStream
from deci_platform_client.apis.paths.serving_demo_model_name_busy import ServingDemoModelNameBusy
from deci_platform_client.apis.paths.serving_demo import ServingDemo
from deci_platform_client.apis.paths.snippets_template_name import SnippetsTemplateName
from deci_platform_client.apis.paths.support_log import SupportLog
from deci_platform_client.apis.paths.support_upload_log_url_tracking import SupportUploadLogUrlTracking
from deci_platform_client.apis.paths.support_upload_log_url import SupportUploadLogUrl
from deci_platform_client.apis.paths.users_ import Users
from deci_platform_client.apis.paths.users_user_id import UsersUserId
from deci_platform_client.apis.paths.users_user_id_activity import UsersUserIdActivity
from deci_platform_client.apis.paths.workspaces_stats import WorkspacesStats
from deci_platform_client.apis.paths.workspaces_ import Workspaces
from deci_platform_client.apis.paths.workspaces_id import WorkspacesId
from deci_platform_client.apis.paths.workspaces_workspace_id_members import WorkspacesWorkspaceIdMembers
from deci_platform_client.apis.paths.architectures import Architectures
from deci_platform_client.apis.paths.architectures_user import ArchitecturesUser
from deci_platform_client.apis.paths.autonac_runs_start import AutonacRunsStart
from deci_platform_client.apis.paths.autonac_runs_complete_autonac_run_id import AutonacRunsCompleteAutonacRunId

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.VERSION: Version,
        PathValues.HEALTHZ: Healthz,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.AUTONAC_MODEL_NAME_FILE_NAME: AutonacModelNameFileName,
        PathValues.AUTONAC_RUN_ID: AutonacRunId,
        PathValues.COMPANIES_STATS: CompaniesStats,
        PathValues.CONVERSION_MODEL_ID: ConversionModelId,
        PathValues.EVENTS_UPGRADE: EventsUpgrade,
        PathValues.EVENTS_SUPPORT: EventsSupport,
        PathValues.EVENTS_BUYMODEL: EventsBuyModel,
        PathValues.EVENTS_COMPAREMODELSINMODELZOO: EventsCompareModelsInModelZoo,
        PathValues.EVENTS_REQUESTPUBLICARCHITECTURE: EventsRequestPublicArchitecture,
        PathValues.EVENTS_QUOTAINCREASE: EventsQuotaIncrease,
        PathValues.EVENTS_TYPE: EventsType,
        PathValues.EVENTS_: Events,
        PathValues.EXPERIMENTS_: Experiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_UPLOAD_URL: ExperimentsExperimentIdUploadUrl,
        PathValues.EXPERIMENTS_COUNTER: ExperimentsCounter,
        PathValues.GLOBALCONFIGURATION_HARDWARE: GlobalConfigurationHardware,
        PathValues.GLOBALCONFIGURATION_HARDWARETYPES: GlobalConfigurationHardwareTypes,
        PathValues.GLOBALCONFIGURATION_FRAMEWORKS: GlobalConfigurationFrameworks,
        PathValues.GLOBALCONFIGURATION_ARCHITECTURES: GlobalConfigurationArchitectures,
        PathValues.GLOBALCONFIGURATION_DEEPLEARNINGTASKS: GlobalConfigurationDeepLearningTasks,
        PathValues.GLOBALCONFIGURATION_PERFORMANCEMETRICS: GlobalConfigurationPerformanceMetrics,
        PathValues.GLOBALCONFIGURATION_ACCURACYMETRICS: GlobalConfigurationAccuracyMetrics,
        PathValues.GLOBALCONFIGURATION_BATCHSIZES: GlobalConfigurationBatchSizes,
        PathValues.GLOBALCONFIGURATION_QUANTIZATIONLEVELS: GlobalConfigurationQuantizationLevels,
        PathValues.GLOBALCONFIGURATION_FEATUREFLAGS: GlobalConfigurationFeatureFlags,
        PathValues.INFERYLICENSE_EXPIRATION: InferyLicenseExpiration,
        PathValues.INVITES_: Invites,
        PathValues.MANAGEDINFERENCE_GENERATE_MODEL_NAME: ManagedInferenceGenerateModelName,
        PathValues.MODELREPOSITORY_MODELS: ModelRepositoryModels,
        PathValues.MODELREPOSITORY_MODELS_NAME_NAME: ModelRepositoryModelsNameName,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID: ModelRepositoryModelsModelId,
        PathValues.MODELREPOSITORY_MODELS_VERIFY_NAME: ModelRepositoryModelsVerifyName,
        PathValues.MODELREPOSITORY_MODELS_VERIFY: ModelRepositoryModelsVerify,
        PathValues.MODELREPOSITORY_V2_MODELS: ModelRepositoryV2Models,
        PathValues.MODELREPOSITORY_MODELS_PUBLIC: ModelRepositoryModelsPublic,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZED: ModelRepositoryModelsModelIdOptimized,
        PathValues.MODELREPOSITORY_MODELS_BENCHMARK_BENCHMARK_REQUEST_ID: ModelRepositoryModelsBenchmarkBenchmarkRequestId,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_BENCHMARK: ModelRepositoryModelsModelIdBenchmark,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZED_MODELS: ModelRepositoryModelsModelIdOptimizedModels,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_AUTONAC: ModelRepositoryModelsModelIdAutonac,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZE: ModelRepositoryModelsModelIdOptimize,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_GRU: ModelRepositoryModelsModelIdGru,
        PathValues.MODELREPOSITORY_MODELS_MODEL_NAME_UPLOADURL: ModelRepositoryModelsModelNameUploadUrl,
        PathValues.MODELREPOSITORY_MODELS_MODEL_NAME_COPYFILE: ModelRepositoryModelsModelNameCopyFile,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_DOWNLOADURL: ModelRepositoryModelsModelIdDownloadUrl,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_DEPLOY_INFERY: ModelRepositoryModelsModelIdDeployInfery,
        PathValues.MODELREPOSITORY_MODELZOO: ModelRepositoryModelZoo,
        PathValues.SERVING_: Serving,
        PathValues.SERVING_START: ServingStart,
        PathValues.SERVING_LOAD: ServingLoad,
        PathValues.SERVING_STOP: ServingStop,
        PathValues.SERVING_DEMO_MODEL_NAME_GENERATE: ServingDemoModelNameGenerate,
        PathValues.SERVING_DEMO_MODEL_NAME_GENERATE_STREAM: ServingDemoModelNameGenerateStream,
        PathValues.SERVING_DEMO_MODEL_NAME_BUSY: ServingDemoModelNameBusy,
        PathValues.SERVING_DEMO: ServingDemo,
        PathValues.SNIPPETS_TEMPLATE_NAME: SnippetsTemplateName,
        PathValues.SUPPORT_LOG: SupportLog,
        PathValues.SUPPORT_UPLOADLOGURL_TRACKING: SupportUploadLogUrlTracking,
        PathValues.SUPPORT_UPLOADLOGURL: SupportUploadLogUrl,
        PathValues.USERS_: Users,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS_USER_ID_ACTIVITY: UsersUserIdActivity,
        PathValues.WORKSPACES_STATS: WorkspacesStats,
        PathValues.WORKSPACES_: Workspaces,
        PathValues.WORKSPACES_ID: WorkspacesId,
        PathValues.WORKSPACES_WORKSPACE_ID_MEMBERS: WorkspacesWorkspaceIdMembers,
        PathValues.ARCHITECTURES: Architectures,
        PathValues.ARCHITECTURES_USER: ArchitecturesUser,
        PathValues.AUTONACRUNS_START: AutonacRunsStart,
        PathValues.AUTONACRUNS_COMPLETE_AUTONAC_RUN_ID: AutonacRunsCompleteAutonacRunId,
    }
)

path_to_api = PathToApi(
    {
        PathValues.VERSION: Version,
        PathValues.HEALTHZ: Healthz,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.AUTONAC_MODEL_NAME_FILE_NAME: AutonacModelNameFileName,
        PathValues.AUTONAC_RUN_ID: AutonacRunId,
        PathValues.COMPANIES_STATS: CompaniesStats,
        PathValues.CONVERSION_MODEL_ID: ConversionModelId,
        PathValues.EVENTS_UPGRADE: EventsUpgrade,
        PathValues.EVENTS_SUPPORT: EventsSupport,
        PathValues.EVENTS_BUYMODEL: EventsBuyModel,
        PathValues.EVENTS_COMPAREMODELSINMODELZOO: EventsCompareModelsInModelZoo,
        PathValues.EVENTS_REQUESTPUBLICARCHITECTURE: EventsRequestPublicArchitecture,
        PathValues.EVENTS_QUOTAINCREASE: EventsQuotaIncrease,
        PathValues.EVENTS_TYPE: EventsType,
        PathValues.EVENTS_: Events,
        PathValues.EXPERIMENTS_: Experiments,
        PathValues.EXPERIMENTS_EXPERIMENT_ID_UPLOAD_URL: ExperimentsExperimentIdUploadUrl,
        PathValues.EXPERIMENTS_COUNTER: ExperimentsCounter,
        PathValues.GLOBALCONFIGURATION_HARDWARE: GlobalConfigurationHardware,
        PathValues.GLOBALCONFIGURATION_HARDWARETYPES: GlobalConfigurationHardwareTypes,
        PathValues.GLOBALCONFIGURATION_FRAMEWORKS: GlobalConfigurationFrameworks,
        PathValues.GLOBALCONFIGURATION_ARCHITECTURES: GlobalConfigurationArchitectures,
        PathValues.GLOBALCONFIGURATION_DEEPLEARNINGTASKS: GlobalConfigurationDeepLearningTasks,
        PathValues.GLOBALCONFIGURATION_PERFORMANCEMETRICS: GlobalConfigurationPerformanceMetrics,
        PathValues.GLOBALCONFIGURATION_ACCURACYMETRICS: GlobalConfigurationAccuracyMetrics,
        PathValues.GLOBALCONFIGURATION_BATCHSIZES: GlobalConfigurationBatchSizes,
        PathValues.GLOBALCONFIGURATION_QUANTIZATIONLEVELS: GlobalConfigurationQuantizationLevels,
        PathValues.GLOBALCONFIGURATION_FEATUREFLAGS: GlobalConfigurationFeatureFlags,
        PathValues.INFERYLICENSE_EXPIRATION: InferyLicenseExpiration,
        PathValues.INVITES_: Invites,
        PathValues.MANAGEDINFERENCE_GENERATE_MODEL_NAME: ManagedInferenceGenerateModelName,
        PathValues.MODELREPOSITORY_MODELS: ModelRepositoryModels,
        PathValues.MODELREPOSITORY_MODELS_NAME_NAME: ModelRepositoryModelsNameName,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID: ModelRepositoryModelsModelId,
        PathValues.MODELREPOSITORY_MODELS_VERIFY_NAME: ModelRepositoryModelsVerifyName,
        PathValues.MODELREPOSITORY_MODELS_VERIFY: ModelRepositoryModelsVerify,
        PathValues.MODELREPOSITORY_V2_MODELS: ModelRepositoryV2Models,
        PathValues.MODELREPOSITORY_MODELS_PUBLIC: ModelRepositoryModelsPublic,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZED: ModelRepositoryModelsModelIdOptimized,
        PathValues.MODELREPOSITORY_MODELS_BENCHMARK_BENCHMARK_REQUEST_ID: ModelRepositoryModelsBenchmarkBenchmarkRequestId,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_BENCHMARK: ModelRepositoryModelsModelIdBenchmark,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZED_MODELS: ModelRepositoryModelsModelIdOptimizedModels,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_AUTONAC: ModelRepositoryModelsModelIdAutonac,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_OPTIMIZE: ModelRepositoryModelsModelIdOptimize,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_GRU: ModelRepositoryModelsModelIdGru,
        PathValues.MODELREPOSITORY_MODELS_MODEL_NAME_UPLOADURL: ModelRepositoryModelsModelNameUploadUrl,
        PathValues.MODELREPOSITORY_MODELS_MODEL_NAME_COPYFILE: ModelRepositoryModelsModelNameCopyFile,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_DOWNLOADURL: ModelRepositoryModelsModelIdDownloadUrl,
        PathValues.MODELREPOSITORY_MODELS_MODEL_ID_DEPLOY_INFERY: ModelRepositoryModelsModelIdDeployInfery,
        PathValues.MODELREPOSITORY_MODELZOO: ModelRepositoryModelZoo,
        PathValues.SERVING_: Serving,
        PathValues.SERVING_START: ServingStart,
        PathValues.SERVING_LOAD: ServingLoad,
        PathValues.SERVING_STOP: ServingStop,
        PathValues.SERVING_DEMO_MODEL_NAME_GENERATE: ServingDemoModelNameGenerate,
        PathValues.SERVING_DEMO_MODEL_NAME_GENERATE_STREAM: ServingDemoModelNameGenerateStream,
        PathValues.SERVING_DEMO_MODEL_NAME_BUSY: ServingDemoModelNameBusy,
        PathValues.SERVING_DEMO: ServingDemo,
        PathValues.SNIPPETS_TEMPLATE_NAME: SnippetsTemplateName,
        PathValues.SUPPORT_LOG: SupportLog,
        PathValues.SUPPORT_UPLOADLOGURL_TRACKING: SupportUploadLogUrlTracking,
        PathValues.SUPPORT_UPLOADLOGURL: SupportUploadLogUrl,
        PathValues.USERS_: Users,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS_USER_ID_ACTIVITY: UsersUserIdActivity,
        PathValues.WORKSPACES_STATS: WorkspacesStats,
        PathValues.WORKSPACES_: Workspaces,
        PathValues.WORKSPACES_ID: WorkspacesId,
        PathValues.WORKSPACES_WORKSPACE_ID_MEMBERS: WorkspacesWorkspaceIdMembers,
        PathValues.ARCHITECTURES: Architectures,
        PathValues.ARCHITECTURES_USER: ArchitecturesUser,
        PathValues.AUTONACRUNS_START: AutonacRunsStart,
        PathValues.AUTONACRUNS_COMPLETE_AUTONAC_RUN_ID: AutonacRunsCompleteAutonacRunId,
    }
)
