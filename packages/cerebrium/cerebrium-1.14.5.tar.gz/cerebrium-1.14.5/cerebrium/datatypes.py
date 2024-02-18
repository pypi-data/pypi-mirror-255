import enum
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Union

MAX_MEMORY = 256
MAX_GPU_COUNT = 8
MAX_CPU = 48

MIN_CPU = 1
MIN_MEMORY = 2

DEFAULT_COOLDOWN = 60
DEFAULT_CPU = 2
DEFAULT_MEMORY = 16
DEFAULT_MIN_REPLICAS = 0
DEFAULT_MAX_REPLICAS = 5
DEFAULT_GPU_SELECTION = "AMPERE_A5000"
DEFAULT_PYTHON_VERSION = "3.11"
DEFAULT_GPU_COUNT = 1
DEFAULT_CUDA_VERSION = "12"

DEFAULT_INCLUDE = "[./*, main.py]"
DEFAULT_EXCLUDE = "[./.*, ./__*]"

INTERNAL_FILES = [
    "requirements.txt",
    "pkglist.txt",
    "conda_pkglist.txt",
    "_cerebrium_predict.json",
]

# TODO @Katsie011: Extract constants to a separate file


PythonVersionType = Literal["3.9", "3.10", "3.11"]
LogLevelType = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


class PythonVersion(enum.Enum):
    PYTHON_3_9 = "3.9"
    PYTHON_3_10 = "3.10"
    PYTHON_3_11 = "3.11"


class OperationType(enum.Enum):
    DEPLOY = "deploy"
    RUN = "run"


##These are hardware options from compute providers
@dataclass
class Hardware:
    def __init__(
        self,
        name: str,
        VRAM: int,
        gpu_model: str,
        max_memory: float = 128.0,
        max_cpu: int = 36,
        max_gpu_count: int = MAX_GPU_COUNT,
        has_nvlink: bool = False,
    ):
        self.name = name
        self.gpu_model = gpu_model
        self.max_memory = max_memory
        self.max_cpu = max_cpu
        self.max_gpu_count = max_gpu_count
        self.VRAM = VRAM
        self.has_nvlink = has_nvlink

    def validate(self, cpu: int, memory: float, gpu_count: int) -> str:
        if not all(
            isinstance(i, (int, float)) and i >= 0 for i in [cpu, memory, gpu_count]
        ):
            raise TypeError("CPU, memory, and GPU count must be positive numbers.")

        message = ""
        if cpu > self.max_cpu:
            message += f"CPU must be at most {self.max_cpu} for {self.name}.\n"
        if cpu < MIN_CPU:
            message += f"CPU must be at least {MIN_CPU} for {self.name}.\n"
        if memory > self.max_memory:
            message += f"Memory must be at most {self.max_memory} GB for {self.name}.\n"
        if memory < MIN_MEMORY:
            message += f"Memory must be at least {MIN_MEMORY} GB for {self.name}.\n"
        if gpu_count > self.max_gpu_count:
            message += f"Number of GPUs must be at most {self.max_gpu_count} for {self.name}.\n"
        if gpu_count < 1:
            message += f"Number of GPUs must be at least 1 for {self.name}.\n"

        return message

    def __str__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=False)


