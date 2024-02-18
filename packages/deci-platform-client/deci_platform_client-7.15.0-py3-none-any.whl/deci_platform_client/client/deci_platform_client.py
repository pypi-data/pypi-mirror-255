import io
import logging
import os
import re
import threading
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager, redirect_stdout
from datetime import datetime
from pathlib import Path
from timeit import default_timer
from typing import TYPE_CHECKING, overload
from uuid import UUID, uuid4

import requests
from deci_common.abstractions.abstract_logger import get_logger
from requests import Response

from deci_platform_client.apis.tags.platform_api import PlatformApi
from deci_platform_client.client.api_client import ApiClient
from deci_platform_client.client.configuration import Configuration
from deci_platform_client.client.exceptions import (
    BenchmarkRequestError,
    BenchmarkResultNotFoundException,
    PyTorchNotInstalledError,
    UnsupportedLoadedModelFramework,
)
from deci_platform_client.client.helpers import (
    TqdmUpTo,
    build_gru_request_form,
    build_model_metadata,
    default_hardware_list,
)
from deci_platform_client.client.schemas_hack import hack_schemas
from deci_platform_client.models import (
    BaselineModelResponseMetadata,
    BodyAddModelV2,
    BodyRegisterUserArchitecture,
    BodySendModelBenchmarkRequest,
    DeepLearningTask,
    EditModelForm,
    ExperimentForm,
    FrameworkType,
    InviteColleagueWithWorkspace,
    LogRequestBody,
    Metric,
    ModelBenchmarkResultMetadata,
    ModelBenchmarkState,
    ModelMetadata,
    ModelMetadataIn,
    ModelOptimizationState,
    ModelSource,
    QuantizationLevel,
    SentryLevel,
    StartAutonacRun,
    TrainingExperiment,
    UserArchitecture,
    WorkspaceForm,
)
from deci_platform_client.types.s3_signed_url import S3SignedUrl

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping, Sequence
    from logging import Logger
    from typing import Any, Literal, Optional, Union

    from torch import nn

    from deci_platform_client.client.helpers import Hardware
    from deci_platform_client.models import (
        AccuracyMetric,
        AccuracyMetricKey,
        AutoNACFileName,
        BatchSize,
        DatasetName,
        WorkspaceBase,
    )

hack_schemas()


