from collections import namedtuple, ChainMap
from datetime import datetime
from cortex_sdk.api.api_resource import api_key, api_url
import cortex_sdk
import yaml
import os, sys
import traceback
import importlib
from mlflow.models.signature import infer_signature
from .mlflow import MLflowModel

EthicsType   = namedtuple('BaseEthicsType', 'ethics_type_enum sensitive_predictor_columns label_column')
EthicsResult = namedtuple('BaseEthicsResult', 'ethics_type result_str risk')
DriftType    = namedtuple('BaseDriftType', 'drift_type_enum model_instance data_array')
DriftResult  = namedtuple('BaseDriftResult', 'drift_type result_str')

class Trainer():
    def __init__(self, use_tracking = True, pipeline_id = None, verbose = False):
        self._use_tracking  = use_tracking
        self._pipeline_id   = pipeline_id
        self._verbose       = verbose
        self._error_message = None
        self._success       = False

        #self.model = None
        
        #self._model_json = None
        #self._pipeline_json = None
        #self._requested_secrets = []

    def _get_git_repo_name(self, path: str):
        """
        Parses the repo name from a locally cloned git repository.

        Args:
            path (str):
            The file path of the locally cloned git repository.
        """
        with open(f'{path}/.git/config', 'r') as file:
            for line in file.readlines():
                if line.strip().startswith('url ='):
                    url  = line.split('=')[1].strip()
                    name = url.split('/')[-1]
                    
                    # Name will have .git at the end, chop it off for the repo
                    if name.endswith('.git'):
                        return name[:-4]
                    else:
                        return name
                    
    def _get_git_repo_branch(self, path: str):
        """
        Parses the branch name from a locally cloned git repository.

        Args:
            path (str):
            The file path of the locally cloned git repository.
        """
        with open(f'{path}/.git/HEAD', 'r') as file:
            # Line will be formatted like: "ref: refs/heads/main"
            # We want to parse out 'main' from that
            ref = file.read().split(' ')[1]
            return ref.split('/')[-1].strip() # Beware \n at the end

    def _get_git_repo_hash(self, path: str, branch: str):
        """
        Parses the hash from a locally cloned git repository.

        Args:
            path (str):
            The file path of the locally cloned git repository.
        """
        with open(f'{path}/.git/refs/heads/{branch}', 'r') as file:
            # File is just a hash of the commit we're on
            return file.read().strip() # Beware \n at the end
        
    def _load_cortex_yaml(self):
        """
        Loads a model's cortex.yaml file.
        """
        with open(os.path.join(self._path, 'cortex.yml'), 'r') as file:
            config = yaml.safe_load(file)

        output = {}

        Step      = namedtuple('Step', 'name type')
        steps_key = 'training_steps' if 'training_steps' in config.keys() else 'pipeline_steps'

        steps = {}
        for item in config[steps_key]:
            key, value = list(item.items())[0]
            steps[key] = value

        config['training_steps'] = steps

        config['modules'] = {}
        walk_path = '.'
        if 'module_path' in config.keys() and config['module_path'] is not None:
            config['module_path'] = os.path.join(self._path, f'{config["module_path"][2:]}')
            walk_path = config['module_path']
        for (root, dir_names, file_names) in os.walk(walk_path):
            file_names[:] = [
                f for f in file_names 
                if f.endswith('.py') and f not in ['__init__.py', '{}.py'.format(walk_path)] 
            ]
            # TODO: Set map of file path locations to module name
            for f in file_names:
                config['modules']['{}/{}'.format(root, f)] = f.replace('.py', '')

        return config


    def _get_model(self):
        try:
            self._repo_name   = self._get_git_repo_name(self._path)
            model = cortex_sdk.Models.get(repo_name = self._repo_name)[0]
            return {
                'model_id': model.id
            }
        except:
            return {
                'model_id': None
            }


    def _setup_pipeline(self):
        """
        Returns an existing pipeline, or creates a new one if required.
        """
        self._repo_branch = self._get_git_repo_branch(self._path)
        self._repo_hash   = self._get_git_repo_hash(self._path, self._repo_branch)

        if self._pipeline_id:
            pipeline_id = cortex_sdk.Pipelines.get(resource_id = self._pipeline_id).id

        else:
            pipeline_id = cortex_sdk.Pipelines.create(self._model_id, self._repo_branch, self._repo_hash).json()['_id']

        return {
            'pipeline_id': pipeline_id
        }

    
    def _initialize_steps(self, pipeline_id: str):
        # Add default initialize model and download data steps
        _steps = [
            {
                'name':   'Initialize model class',
                'type':   '_instantiate_model',
                'config': {
                    'cortex_cli_func': True
                }
            },
            {
                'name':   'Download model data',
                'type':   'download_data',
                'config': {}
            }
        ]

        for key, value in self._cortex_config['training_steps'].items():
            _steps.append({
                'name':   value,
                'type':   key,
                'config': {}
            })
        
        # Add default download data step
        _steps.append({
            'name':   'Cleanup model params',
            'type':   'cleanup_self',
            'config': {}
        })

        # Add default save pipeline artifacts step
        _steps.append({
            'name':   'Save pipeline artifacts',
            'type':   '_save_pipeline',
            'config': {
                'cortex_cli_func': True
            }
        })

        # Add default upload to cortex step
        _steps.append({
            'name':   'Upload pipeline artifacts',
            'type':   '_upload_pipeline',
            'config': {
                'cortex_cli_func': True,
                'requires_tracking': True
            }
        })
        
        if self._use_tracking:
            # Set cortex steps
            self._steps = cortex_sdk.Pipelines.create_steps(pipeline_id, _steps).json()
        else:
            # Set normal steps
            self._steps = _steps

        print('Loaded pipeline steps')
        
    def _complete_step(self, step, step_status, step_result, step_risk):
        return cortex_sdk.Steps.complete(
            pipeline_id = step['pipelineId'],
            step_id     = step['_id'],
            name        = step['name'],
            type        = step['type'],
            order       = step['order'],
            status      = step_status,
            message     = step_result,
            risk        = step_risk or None
        )
    
    def _complete_callback(self, current_stage, error_message = None):
        cortex_sdk.Pipelines.complete(
            pipeline_id   = self._pipeline_id,
            model_id      = self._model_id,
            current_stage = current_stage,
            message       = error_message
        )

    def _get_drift_inferences(self):
        cortex_sdk.Inferences.get_dri
        response = requests.get(
            url=f'{api_url()}/inferences?modelId={self._model_id}&hasTags[]=Drift Detection',
            headers=self._headers
        ).json()

        inferences = []
        if response and len(response['documents']) > 0:
            for inference in response['documents']:
                if inference['successful']:
                    inferences.append((inference['_id'], [inference['inputs']['ndarray'][0]], [inference['outputs']['ndarray'][0]]))

        return inferences
    
    def _run_pipeline(self, pipeline_id: str, model_id: str):
        return cortex_sdk.Pipelines.run(pipeline_id = pipeline_id, model_id = model_id)
    
    def _run_training_steps(self):
        current_step = None
        try:
            for step in self._steps:
                current_step = step['type']
                step_config  = step['config']
                step_func    = getattr(self if step_config.get('cortex_cli_func') else self.model, current_step)
                step_result  = None

                if self._verbose:
                    print(f'Running step: {step["name"]} ({current_step})')

                # Extract secrets from model if we are in cleanup step
                if current_step == 'cleanup_self':
                    # Check if secrets_manager exists
                    if hasattr(self.model, 'secrets_manager'):
                        self._requested_secrets = self.model.secrets_manager.secrets
                    else:
                        self._requested_secrets = []

                # Handle special case for passing testing inferences to test_predict function
                if current_step == 'detect_drift':
                    step_result = step_func(self._get_drift_inferences())
                else:
                    if (step_config.get('requires_tracking') and self._use_tracking) or (not step_config.get('requires_tracking')):
                        step_result = step_func()

                if self._use_tracking:
                    step_risk = ''

                    # Get ethics check results (if it exists)
                    step_result_type = type(step_result)
                    if step_result_type == EthicsResult:
                        # Parse out risk level
                        step_risk = step_result.risk.value

                        # Parse out result
                        step_result = step_result.result_str
                    elif step_result_type == DriftResult:
                        # Parse out result
                        step_result = step_result.result_str
                    elif step_result_type == str and self._verbose:
                        print(step_result)

                    self._complete_step(
                        step, 
                        'Successful',
                        step_result, 
                        step_risk
                    )

                print(f'{step["name"]} completed successfully')
            self._success = True
        except Exception as e:
            if self._use_tracking:
                self._complete_step(step, 'Failed', str(e), '')
            self._error_message = f'{step["name"]} completed with an error.\n{traceback.format_exc()}'
            raise Exception
    

    def get_model_params(self):
        if 'model_params' not in self.__dict__.keys():
            self.model_params = dict(ChainMap(*self._cortex_config['params'])) if self._cortex_config['params'] else {}

        return self.model_params


    def set_model_param(self, key, value):
        model_params = self.get_model_params()
        model_params[key] = value
        self.model_params = model_params

        return self.model_params


    def _instantiate_model(self):
        # LOAD DEPENDENCY MODULES (except model)
        for path, module in self._cortex_config['modules'].items():
            self._load_module(path, module)

        # LOAD MODEL MODULE
        if 'module_path' in self._cortex_config.keys() and self._cortex_config['module_path'] is not None:
            model_module = self._load_module(
                '{}/{}.py'.format(self._cortex_config['module_path'], self._cortex_config['model_module']),
                self._cortex_config['model_module']
            )
        else:
            model_module = self._load_module(
                '{}.py'.format(self._cortex_config['model_module']),
                self._cortex_config['model_module']
            )

        model_params = self.get_model_params()

        # Initialize safe local variables
        _model_id = None
        _api_key = None
        _api_url = None

        # Model id failsafe
        try:
            _model_id = self._model_id
        except Exception as e:
            print(f'Failed to get model ID. Using empty string instead.\n{e}')

        # NH API failsafe
        try:
            _api_url = api_url()
            _api_key = api_key()
        except Exception as e:
            print(f'Failed to get API url and key from environment variables. Using empty string instead.\n{e}')

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {_api_key}',
        }

        self.model = getattr(model_module, self._cortex_config['model_class'])(model_params, _model_id, _api_url, headers)

    def _load_module(self, module_path, module_name):
        print('\t\tLoading module {} from {}'.format(module_name, module_path))
        spec                     = importlib.util.spec_from_file_location(module_name, module_path)
        module                   = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    
    def _save_pipeline(self):
        print('Saving pipeline artifacts...')
        signature = infer_signature(self.model.input_example, self.model.output_example)

        # Save model
        modules = list(self._cortex_config['modules'].keys())
       # modules.append(self._cortex_config['model_module'])
        if self.model.model_type == 'cortex':
            MLflowModel.save_model(
                python_model     = self.model, 
                path             = self._artifacts_dir,                   # Where artifacts are stored locally
                code_path        = modules,                    # Local code paths not on
                conda_env        = 'conda.yml',
                signature        = infer_signature(self.model.input_example, self.model.output_example),
                training_steps   = self._cortex_config['training_steps'],
                deployment_steps = self._cortex_config.get('deployment_steps') or []
            )
        else:
            self._error_message = f"An error occurred while detecting the Cortex model type. \
            Found '{self.model.model_type}', but only ['cortex'] are acceptable values"
            raise Exception

        return f'Saved the pipeline artifacts to disk: ({self._artifacts_dir})'

    def _upload_pipeline(self):
        cortex_sdk.Pipelines.upload_files(self._pipeline_id, f'./models/cortex/{self._pipeline_id}/')
    

    def set_artifacts_dir(self, artifacts_dir: str):
        if artifacts_dir:
            self._artifacts_dir = artifacts_dir
            return self._artifacts_dir
        
        location = 'cortex' if self._use_tracking else 'local'
        id = self._pipeline_id if self._use_tracking and self._pipeline_id else self._now
        self._artifacts_dir =  f'models/{location}/{id}'

        return self._artifacts_dir
    
    @property
    def _now(self):
        return datetime.now().strftime('%m%d%Y-%H%M%S')

    #---------------------------------------------------------------------------

    def from_file(self, path: str):
        self._path          = path
        self._cortex_config = self._load_cortex_yaml()

        return self

    def run(self):
        try:
            # Step 1 - Setup model data
            model_info = self._get_model()
            self._model_id = model_info['model_id']

            # Step 2 - Create / Get live pipeline data
            if self._use_tracking:
                pipeline_info     = self._setup_pipeline()
                self._pipeline_id = pipeline_info['pipeline_id']

            self.set_artifacts_dir()

            # Step 3 - Initialize the pipeline steps
            self._initialize_steps(self._pipeline_id)

            # Step 4 - Run the pipeline
            if self._use_tracking:
                self._run_pipeline(
                    self._pipeline_id,
                    self._model_id
                )

            # Step 5 - Run the training steps
            self._run_training_steps()

        except Exception as e:
            # Handle extra errors in cases we haven't yet caught
            if not self._error_message:
                self._error_message = traceback.format_exc()

        finally:
            try:
                # Final Step - Contact callback route to update currentStage of model pipeline
                if self._use_tracking:
                    status = 'Failed' if self._error_message or not self._success else 'Successful'
                    self._complete_callback(
                        status,
                        self._error_message
                    )

            except Exception as e:
                print(f'An internal server error has occurred!\n{e}')

            if self._error_message:
                print(self._error_message)
            else:
                print('Completed Cortex Pipeline Run')