class HardwareOptions:
    GPU: Hardware = Hardware(
        name="TURING_4000",
        max_memory=256.0,
        max_cpu=48,
        VRAM=8,
        gpu_model="Quadro RTX 4000",
    )
    TURING_4000: Hardware = Hardware(
        name="TURING_4000",
        max_memory=256.0,
        max_cpu=48,
        VRAM=8,
        gpu_model="Quadro RTX 4000",
    )
    TURING_5000: Hardware = Hardware(
        name="TURING_5000", max_memory=256.0, max_cpu=48, VRAM=8, gpu_model="RTX 5000"
    )
    AMPERE_A4000: Hardware = Hardware(
        name="AMPERE_A4000",
        max_memory=256.0,
        max_cpu=48,
        VRAM=16,
        gpu_model="RTX A4000",
    )
    AMPERE_A5000: Hardware = Hardware(
        name="AMPERE_A5000",
        max_memory=256.0,
        max_cpu=48,
        VRAM=24,
        gpu_model="RTX A5000",
    )
    AMPERE_A6000: Hardware = Hardware(
        name="AMPERE_A6000",
        max_memory=256.0,
        max_cpu=48,
        VRAM=48,
        gpu_model="RTX A6000",
    )
    AMPERE_A100: Hardware = Hardware(
        name="AMPERE_A100",
        max_memory=256.0,
        max_cpu=48,
        VRAM=80,
        has_nvlink=True,
        gpu_model="A100",
    )
    AMPERE_A100_40GB: Hardware = Hardware(
        name="AMPERE_A100_40GB",
        max_memory=256.0,
        max_cpu=48,
        VRAM=40,
        has_nvlink=True,
        gpu_model="A100 40GB",
    )

    @classmethod
    def available_hardware(cls):
        return list(cls.__annotations__.keys())


class CerebriumScaling:
    def __init__(
        self,
        min_replicas: int = DEFAULT_MIN_REPLICAS,
        max_replicas: int = DEFAULT_MAX_REPLICAS,
        cooldown: int = DEFAULT_COOLDOWN,
    ):
        self.validate(min_replicas, max_replicas, cooldown)
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.cooldown = cooldown

    def validate(self, min_replicas: int, max_replicas: int, cooldown: int):
        if not all(x >= 0 for x in [min_replicas, cooldown]):
            raise ValueError(
                "Min replicas, cooldown, and max replicas must be positive integers"
            )
        if max_replicas < 1:
            raise ValueError("Max replicas must be at least 1.")
        if min_replicas > max_replicas:
            raise ValueError("Max replicas must be larger than min replicas.")

    def __str__(self):
        return json.dumps(self.__to_dict__(), indent=4, sort_keys=False)

    def __to_dict__(self):
        return self.__dict__

    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)


class CerebriumBuild:
    def __init__(
        self,
        predict_data: Union[str, None] = None,
        force_rebuild: bool = False,
        hide_public_endpoint: bool = False,
        disable_animation: bool = False,
        disable_build_logs: bool = False,
        disable_syntax_check: bool = False,
        disable_predict: bool = False,
        disable_confirmation: bool = False,
        init_debug: bool = False,
        log_level: LogLevelType = "INFO",
    ):
        self.predict_data = predict_data
        self.force_rebuild = force_rebuild
        self.hide_public_endpoint = hide_public_endpoint
        self.disable_animation = disable_animation
        self.disable_build_logs = disable_build_logs
        self.disable_syntax_check = disable_syntax_check
        self.disable_predict = disable_predict
        self.init_debug = init_debug
        self.log_level = log_level
        self.disable_confirmation = disable_confirmation

    def __str__(self):
        return json.dumps(self.__to_dict__(), indent=4, sort_keys=False)

    def __to_dict__(self):
        return self.__dict__

    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)


class CerebriumDeployment:
    def __init__(
        self,
        name: str = "cerebrium-model",
        python_version: PythonVersionType = "3.10",
        include: str = DEFAULT_INCLUDE,
        exclude: str = DEFAULT_EXCLUDE,
        cuda_version: str = DEFAULT_CUDA_VERSION,
    ):
        self.name = self.validate_name(name)
        self.python_version = python_version
        self.include = include
        self.exclude = exclude
        self.cuda_version = str(cuda_version)  # Avoids accidental int or float

    def validate_name(self, name: str, env: str = "prod") -> str:
        if not name:
            raise ValueError("No name provided.")
        max_length = 32 if env == "prod" else 63 - 28 - 2 * len(env)
        if len(name) > max_length:
            raise ValueError(f"Name must be at most {max_length} characters.")
        if not re.match("^[a-z0-9\\-]*$", name):
            raise ValueError(
                "Name must only contain lower case letters, numbers, and dashes."
            )
        return name

    def __str__(self):
        return json.dumps(self.__to_dict__(), indent=4, sort_keys=False)

    def __to_dict__(self):
        return self.__dict__

    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)


