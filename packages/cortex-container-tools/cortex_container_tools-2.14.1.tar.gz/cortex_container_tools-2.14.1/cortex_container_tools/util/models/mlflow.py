from ._model import LoadableModel


import os

import cloudpickle
import pkg_resources


# External Libraries
from collections import namedtuple
from mlflow.models import Model, ModelSignature, ModelInputExample
from mlflow.models.model import MLMODEL_FILE_NAME

from mlflow.pyfunc import PythonModel

from mlflow.models.utils import _save_example
from mlflow.utils.environment import (
    _validate_env_arguments,
)

from mlflow.utils.model_utils import (
    _add_code_from_conf_to_system_path,
    _validate_and_prepare_target_save_path,
)

from mlflow.utils import (
    PYTHON_VERSION,
    get_major_minor_py_version,
)

from mlflow.protos.databricks_pb2 import (
    INVALID_PARAMETER_VALUE,
)

from mlflow.exceptions import MlflowException

from mlflow.utils.file_utils import TempDir, _copy_file_or_tree

def _warn_potentially_incompatible_py_version_if_necessary(model_py_version=None):
    """
    Compares the version of Python that was used to save a given model with the version
    of Python that is currently running. If a major or minor version difference is detected,
    logs an appropriate warning.
    """
    if model_py_version is None:
        _logger.warning(
            "The specified model does not have a specified Python version. It may be"
            " incompatible with the version of Python that is currently running: Python %s",
            PYTHON_VERSION,
        )

    elif get_major_minor_py_version(model_py_version) != get_major_minor_py_version(PYTHON_VERSION):
        _logger.warning(
            "The version of Python that the model was saved in, `Python %s`, differs"
            " from the version of Python that is currently running, `Python %s`,"
            " and may be incompatible",
            model_py_version,
            PYTHON_VERSION,
        )


import logging
_logger = logging.getLogger(__name__)

PY_VERSION = 'python_version'
FLAVOR_VERSION = 'flavor_version'
FLAVOR_NAME = 'cortex_python_function'
CODE = 'code'
DATA = 'data'
ENV = 'env'
TRAINING_STEPS   = 'training_steps'
DEPLOYMENT_STEPS = 'deployment_steps'
CONFIG_KEY_PYTHON_MODEL = 'python_model'
CONFIG_KEY_CLOUDPICKLE_VERSION = 'cloudpickle_version'
PYFUNC_FLAVOR_NAME = 'python_function'

class MLflowModel(PythonModel):
    @staticmethod
    def save_model(
        path,
        code_path=None,
        conda_env=None,
        mlflow_model=None,
        python_model=None,
        signature: ModelSignature = None,
        input_example: ModelInputExample = None,
        pip_requirements=None,
        extra_pip_requirements=None,
        metadata=None,
        training_steps=None,
        deployment_steps=None,
        **kwargs,
    ):
        """
        Save a cortex model to a local file or a run.
        """
        
        _validate_env_arguments(conda_env, pip_requirements, extra_pip_requirements)

        mlflow_model = kwargs.pop('model', mlflow_model)
        if len(kwargs) > 0:
            raise TypeError(f'save_model() got unexpected keyword arguments: {kwargs}')
        if code_path is not None:
            if not isinstance(code_path, list):
                raise TypeError('Argument code_path should be a list, not {}'.format(type(code_path)))
        
        _validate_and_prepare_target_save_path(path)
        if mlflow_model is None:
            mlflow_model = Model()

        if signature is not None:
            mlflow_model.signature = signature

        if input_example is not None:
            _save_example(mlflow_model, input_example, path)

        if metadata is not None:
            mlflow_model.metadata = metadata


        # Custom PyFunc saving logic
        custom_model_config_kwargs = {
            CONFIG_KEY_CLOUDPICKLE_VERSION: cloudpickle.__version__,
            FLAVOR_VERSION: pkg_resources.get_distribution('cortex_cli').version,
            TRAINING_STEPS: training_steps,
            DEPLOYMENT_STEPS: deployment_steps,
        }

        if isinstance(python_model, PythonModel):
            saved_python_model_subpath = 'python_model.pkl'
            with open(os.path.join(path, saved_python_model_subpath), "wb") as out:
                cloudpickle.dump(python_model, out)
            custom_model_config_kwargs[CONFIG_KEY_PYTHON_MODEL] = saved_python_model_subpath
        else:
            raise MlflowException(
                message=(
                    '`python_model` must be a subclass of `PythonModel`. Instead, found an'
                    ' object of type: {python_model_type}'.format(python_model_type=type(python_model))
                ),
                error_code=INVALID_PARAMETER_VALUE,
            )
        
        saved_code_subpath = None
        if code_path is not None:
            saved_code_subpath = 'code'
            for code in code_path:
                _copy_file_or_tree(src=code, dst=path, dst_dir=saved_code_subpath)
        
        mlflow_model.add_flavor(
            FLAVOR_NAME,
            code=saved_code_subpath,
            env=conda_env,
            loader_module='cortex_container_tools.util.models.mlflow',
            python_version=PYTHON_VERSION,
            **custom_model_config_kwargs,
        )
        mlflow_model.add_flavor(
            PYFUNC_FLAVOR_NAME,
            loader_module='cortex_container_tools.util.models.mlflow',
            python_version=PYTHON_VERSION,
        )
        mlflow_model.save(os.path.join(path, MLMODEL_FILE_NAME))

    
    def from_file(self, path: str):
        # Return model if it's already been loaded
        if 'instance' in dir(self) and self.instance is not None:
            return self
        
        # Check if the model's been downloaded
        if not os.path.exists(path) or len(os.listdir(path)) <= 0:
            raise Exception('Missing model data')
        
        # Reads the MLmodel file
        model_metadata = Model.load(os.path.join(path, MLMODEL_FILE_NAME))
        model_config   = model_metadata.flavors.get(FLAVOR_NAME)
        if model_config is None:
            raise Exception('Model does not have the "{FLAVOR_NAME}" flavor')

        model_py_version = model_config.get(PY_VERSION)
        _warn_potentially_incompatible_py_version_if_necessary(model_py_version=model_py_version)
        _add_code_from_conf_to_system_path(path, model_config, code_key=CODE)
        
        python_model_subpath = model_config.get(CONFIG_KEY_PYTHON_MODEL)
        if python_model_subpath is None:
            raise Exception('Model config does not specify a model path')

        python_model = None
        with open(os.path.join(path, python_model_subpath), 'rb') as file:
            python_model = cloudpickle.load(file)
            
        Step             = namedtuple('Step', 'name type')
        deployment_steps = [Step(dict[list(dict.keys())[0]], list(dict.keys())[0]) for dict in model_config.get(DEPLOYMENT_STEPS)]

        for step in deployment_steps:
            if hasattr(python_model, step.type):
                _logger.info(f'Running step: {step.name} ({step.type})')
                function = getattr(python_model, step.type)
                if callable(function):
                    function()

        self.instance = python_model
        return self
