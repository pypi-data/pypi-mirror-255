import dataclasses
import logging
import statistics
import time
import typing
import onnxruntime
import torch.utils.data
import irisml.core
from irisml.tasks.train.build_dataloader import build_dataloader

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Bencharmk a given onnx model using onnxruntime.

    Inference will be repeated for num_iterations times. Then, the average will be calculated excluding the result of the first iteration.

    Config:
        batch_size (int): The batch size. To use arbitrary batch_size, the onnx model must be exported with dynamic axes.
        device ('cpu' or 'cuda'): The device to run onnxruntime.
        num_iterations (int): The number of iterations to run.
        verbose (bool): Show verbose level logging
    """
    VERSION = '0.1.3'
    CACHE_ENABLED = False

    @dataclasses.dataclass
    class Inputs:
        onnx_model_bytes: bytes
        dataset: torch.utils.data.Dataset
        transform: typing.Callable

    @dataclasses.dataclass
    class Config:
        batch_size: int = 1
        device: typing.Optional[typing.Literal['cpu', 'cuda']] = None
        num_iterations: int = 10
        verbose: bool = False

    @dataclasses.dataclass
    class Outputs:
        prediction_time_per_iteration: float = 0.0

    def execute(self, inputs):
        providers = ['CPUExecutionProvider'] if self.config.device == 'cpu' else ['CUDAExecutionProvider', 'CPUExecutionProvider']

        if not set(providers) <= set(onnxruntime.get_available_providers()):
            raise RuntimeError(f"The current environment supports only {onnxruntime.get_available_providers()}. Expected {providers}")

        if self.config.device == 'cuda' and onnxruntime.get_device() != 'GPU':
            raise RuntimeError(f"CUDA benchmark is requested, but the current device is {onnxruntime.get_device()}")

        logger.debug(f"Running benchmark with {providers=}")

        options = onnxruntime.SessionOptions()
        if self.config.verbose:
            options.log_severity_level = 2

        session = onnxruntime.InferenceSession(inputs.onnx_model_bytes, options, providers=providers)
        model_inputs = session.get_inputs()
        model_outputs = session.get_outputs()

        if len(model_inputs) != 1:
            raise ValueError(f"This task supports only 1-input models. Found {model_inputs=}")

        if not model_outputs:
            raise ValueError("The ONNX model has to have at least one output.")

        dataloader = build_dataloader(inputs.dataset, inputs.transform, batch_size=self.config.batch_size, shuffle=False, drop_last=True)
        prediction_time_all = []
        for i, batch in enumerate(dataloader):
            input_array = batch[0].numpy()
            start = time.time()
            session.run([model_outputs[0].name], {model_inputs[0].name: input_array})
            prediction_time = time.time() - start
            prediction_time_all.append(prediction_time)
            if i >= self.config.num_iterations:
                break

        if len(prediction_time_all) < self.config.num_iterations:
            logger.info(f"The dataset is smaller than expected. The actual number of iteration is {len(prediction_time_all)}")

        prediction_time_per_iteration = self._mean_without_first_sample(prediction_time_all)

        logger.debug(f"{prediction_time_all=}")
        logger.info(f"{prediction_time_per_iteration=}")
        return self.Outputs(prediction_time_per_iteration)

    @staticmethod
    def _mean_without_first_sample(values):
        # Since the first run requires initialization and weights transfer, it is usually slow. We exlucde it from calculating the average.
        return statistics.fmean(values[1:] if len(values) > 1 else values)
