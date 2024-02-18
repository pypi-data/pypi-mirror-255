class DownloadModelError(Exception):
    pass


class PyTorchNotInstalledError(Exception):
    def __init__(self):
        super(PyTorchNotInstalledError, self).__init__(
            "Could not `import torch`, please install PyTorch before running this method"
        )


class UnsupportedLoadedModelFramework(Exception):
    def __init__(self):
        super(UnsupportedLoadedModelFramework, self).__init__(
            "local_loaded_model is only supported for Pytorch models at the moment."
            " Please specify a model_local_path instead"
        )


class BenchmarkRequestError(Exception):
    def __init__(self, error_message: str):
        super(BenchmarkRequestError, self).__init__(error_message)


class BenchmarkResultNotFoundException(Exception):
    def __init__(self, job_id: str):
        super(BenchmarkResultNotFoundException, self).__init__(f"Benchmark results were not found for job {job_id}")
