from setuptools import find_packages, setup

# Setup custom import schema
# cortex.__version__
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current)

from cortex_container_tools import __version__

setup(
    name         = 'cortex_container_tools',
    version      = __version__,
    packages     = find_packages(exclude=['tests*']),
    author       = 'Nearly Human',
    author_email = 'support@nearlyhuman.ai',
    description  = 'Nearly Human Cortex Container Tools dependency for creating training / deployment containers.',
    keywords     = 'nearlyhuman, nearly human, cortex, container, tools',

    python_requires  = '>=3.8.10',
    install_requires = [
        'fastapi~=0.104.0',
        'mlflow-skinny==2.8.0',
        'mlserver==1.2.1',
        'cortex_sdk'
    ]
)