class DeciPlatformClient:
    """
    Attributes:
        raw_api (PlatformApi): This is a low-level interface to the platform. Shouldn't be used directly.
    """

    def __init__(self, proxy_headers: "Optional[dict[str, Any]]" = None, logger: "Optional[Logger]" = None):
        """Create a new instance of the platform client.

        In order to use the client, you need to login to the platform.
        To do so, you'll need to set the following environment variables:

        * `DECI_CLIENT_ID`: The user's client ID generated in the [Deci platform](https://console.deci.ai/settings/api-tokens).
        * `DECI_CLIENT_SECRET`: The user's secret generated in the [Deci platform](https://console.deci.ai/settings/api-tokens).
        * `DECI_WORKSPACE_ID`: Optional desired workspace ID to use upon a successful login. If not specified, the client will use the first workspace retrieved. The workspace ID should be retrieved from the platform [here](https://console.deci.ai/settings/workspace)

        Args:
            proxy_headers: A dictionary containing headers that will be sent to the proxy (`urllib3.ProxyManager`). In case of HTTP they are being sent with each request, while in the HTTPS/CONNECT case they are sent only once. Could be used for proxy authentication.
            logger: An optional logger to use. If not specified, a default logger will be used.
        """
        self._logger = logger or get_logger(logger_name="deci-platform-client")

        configuration = Configuration(proxy_headers=proxy_headers)
        self.api_client = ApiClient(configuration)
        self.raw_api = PlatformApi(self.api_client)

        self.experiment: "Optional[TrainingExperiment]" = None
        self.experiments_pool: "dict[str, threading.Thread]" = dict()

        client_id = os.getenv("DECI_CLIENT_ID")
        secret = os.getenv("DECI_CLIENT_SECRET")
        if client_id is not None and secret is not None:
            self.login(client_id=client_id, secret=secret)

    def login(self, client_id: str, secret: str) -> None:
        """Login to the platform.

        Tip:
            This method is called implicitly when you instantiate the client and specify the environment variables:

            -   `DECI_CLIENT_ID`
            -   `DECI_CLIENT_SECRET`

            If you haven't done so, you'll need to call this method manually.
            You can generate the client ID and secret from your [platform account](https://console.deci.ai/settings/api-tokens)

        Args:
          client_id: The user's client ID generated in the Deci platform.
          secret: The user's secret generated in the Deci platform.

        """
        self.api_client.set_up_frontegg_auth(client_id=client_id, secret=secret)
        self._logger.info(
            f"Successfully logged in as {self.api_client.email} (Workspace ID - {self.api_client.workspace_id})."
        )

    def logout(self):
        """Log out from the Deci platform (Disposes the credentials)."""
        self.api_client.tear_down_frontegg_auth()
        self._logger.info("Successfully logged out.")

    def _prepare_model(
        self,
        model_metadata: "ModelMetadataIn",
        model: "Optional[nn.Module]",
        inputs_metadata: "Optional[Mapping[str, Mapping[str, Any]]]",
        **kwargs: "Any",
    ) -> "tuple[ModelMetadataIn, Optional[str]]":
        model_metadata_update = {"source": ModelSource.SDK}
        model_path: "Optional[str]" = None
        if model is not None:
            if model_metadata.framework == FrameworkType.PYTORCH:
                with self.support(tag="pytorch-to-onnx"):
                    model_path = self.convert_pytorch_to_onnx(
                        local_loaded_model=model,
                        inputs_metadata=inputs_metadata,
                        **kwargs,
                    )
                model_metadata_update["framework"] = FrameworkType.ONNX
            else:
                raise UnsupportedLoadedModelFramework
        model_metadata = ModelMetadataIn(**{**model_metadata, **model_metadata_update})
        self.raw_api.assert_model_arguments(body=model_metadata)  # type: ignore[arg-type]
        return model_metadata, model_path

    def _add_model_start(
        self,
        model_metadata: "ModelMetadataIn",
        model: "Optional[nn.Module]" = None,
        model_path: "Optional[str]" = None,
        inputs_metadata: "Optional[Mapping[str, Mapping[str, Any]]]" = None,
        **kwargs: "Any",
    ) -> "tuple[ModelMetadataIn, str]":
        if (model is not None and model_path is not None) or (model is None and model_path is None):
            raise TypeError(
                f"Exactly one of model and model_path parameters must be specified,"
                f" received model={model}, model_path={model_path}"
            )

        model_metadata, converted_pytorch_model_path = self._prepare_model(
            model_metadata=model_metadata,
            model=model,
            inputs_metadata=inputs_metadata,
            **kwargs,
        )
        storage_etag = self._upload_file_to_s3(
            converted_pytorch_model_path if converted_pytorch_model_path is not None else model_path,
            model_metadata.name,
        )

        if converted_pytorch_model_path is not None:
            try:
                os.remove(converted_pytorch_model_path)
            except (OSError, UnboundLocalError):
                pass

        return model_metadata, storage_etag

    @overload
    def register_model(
        self,
        model: "nn.Module",
        *,
        name: str,
        framework: "FrameworkType.PYTORCH",
        dl_task: DeepLearningTask = DeepLearningTask.OTHER,
        inputs_metadata: "Mapping[str, Mapping[str, Any]]",
        input_dimensions: "Optional[Literal[None]]" = None,
        hardware_types: "Optional[list[Hardware]]" = None,
        accuracy: "Optional[float]" = None,
        accuracy_key: "Optional[AccuracyMetricKey]" = None,
        description: "Optional[str]" = None,
        dataset_name: "Optional[DatasetName]" = None,
        target_metric: "Optional[Metric]" = None,
        target_metric_value: "Optional[float]" = None,
        model_size: "Optional[float]" = None,
        memory_footprint: "Optional[float]" = None,
        **kwargs: "Any",
    ) -> "UUID":
        ...

    @overload
    def register_model(
        self,
        model: "Union[Path, str]",
        *,
        name: str,
        framework: "Union[FrameworkType.TF2, FrameworkType.KERAS, FrameworkType.ONNX]",
        dl_task: str = DeepLearningTask.OTHER,
        inputs_metadata: "Optional[Literal[None]]" = None,
        input_dimensions: "Optional[Union[Sequence[int], Sequence[Sequence[int]]]]" = None,
        hardware_types: "Optional[list[Hardware]]" = None,
        accuracy: "Optional[float]" = None,
        accuracy_key: "Optional[AccuracyMetricKey]" = None,
        description: "Optional[str]" = None,
        dataset_name: "Optional[DatasetName]" = None,
        target_metric: "Optional[Metric]" = None,
        target_metric_value: "Optional[float]" = None,
        model_size: "Optional[float]" = None,
        memory_footprint: "Optional[float]" = None,
        **kwargs: "Any",
    ) -> "UUID":
        ...

    def register_model(
        self,
        model: "Union[Path, str, nn.Module]",
        *,
        name: str,
        framework: "Union[FrameworkType.TF2, FrameworkType.KERAS, FrameworkType.ONNX, FrameworkType.PYTORCH]",
        dl_task: DeepLearningTask = DeepLearningTask.OTHER,
        inputs_metadata: "Optional[Mapping[str, Mapping[str, Any]]]" = None,
        input_dimensions: "Optional[Union[Sequence[int], Sequence[Sequence[int]]]]" = None,
        hardware_types: "Optional[list[Hardware]]" = None,
        accuracy: "Optional[float]" = None,
        accuracy_key: "Optional[AccuracyMetricKey]" = None,
        description: "Optional[str]" = None,
        dataset_name: "Optional[DatasetName]" = None,
        target_metric: "Optional[Metric]" = None,
        target_metric_value: "Optional[float]" = None,
        model_size: "Optional[float]" = None,
        memory_footprint: "Optional[float]" = None,
        **kwargs: "Any",
    ) -> "UUID":
        """Registers a new model to the user's model repository.

        The new model metadata details are passed to the API, and the model itself is uploaded to s3 from local machine or from another public s3 bucket.
        If the model's framework is PyTorch, it will first be converted to ONNX.

        Examples:
            ### Uploading PyTorch model
            ```py hl_lines="8-20"
            import super_gradients
            from deci_platform_client import DeciPlatformClient
            from deci_platform_client.models import FrameworkType, DeepLearningTask

            client = DeciPlatformClient()
            architecture = "resnet18"
            model = super_gradients.training.models.get(model_name=architecture, num_classes=1000)
            inputs_metadata = {
                                "input0": {
                                    "dtype": np.float32,
                                    "shape": (1, 3, 224, 224),
                                },
                               }
            model_id = client.register_model(
                model=model,
                name=architecture,
                framework=FrameworkType.PYTORCH,
                dl_task=DeepLearningTask.CLASSIFICATION,
                inputs_metadata=inputs_metadata
            )
            ```

            where batch size is 1 and the first input dimension is (3, 224, 224).

            ### Uploading model from local file
            ```py hl_lines="5-10"
            from deci_platform_client import DeciPlatformClient
            from deci_platform_client.models import FrameworkType, DeepLearningTask

            client = DeciPlatformClient()
            model_id = client.register_model(
                model="/path/to/yolox.onnx",
                name="yolox",
                framework=FrameworkType.ONNX,
                dl_task=DeepLearningTask.OBJECT_DETECTION,
            )
            ```

            ### Upload model from s3
            ```py hl_lines="5-10"
            from deci_platform_client import DeciPlatformClient
            from deci_platform_client.models import FrameworkType, DeepLearningTask

            client = DeciPlatformClient()
            model_id = client.register_model(
                model="s3://public-nlp-models/roberta.zip",
                name="Roberta",
                framework=FrameworkType.TF2,
                dl_task=DeepLearningTask.NLP,
            )
            ```

        Args:
            model: PyTorch loaded model object OR path to the model's file OR s3 URI starting with `s3://`
            name: The model's name, should be unique within the user's model repository
            framework: The model's framework. Currently supported frameworks are: PyTorch, TensorFlow, Keras and ONNX
            dl_task: The deep learning task of the model.
            inputs_metadata: A dictionary that describes the inputs of the model, needed for PyTorch upload, the dict should have the following schema:

                - KEY (`str`): an input name
                - VALUE (`dict`): A dictionary with the following schema:

                    - `dtype` (`numpy.dtype`) - describes the data type of the input
                    - `shape` (`tuple[int]`) that describes the shape of the input with batch size as the first element of the tuple

                For an example see the [pytorch model upload example](#pytorch)
            input_dimensions: The model's input dimensions, will be ignored for PyTorch models
            hardware_types: A list of hardware types to benchmark the model on
            accuracy: The model's accuracy, as a float
            accuracy_key: The model's accuracy key
            description: The model's description
            dataset_name: The name of a similar dataset to that your model was trained on
            target_metric: The model's target metric
            target_metric_value: The model's target metric value
            model_size: The model's target size
            memory_footprint: The model's target memory footprint

        The following parameters are used to control the conversion of a PyTorch model to ONNX.
        If you wish to use more parameters, see the [torch.onnx.export documentation](https://pytorch.org/docs/master/onnx.html#torch.onnx.export). All parameters passed as keyword arguments will be passed to torch.onnx.export.

        Other Parameters:
            opset_version (int, optional): The version of the [default (ai.onnx) opset](https://github.com/onnx/onnx/blob/master/docs/Operators.md) to target. Must be >= 7 and <= 16. Defaults to 15
            do_constant_folding (bool): Apply the constant-folding optimization. Constant-folding will replace some of the ops that have all constant inputs with pre-computed constant nodes. Defaults to `True`
            dynamic_axes: By default the exported model will have the shapes of all input and output tensors set to exactly match those given in `inputs_metadata`. To specify axes of tensors as dynamic (i.e. known only at run-time), set `dynamic_axes` to a dict with schema:

                - KEY (`str`): an input or output name. Each name must also be provided in `input_names` or `output_names`
                - VALUE (`dict` or `list`): If a `dict`, keys are axis indices and values are axis names. If a `list`, each element is an axis index
            input_names (list[str]): names to assign to the input nodes of the graph, in order
            output_names (list[str]): names to assign to the output nodes of the graph, in order
        Returns:
            The ID of the model registered, in the user's model repository
        """
        if framework == FrameworkType.PYTORCH:
            from torch import nn

            if not isinstance(model, nn.Module):
                raise TypeError(f"Model parameter must be a nn.Module, received {type(model)}")
            if inputs_metadata is None:
                raise TypeError(
                    "Model inputs metadata must be specified when uploading pytorch models. Refer to the documentation of this function"
                )
            if not all(
                "shape" in input_metadata and "dtype" in input_metadata for input_metadata in inputs_metadata.values()
            ):
                raise TypeError(
                    "Model inputs metadata must have a 'dtype' and 'shape' key. Refer to the documentation of this function"
                )
            input_dimensions = [list(input_metadata["shape"][1:]) for input_metadata in inputs_metadata.values()]
            kwargs["model"] = model
        else:
            kwargs["model_path"] = model
            if input_dimensions is None:
                input_dimensions = []

        model_metadata = build_model_metadata(
            name=name,
            framework=framework,
            dl_task=dl_task,
            input_dimensions=input_dimensions,
            primary_hardware=hardware_types[0] if hardware_types else None,
            accuracy=accuracy,
            accuracy_key=accuracy_key,
            description=description,
            dataset_name=dataset_name,
            target_metric=target_metric,
            target_metric_value=target_metric_value,
            model_size=model_size,
            memory_footprint=memory_footprint,
        )
        kwargs.pop("model_metadata", None)
        kwargs.pop("channel_first", None)
        kwargs["inputs_metadata"] = inputs_metadata

        if isinstance(model, str) and model.startswith("s3://"):
            storage_etag = self.raw_api.copy_model_file_from_s3_uri(
                body={"s3_uri": model},
                path_params={"model_name": name},
            ).body["data"]
        else:
            model_metadata, storage_etag = self._add_model_start(model_metadata=model_metadata, **kwargs)
        response = self.raw_api.add_model_v2(
            body=BodyAddModelV2(model=model_metadata, hardware_types=hardware_types or default_hardware_list()),
            query_params={"etag": storage_etag},
        )
        return response.body["data"]["modelId"]

    def download_model(self, model_id: str, dest_path: "Optional[str]" = None, show_progress: bool = True) -> Path:
        """Downloads a model with the specified ID from the platform to a specified path.

        Args:
            model_id: The model ID to download
            dest_path: The full path to which the model will be written to, will download to current working directory if `None` supplied.
            show_progress: Whether to show the current progress of download

        Returns:
            Path to the downloaded model
        """
        response = self.raw_api.get_model_signed_url_for_download(path_params={"model_id": model_id})
        download_url = str(response.body["data"])
        if not dest_path:
            filename = re.findall('filename="(.+)"&', urllib.parse.unquote(download_url))[0]
            dest_path = Path.cwd().joinpath(filename)
        self._logger.info("Downloading...")
        with TqdmUpTo(**TqdmUpTo.DOWNLOAD_PARAMS, desc=str(dest_path)) as t:
            urllib.request.urlretrieve(
                url=download_url,
                filename=dest_path,
                reporthook=t.update_to if show_progress else None,
            )
        self._logger.info(f"The model was downloaded to {dest_path}")
        return dest_path

    @staticmethod
    @contextmanager
    def redirect_output() -> "Generator[tuple[io.StringIO, io.StringIO], Any, None]":
        root_logger = logging.getLogger()
        logs = io.StringIO()
        handler = logging.StreamHandler(logs)
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)
        with redirect_stdout(io.StringIO()) as stdout:
            yield stdout, logs

        root_logger.removeHandler(handler)

    def send_support_logs(
        self,
        *,
        log: str,
        tag: "Optional[str]" = None,
        level: "Optional[SentryLevel]" = None,
    ) -> None:
        if len(log) == 0:
            self._logger.info("No logs detected, not sending anything.")
            return
        log_request_body = {}
        if level is not None:
            log_request_body["level"] = level
        if tag is not None:
            log_request_body["tag"] = tag
        self.raw_api.log(body=LogRequestBody(log=log, **log_request_body))
        self._logger.info("Successfully sent support logs.")

    @contextmanager
    def support(
        self,
        tag: "Optional[str]" = None,
        level: "Optional[SentryLevel]" = None,
    ) -> "Generator[None, None, Any]":
        exception: "Optional[Exception]" = None
        with self.redirect_output() as (stdout, logs):
            try:
                yield
            except Exception as e:
                exception = e
        log = "\n".join(["stdout:", stdout.getvalue(), "logging:", logs.getvalue()])
        self.send_support_logs(log=log, tag=tag, level=level)
        if exception is not None:
            raise exception

    @staticmethod
    def convert_pytorch_to_onnx(
        local_loaded_model: "nn.Module",
        inputs_metadata: "Mapping[str, Mapping[str, Any]]",
        export_path: "Optional[str]" = None,
        opset_version=15,
        do_constant_folding=True,
        dynamic_axes: "Mapping[str, Any]" = None,
        **kwargs: "Any",
    ) -> str:
        """
        Convert PyTorch model to ONNX.
        :param local_loaded_model: Pytorch loaded model object (nn.Module).
        :param inputs_metadata: A dictionary that describes the inputs of the model, ex:
            >>> {\
                    "input0": {\
                        "dtype": np.float32,\
                        "shape": (1, 3, 224, 224),\
                    },\
                    ...\
                }
            where batch size is up to 64 and the first input dimension is (3, 224, 224).
        :param export_path: Path to where to save the converted model file.
            If not given "converted_model_{time.time()}.onnx" will be used.

        You may pass the following parameters as kwargs in order to control the conversion to onnx:
        :param opset_version
        :param do_constant_folding
        """
        import numpy as np

        model_inputs = []
        input_dimensions = []
        try:
            import torch
        except Exception as e:
            raise PyTorchNotInstalledError from e

        # Building the dummy inputs
        for input_name, input_metadata in inputs_metadata.items():
            input_shape, input_dtype = input_metadata["shape"], input_metadata["dtype"]
            input_size = tuple(input_shape)
            if np.issubdtype(input_dtype, int):
                _input = torch.randint(low=1, high=255, size=input_size, requires_grad=False)
            else:
                _input = torch.randn(size=input_size, requires_grad=False)
            model_inputs.append(_input)
            input_dimensions.append(input_size)

        model_path = export_path if export_path is not None else f"converted_model_{time.time()}.onnx"

        # Export the model
        local_loaded_model.eval()  # Put model into eval mode

        logging.info(f"Running torch.jit.trace on model with input dimensions {input_dimensions}")
        try:
            local_loaded_model = torch.jit.trace(local_loaded_model, example_inputs=model_inputs, strict=False)
            logging.info("Successfully traced model.")
        except torch.jit.TracingCheckError as e:
            logging.warning("Error tracing model")
            logging.warning(e)

        logging.info(f"Exporting model to ONNX with opset version {opset_version}")
        try:
            torch.onnx.export(
                model=local_loaded_model,  # Model being run
                # a torch tensor contains the model input dims and the primary_batch_size.
                args=model_inputs[0] if len(model_inputs) == 1 else model_inputs,
                f=model_path,  # Where to save the model (can be a file or file-like object)
                export_params=True,  # Store the trained parameter weights inside the model file
                opset_version=opset_version,  # The ONNX version to export the model to
                do_constant_folding=do_constant_folding,  # Whether to execute constant folding for optimization
                dynamic_axes=dynamic_axes,  # The dynamic axes names for every input
                **kwargs,
            )
        except Exception as e:
            logging.error("Error converting model")
            logging.error(e)
            raise
        logging.info(f"Successfully exported model to {model_path}")

        return model_path

    def _upload_file_to_s3(self, model_local_path: str, model_name: str, model_version: "Optional[str]" = None):
        with open(model_local_path, "rb") as f:
            # Upload the model to the s3 bucket of the company
            kwargs = {"query_params": {"model_version": model_version}} if model_version is not None else {}
            signed_url_upload_request = self.raw_api.get_model_signed_url_for_upload(
                path_params={"model_name": model_name},
                **kwargs,
            )
            upload_request_parameters = signed_url_upload_request.body["data"]
            requests.post(upload_request_parameters["url"], data=[])
            self._logger.info("Uploading the model file...")
            files = {"file": (upload_request_parameters["fields"]["key"], f)}
            http_response = requests.post(
                upload_request_parameters["url"],
                data=upload_request_parameters["fields"],
                files=files,
            )
            # Getting the s3 created Etag from the http headers, and passing it to the 'add_model' call
            s3_file_etag = http_response.headers.get("ETag")  # Verify the model was uploaded
            http_response.raise_for_status()
            self._logger.info("Finished uploading the model file.")
            return s3_file_etag

    # TODO: Make the above method to use the one that follows. Ensure good naming conventions.
    @staticmethod
    def upload_file_to_s3(from_path: str, s3_signed_url: S3SignedUrl) -> Response:
        with open(from_path, "rb") as file:
            files = {"file": (s3_signed_url.fields["key"], file)}
            http_response = requests.post(s3_signed_url.url, files=files, data=s3_signed_url.fields)
            return http_response

    def register_experiment(self, name: str, model_name: "Optional[str]" = None, resume: bool = True) -> None:
        """
        Registers a training experiment in Deci's backend

        :param name: The experiment name
        :param model_name: The model name that being run in the experiment. Optional.
        :param resume: Resume the experiment `name` by uploading files to the existing experiment folder alongside any existing files.
                       If `resume=False` - archive all previously existing experiment `name` files. True by default.
        """
        try:
            response = self.raw_api.start_experiment(
                body=ExperimentForm(name=name, model_name=model_name, resume=resume),
            )
            self.experiment = response.body["data"]
        except Exception:
            self._logger.exception(f"Failed to register experiment {name}")

    def save_experiment_file(self, file_path: str) -> "threading.Thread":
        """
        Uploads a training related file to Deci's location in S3. This can be a TensorBoard file or a log

        :param file_path: The local path of the file to be uploaded
        """

        def save(path: str, existing_thread: "Optional[threading.Thread]") -> None:
            # If there's already an upload schedule for the same file kill it
            if existing_thread:
                self._logger.debug("There's already a thread trying to upload the same filename")
                existing_thread.join()
                self._logger.debug("Old thread finished. We'll create a new one")

            if not os.path.exists(path):
                self._logger.warning("We didn't find that file")
                return

            try:
                filename = os.path.basename(file_path)
                query_params = {"filename": filename}
                response = self.raw_api.get_experiment_upload_url(
                    path_params={"experiment_id": self.experiment["id"]},
                    query_params=query_params,
                )
            except Exception:
                self._logger.exception("We couldn't fetch an upload URL from the server")
                return

            try:
                s3_target = S3SignedUrl(**response.body["data"])
                upload_response = self.upload_file_to_s3(from_path=file_path, s3_signed_url=s3_target)
                upload_response.raise_for_status()
            except Exception:
                self._logger.exception("We couldn't upload your file")

        file_absolute_path = str(Path(file_path).resolve())
        current_thread = self.experiments_pool.get(file_absolute_path)

        save_file_thread = threading.Thread(target=save, args=(file_absolute_path, current_thread))
        self.experiments_pool[file_absolute_path] = save_file_thread

        save_file_thread.start()
        return save_file_thread

    def get_model(
        self,
        name: "str",
        version: "Optional[str]" = None,
        download_path: "Optional[str]" = None,
        should_download: bool = True,
    ) -> "tuple[BaselineModelResponseMetadata, Optional[Path]]":
        """Get a model from the user's model repository in Lab tab, and optionally downloads the model file to the local machine.

        Args:
            name: Name of the model to retrieve from the lab
            version: Version of the model to retrieve from the lab (the version is specified near the model name). If not supplied, just the name will be used for fetching the model
            download_path: An optional download path to download the model to, if not supplied and should_download is set to `True`, will download to the current working directory
            should_download: A flag to indicate whether to download the model's file locally

        Returns:
            A tuple containing the model metadata and the download path (or None, if not downloaded) for the location of the model in the local machine
        """

        response = self.raw_api.get_model_by_name(
            path_params={"name": name},
            query_params={"version": version} if version is not None else {},
        )
        model_metadata = response.body["data"]
        if should_download:
            download_path = self.download_model(model_id=model_metadata["modelId"], dest_path=download_path)
        return model_metadata, download_path

    def request_benchmark(
        self,
        model_path: "Union[Path, str]",
        hardware_type: "Hardware",
        model_name: "Optional[str]" = None,
        batch_size: int = 1,
        quantization_level: "QuantizationLevel" = QuantizationLevel.FP16,
        source_framework: "Union[FrameworkType.TF2, FrameworkType.KERAS, FrameworkType.ONNX]" = FrameworkType.ONNX,
        should_convert: bool = True,
        autonac_run_id: "Optional[Union[UUID, str]]" = None,
    ) -> "UUID":
        """
        This method is used to request a benchmark of a model on a specified hardware with or without conversion.
        This should be used with the complimentary `get_benchmark_result` and `wait_for_benchmark_result` methods.
        :param model_path: The path of the model to be benchmarked
        :param hardware_type: Hardware type to benchmark the model on
        :param model_name: Optional name of the model to be benchmarked
        :param batch_size: Batch size to benchmark the model on
        :param quantization_level: Quantization level to benchmark the model on
        :param source_framework: The source framework of the model
        :param should_convert: Whether to convert the model to the target hardware before benchmarking
        :param autonac_run_id: Optional - pass to schedule optimizations on machines utilizing the TRT timing-cache
        :return: UUID representing the benchmark request
        :throws: BenchmarkRequestError if the benchmark request could not be created
        """
        model_name = model_name or Path(model_path).stem
        try:
            model_id = self.register_model(
                model=model_path,
                name=str(uuid4()),
                primary_batch_size=batch_size,
                architecture=model_name,
                description=f"Benchmark request on model: {model_path}",
                framework=source_framework,
                quantization_level=QuantizationLevel.FP32 if should_convert else quantization_level,
                hardware_types=[hardware_type],
            )
            if not should_convert:
                self.send_model_benchmark_request(
                    model_id=model_id,
                    batch_sizes=[batch_size],
                    hardware_types=[hardware_type],
                )
                return model_id
            optimize_model_ids = self.optimize_model(
                model_id,
                hardware_types=[hardware_type],
                batch_size=batch_size,
                quantization_level=quantization_level,
                autonac_run_id=autonac_run_id,
            )
            return optimize_model_ids[0]
        except Exception as ex:
            msg = f"{ex}: Could not upload or benchmark model {model_name}!"
            self._logger.error(msg)
            raise BenchmarkRequestError(error_message=msg) from ex

    def get_benchmark_result(self, model_id: str) -> "ModelBenchmarkResultMetadata":
        """
        Get a benchmark result on the primary hardware of a model by a model ID or by job_id generated by the `request_benchmark` method.
        :param model_id: The ID of the model to retrieve its results or the job id generated by the `request_benchmark` method
        :return: ModelBenchmarkResultMetadata of the result, the error field will be set if there was an error while benchmarking the model
        :throws: BenchmarkResultNotFoundException if the benchmark result could not be found
        """
        try:
            response = self.raw_api.get_model_by_id(path_params={"model_id": model_id})
            if not response.body["success"]:
                raise AssertionError(f"Get model by ID failed with message: {response.body['message']}")
            model_metadata = response.body["data"]
        except Exception:
            self._logger.exception(f"Failed to get benchmark result for job {model_id}, model not found!")
            return ModelBenchmarkResultMetadata(error=f"Model with ID={model_id} not found!")
        if (
            "baselineModelId" in model_metadata
            and model_metadata.get("optimizationState") == ModelOptimizationState.FAILED
        ):
            return ModelBenchmarkResultMetadata(error=f"Model conversion failed on job {model_id}")
        if model_metadata.get("benchmarkState") == ModelBenchmarkState.FAILED:
            return ModelBenchmarkResultMetadata(error=f"Model benchmark failed on job {model_id}")

        if model_metadata["benchmark"].get(model_metadata["primaryHardware"]["name"]) is None:
            raise BenchmarkResultNotFoundException(job_id=model_id)
        try:
            benchmark_results_for_hw = next(
                benchmark_result
                for benchmark_result in model_metadata["benchmark"][model_metadata["primaryHardware"]["name"]]
                if benchmark_result.get("batchSize") == model_metadata["primaryBatchSize"]
                and "batchInfTime" in benchmark_result
            )
        except Exception as ex:
            raise BenchmarkResultNotFoundException(job_id=model_id) from ex

        return ModelBenchmarkResultMetadata(
            **{
                key: benchmark_results_for_hw[key]
                for key in benchmark_results_for_hw
                if benchmark_results_for_hw[key] is not None
            }
        )

    def wait_for_benchmark_result(self, model_id: str, timeout: int = -1) -> "ModelBenchmarkResultMetadata":
        """
        Waits for a benchmark result on the primary hardware of a given model to be available, and returns the result upon completion.
        :param model_id: The ID of the model to retrieve its results or the job id generated by the `request_benchmark` method
        :param timeout: The maximum amount of time to wait, in seconds, for the benchmark result to be available, defaults to -1 (wait forever)
        :return: ModelBenchmarkResultMetadata of the result, the error field will be set if there was an error while benchmarking the model
        :throws: BenchmarkResultNotFoundException if timeout has passed
        """
        start = default_timer()
        while timeout <= 0 or default_timer() - start < timeout:
            try:
                return self.get_benchmark_result(model_id=model_id)
            except BenchmarkResultNotFoundException:
                time.sleep(1)
        raise BenchmarkResultNotFoundException(job_id=model_id)

    def create_workspace(self, name: str, emails_to_add: "Optional[list[str]]" = None) -> "UUID":
        """
        Creates a new workspace
        :param name: The name of the workspace to create.
        :param emails_to_add: A list of emails to add to the workspace. Optional.
        """
        response = self.raw_api.create_workspace(body=WorkspaceForm(name=name))
        workspace_id = response.body["data"]["id"]
        if emails_to_add:
            for email in emails_to_add:
                self.raw_api.invite_colleague_to_join_workspace(
                    body=InviteColleagueWithWorkspace(
                        invitedEmail=email,
                        workspaceId=workspace_id,
                    ),
                )
        self.api_client.refresh_frontegg_auth()
        return UUID(workspace_id)

    def delete_workspace(self, workspace_id: "Union[UUID, str]") -> None:
        """
        Deletes a workspace
        :param workspace_id: The ID of the workspace to delete.
        """
        self.raw_api.delete_workspace(path_params={"id": workspace_id})
        self.api_client.refresh_frontegg_auth()

    def edit_model(
        self,
        model_id: "Union[UUID, str]",
        *,
        name: "Optional[str]" = None,
        description: "Optional[str]" = None,
        dl_task: "Optional[DeepLearningTask]" = None,
        primary_batch_size: "Optional[BatchSize]" = None,
        primary_hardware: "Optional[Hardware]" = None,
        accuracy_metrics: "Optional[list[AccuracyMetric]]" = None,
        input_dimensions: "Optional[Sequence[Sequence[int]]]" = None,
    ) -> None:
        """
        Edits a model
        :param model_id: The ID of the model to edit.
        :param name: The name to set for the model. Optional.
        :param description: The description to set for the model. Optional.
        :param dl_task: The deep learning task to set for the model. Optional.
        :param primary_batch_size: The primary batch size to set for the model. Optional.
        :param primary_hardware: The primary hardware to set for the model. Optional.
        :param accuracy_metrics: The accuracy metrics to set for the model. Optional.
        :param input_dimensions: The input dimensions to set for the model. Optional.
        """
        if not any(
            [name, description, dl_task, primary_batch_size, primary_hardware, accuracy_metrics, input_dimensions]
        ):
            raise ValueError(
                "At least one of name, description, dl_task, primary_batch_size, primary_hardware,"
                " accuracy_metrics, or input_dimensions must be provided."
            )
        edit_model_form = {}
        if name is not None:
            edit_model_form["name"] = name
        if description is not None:
            edit_model_form["description"] = description
        if dl_task is not None:
            edit_model_form["dlTask"] = dl_task
        if primary_batch_size is not None:
            edit_model_form["primaryBatchSize"] = primary_batch_size
        if primary_hardware is not None:
            edit_model_form["primaryHardware"] = primary_hardware
        if accuracy_metrics is not None:
            edit_model_form["accuracyMetrics"] = accuracy_metrics
        if input_dimensions is not None:
            edit_model_form["inputDimensions"] = input_dimensions
        self.raw_api.edit_model(
            body=EditModelForm(**edit_model_form),
            path_params={"model_id": model_id},
        )

    def get_all_models(
        self,
        reorder: bool = False,
        with_deleted: bool = False,
        ids: "Optional[list[Union[str,  UUID]]]" = None,
    ) -> "list[ModelMetadata]":
        """Gets all models in the user's model repository.

        Args:
            reorder: Whether to reorder the models in the response, placing optimized models in an array on their baseline model.
            with_deleted: Whether to include deleted models in the response.
            ids: Optional list of model ids to query the models metadata for. If not given all will be fetched.

        Returns:
            A list containing model metadata for all models in the user's model repository.
        """
        query_params = {}
        if ids is not None:
            query_params["ids"] = [str(model_id) for model_id in ids]
        if reorder:
            query_params["reorder"] = True
        if with_deleted:
            query_params["with_deleted"] = True
        response = self.raw_api.get_all_models(query_params=query_params)
        return response.body["data"]

    def get_model_by_id(self, model_id: "Union[UUID, str]") -> "ModelMetadata":
        """Gets a model metadata from the user's model repository by ID

        Args:
            model_id: The ID of the model to retrieve

        Returns:
            Metadata for the given model
        """

        response = self.raw_api.get_model_by_id(path_params={"model_id": model_id})
        return response.body["data"]

    def switch_to_workspace(self, workspace_id: "Union[UUID, str]") -> None:
        """
        Switches to a workspace
        :param workspace_id: The ID of the workspace to switch to.
        """
        self.api_client.set_up_workspace_id(workspace_id=workspace_id)
        self._logger.info(f"Switched to workspace {workspace_id}")

    def optimize_model(
        self,
        model_id: "Union[UUID, str]",
        *,
        hardware_types: "Optional[list[Hardware]]" = None,
        batch_size: int = 1,
        quantization_level: "QuantizationLevel" = QuantizationLevel.FP16,
        infery_pkl_format: bool = True,
        conversion_parameters: "Optional[dict[str, Any]]" = None,
        name: "Optional[str]" = None,
        target_metric: "Metric" = Metric.LATENCY,
        autonac_run_id: "Optional[Union[UUID, str]]" = None,
    ) -> "list[UUID]":
        """Optimizes a model to a specific hardware type(s).

        Args:
            model_id: The ID of the model to optimize.
            hardware_types: The types of hardware to optimize for. Defaults to T4.
            batch_size: The batch size to optimize for. Defaults to 1.
            quantization_level: The quantization level to optimize for. We currently fully support `FP32` and `FP16` quantization levels.
                We also have a support for `INT8` quantization level without calibration, that is used only to measure the performance of the model.
                In order to fully optimize your model using `INT8` quantization, you must calibrate your model. To learn more, refer to [SuperGradients Quantization Tutorial](https://docs.deci.ai/super-gradients/documentation/source/ptq_qat.html)
            infery_pkl_format: Whether to use infery pickle format. If set to `False`, the optimization process will result in an `.engine` file for TensorRT  or `.zip` file that contains the relevant `.xml` and `.bin` files for OpenVINO.
            conversion_parameters: Additional conversion parameters, to be used when optimizing the model.
            autonac_run_id: Optional - pass to schedule optimizations on machines utilizing the TRT timing-cache

                For example, when converting a model that has fully dynamic axes, this parameter should be used to specify the ranges for all of those axes with `[min, opt, max]` values: `{"axis_ranges": {"batch_size": [1, 2, 4], "sequence": [1, 64, 128]}}`
            name: The name to set for the optimized model. Will use a default naming convention if `None` is supplied.
            target_metric: The target metric to optimize for.

        Returns:
            A list of model IDs representing the optimized models.
        """
        gru_request_form = build_gru_request_form(
            batch_size=batch_size,
            quantization_level=quantization_level,
            target_hardware_types=hardware_types,
            raw_format=not infery_pkl_format,
            target_metric=target_metric,
            name=name,
            conversion_parameters=conversion_parameters,
            autonac_run_id=autonac_run_id,
        )
        response = self.raw_api.gru_model(body=gru_request_form, path_params={"model_id": model_id})
        return response.body["data"]["optimizedModelIds"]

    def autonac_model(self, model_id: "Union[UUID, str]") -> "UUID":
        """Creates a request for running AutoNAC on an existing model.

        Args:
            model_id: The ID of the model to run AutoNAC on

        Returns:
            The ID of the model that will be generated by AutoNAC
        """
        response = self.raw_api.autonac_model(path_params={"model_id": model_id})
        return response.body["data"]["optimizedModelId"]

    def get_autonac_model_file_link(
        self,
        *,
        model_name: str,
        file_name: "AutoNACFileName",
        super_gradients_version: "Optional[str]" = None,
    ) -> "tuple[str, Optional[str]]":
        response = self.raw_api.get_autonac_model_file_link(
            path_params={"model_name": model_name, "file_name": file_name},
            query_params={"super_gradients_version": super_gradients_version} if super_gradients_version else {},
        )
        return response.body["data"], response.response.headers.get("etag")

    def register_user_architecture(self, name: str) -> "UserArchitecture":
        response = self.raw_api.register_user_architecture(
            body=BodyRegisterUserArchitecture(architecture_name=name),
        )
        return response.body

    def upload_log_url(self, *, tag: str, level: "SentryLevel") -> "dict[str, Any]":
        response = self.raw_api.upload_log_url(query_params={"tag": tag, "level": level})
        return response.body["data"]

    def send_model_benchmark_request(
        self,
        model_id: "Union[str, UUID]",
        batch_sizes: "list[int]",
        hardware_types: "list[Hardware]",
    ) -> None:
        self.raw_api.send_model_benchmark_request(
            path_params={"model_id": model_id},
            body=BodySendModelBenchmarkRequest(batch_sizes=batch_sizes, hardwares=hardware_types),
        )

    def benchmark_model(
        self,
        model_id: "Union[str, UUID]",
        batch_sizes: "list[int]",
        hardware_types: "list[Hardware]",
    ) -> None:
        """Benchmark a model on given batch sizes and hardware types.

        Args:
            model_id: The ID of the model to benchmark
            batch_sizes: A list of batch sizes to benchmark for
            hardware_types: A list of hardware types to benchmark for
        """
        self.send_model_benchmark_request(model_id=model_id, batch_sizes=batch_sizes, hardware_types=hardware_types)

    def start_autonac_run(
        self, *, hardware: "Hardware", number_of_machines: int, duration_seconds: "Optional[int]" = None
    ) -> "UUID":
        """
        Create an Autonac Run: Keep a requested number of machines up for the requested hardware and duration.
        Use this to take advantage of the TensorRT Timing Cache on Nvidia Cloud machines.

        Args:
            hardware: Hardware the run will be conducted on.
            number_of_machines: Number of machines (of the given hardware) to keep up during the run, until the run is complete.
            duration_seconds: Optional - Number of **seconds** the machines will remain up. Default: 3 days.

        Returns:
            UUID of the Autonac Run.

            * Pass to `client.request_benchmark` to schedule optimizations on the perpetually running machines.

            * Pass to `client.complete_autonac_run` to complete the run and kill the machines.
        """
        response = self.raw_api.start_autonac_run(
            body=StartAutonacRun(
                hardware=hardware, n_machines_always_up=number_of_machines, duration_seconds=duration_seconds
            )
        )

        return response.body.autonac_run_id

    def complete_autonac_run(self, autonac_run_id: "Union[UUID, str]") -> None:
        """
        Args:
            autonac_run_id: Autonac Run to complete.
        """
        self.raw_api.complete_autonac_run({"autonac_run_id": autonac_run_id})

    def get_infery_license_expiration_time(self) -> "datetime":
        response = self.raw_api.get_license_expiration()
        return datetime.fromisoformat(response.body)

    def _current_workspace(self) -> "WorkspaceBase":
        return self.raw_api.get_workspace_by_id({"id": self.api_client.workspace_id}).body["data"]

    def get_artifactory_token(self) -> "Optional[str]":
        """Get the optional Artifactory Token for the current workspace.
        Returns:
             Artifactory Token for the current workspace if present, otherwise `None`.
        """
        return self._current_workspace().get("artifactoryToken")