class CerebriumHardware:
    def __init__(
        self,
        gpu: str = "AMPERE_A5000",
        cpu: int = DEFAULT_CPU,
        memory: float = DEFAULT_MEMORY,
        gpu_count: int = DEFAULT_GPU_COUNT,
    ):
        try:
            gpuOption = getattr(HardwareOptions, gpu.upper())
        except AttributeError:
            available_gpus = ", ".join(HardwareOptions.available_hardware())
            raise ValueError(
                f"{gpu.upper()} is not a valid GPU option. Available options are: {available_gpus}"
            )
        self.validate(gpuOption, cpu, memory, gpu_count)
        self.gpu = gpu.upper()
        self.cpu = cpu
        self.memory = memory
        self.gpu_count = gpu_count

    def validate(self, gpu: Hardware, cpu: int, memory: float, gpu_count: int):
        if not all(x > 0 for x in [cpu, memory, gpu_count]):
            raise ValueError("CPU, memory, and GPU count must be positive values.")

        if cpu < MIN_CPU:
            raise ValueError(f"CPU must be at least {MIN_CPU}.")

        if memory < MIN_MEMORY:
            raise ValueError(f"Memory must be at least {MIN_MEMORY} GB.")

        if cpu > gpu.max_cpu:
            raise ValueError(
                f"CPU must be <= {gpu.max_cpu} for the selected hardware option."
            )

        if gpu_count > MAX_GPU_COUNT:
            raise ValueError(f"GPU count must be <= {MAX_GPU_COUNT}.")

        if memory > gpu.max_memory:
            raise ValueError(
                f"Memory must be <= {gpu.max_memory} GB for the selected hardware option."
            )

    def __str__(self):
        return json.dumps(self.__to_dict__(), indent=4, sort_keys=False)

    def __to_dict__(self):
        return self.__dict__

    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)


class CerebriumDependencies:
    def __init__(
        self,
        pip: Dict[str, str] = {},
        conda: Dict[str, str] = {},
        apt: List[str] = [],
    ):
        self.pip = pip
        self.conda = conda
        self.apt = apt

    def __str__(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=False)

    def to_dict(self):
        return self.__dict__


class CerebriumConfig:
    def __init__(
        self,
        scaling: CerebriumScaling = CerebriumScaling(),
        build: CerebriumBuild = CerebriumBuild(),
        deployment: CerebriumDeployment = CerebriumDeployment(),
        hardware: CerebriumHardware = CerebriumHardware(),
        dependencies: CerebriumDependencies = CerebriumDependencies(),
        local_files: List[Dict[str, str]] = [],
        cerebrium_version: str = "",
        partial_upload: bool = False,
        file_list: List[str] = [],
    ):
        self.scaling = scaling
        self.build = build
        self.deployment = deployment
        self.hardware = hardware
        self.dependencies = dependencies
        self.local_files = local_files
        self.cerebrium_version = cerebrium_version
        self.partial_upload = partial_upload
        self.file_list = file_list

    def get(self, key: str, default: Any = None):
        return self.__dict__.get(key, default)

    def __str__(self):
        # Convert to dict. All the nested classes need to be converted to dict
        # before converting to string
        dictified = self.to_dict()
        return json.dumps(dictified, indent=4, sort_keys=False)

    def to_dict(self):
        dictified = self.__dict__.copy()
        for key, value in dictified.items():
            if hasattr(value, "__dict__"):
                dictified[key] = value.__dict__
        return dictified

    def __to_json__(self):
        return json.dumps(self.to_dict())
