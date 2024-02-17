# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lmoe', 'lmoe.api', 'lmoe.experts', 'lmoe.framework', 'lmoe.utils']

package_data = \
{'': ['*'], 'lmoe.experts': ['templates/*']}

install_requires = \
['ollama>=0.1.6,<0.2.0', 'pyperclip>=1.8.2,<2.0.0']

entry_points = \
{'console_scripts': ['lmoe = lmoe.main:run']}

setup_kwargs = {
    'name': 'lmoe',
    'version': '0.1.2',
    'description': "lmoe (Layered Mixture of Experts, pronounced 'Elmo') is your programmable CLI assistant.",
    'long_description': '# Introduction\n\n<img src="https://rybosome.github.io/lmoe/assets/lmoe-armadillo.png">\n\nlmoe (layered mixture of experts, pronounced "Elmo") is a multimodal CLI assistant with a natural\nlanguage interface.\n\nRunning on Ollama and various open-weight models, lmoe is a convenient, low-overhead,\nlow-configuration way to interact with programmable AI models from the command line.\n\n## Lmoe Armadillo\n\nThe mascot and avatar for the project is Lmoe Armadillo, a Cyborg [Cingulata](https://en.wikipedia.org/wiki/Cingulata)\nwho is ready to dig soil and do toil.\n\n## Capabilities\n\nlmoe has a natural language interface.\n\nYou will need to quote your strings if you want to use characters that are significant to your shell\n(like `?`).\n\n### Querying\n```\n% lmoe who was matisse\n\n Henri Matisse was a French painter, sculptor, and printmaker, known for his influential role in\n modern art. He was born on December 31, 1869, in Le Cateau-Cambrésis, France, and died on\n November 3, 1954. Matisse is recognized for his use of color and his fluid and expressive\n brushstrokes. His works include iconic paintings such as "The Joy of Life" and "Woman with a Hat."\n```\n\n```\n% lmoe what is the recommended layout for a python project with poetry\n\n With Poetry, a Python packaging and project management tool, a recommended layout for a Python\n project could include the following structure:\n\n myproject/\n ├── pyproject.toml\n ├── README.rst\n ├── requirements.in\n └── src/\n     ├── __init__.py\n     └── mypackage/\n         ├── __init__.py\n         ├── module1.py\n         └── module2.py\n\nIn this layout, the `myproject/` directory contains the root-level project files. The\n`pyproject.toml` file is used for managing dependencies and building your Python package. The\n`README.rst` file is optional, but common, to include documentation about your project. The\n`requirements.in` file lists the external packages required by your project.\n\nThe `src/` directory contains your source code for the project. In this example, there\'s a package\nnamed `mypackage`, which includes an `__init__.py` file and two modules: `module1.py` and\n`module2.py`.\n\nThis is just one suggested layout using Poetry. Depending on your specific project requirements and\npreferences, the layout might vary. Always refer to the [Poetry documentation](https://python-poetry.org/)\nfor more detailed information.\n```\n\n### Querying your context\n\n#### Piping context\n\nPipe it information from your computer and ask questions about it.\n\n```\n% cat projects/lmoe/lmoe/main.py | lmoe what does this code do\n\n The provided code defines a Python script named \'lmoe\' which includes an argument parser, the\n ability to read context from both STDIN and the clipboard, and a \'classifier\' module for\n determining which expert should respond to a query without actually responding. It does not contain\n any functionality for executing queries or providing responses itself. Instead, it sets up the\n infrastructure for interfacing with external experts through their \'generate\' methods.\n```\n\n```\n% ls -la | lmoe how big is my zsh history\n\n The size of your Zsh history file is 16084 bytes.\n```\n\n#### Pasting context\n\nGet an error message and copy it to the clipboard, then ask about it.\n\n```\n% print -x \'hello\'\nprint: positive integer expected after -x: hello\n\n% lmoe --paste how do I fix this error\n To use the `-x` option with the `print` command in Bash, you need to provide a positional argument that is a file descriptor. Instead, you provided a string \'hello\'. Here\'s how you can correctly use it:\n\n1. Create or have a file with the name \'hello\' and make sure it exists in your working directory.\n2. Run the following command instead: `print -r -- < hello`. This reads the contents of the file \'hello\' as input for print, which displays its output to stdout.\n```\n\n### Project Generation\n\nCopying the above advice from `lmoe` on creating a Python Poetry project...\n\n```\n With Poetry, a Python packaging and project management tool, a recommended layout for a Python\n project could include the following structure:\n\n myproject/\n ├── pyproject.toml\n ├── README.rst\n ├── requirements.in\n └── src/\n     ├── __init__.py\n     └── mypackage/\n         ├── __init__.py\n         ├── module1.py\n         └── module2.py\n\nIn this layout, the `myproject/` directory contains the root-level project files. The\n`pyproject.toml` file is used for managing dependencies and building your Python package. The\n`README.rst` file is optional, but common, to include documentation about your project. The\n`requirements.in` file lists the external packages required by your project.\n\nThe `src/` directory contains your source code for the project. In this example, there\'s a package\nnamed `mypackage`, which includes an `__init__.py` file and two modules: `module1.py` and\n`module2.py`.\n\nThis is just one suggested layout using Poetry. Depending on your specific project requirements and\npreferences, the layout might vary. Always refer to the [Poetry documentation](https://python-poetry.org/)\nfor more detailed information.\n```\n\n```\n% lmoe --paste "make a project like this for a module called \'alexandria\' with 3 sub modules: \'auth\', \'util\', and \'io\'"\nmkdir alexandria/\ntouch alexandria/pyproject.toml\ntouch alexandria/README.rst\ntouch alexandria/requirements.in\nmkdir alexandria/src/\ntouch alexandria/src/__init__.py\nmkdir alexandria/src/alexandria/\ntouch alexandria/src/alexandria/__init__.py\nmkdir alexandria/src/alexandria/auth/\ntouch alexandria/src/alexandria/auth/__init__.py\nmkdir alexandria/src/alexandria/util/\ntouch alexandria/src/alexandria/util/__init__.py\nmkdir alexandria/src/alexandria/io/\ntouch alexandria/src/alexandria/io/__init__.py\n```\n\nComing soon: the ability to dry-run this, see the intended commands, then execute it.\n\n## Extension Model\n\nNew capabilities can be added to `lmoe` with low overhead. Just implement\n`lmoe.api.base_expert.BaseExpert` and add your new expert to the registry in\n`lmoe/experts/__init__.py`. See existing experts for examples.\n\n## Commands\n\n`lmoe` supports command-like behavior (i.e. executing actions for and against itself).\n\nAll of these are supported using the same extension model available to external developers.\n\n### Refresh\n\nUpdate local Ollama modelfiles. This should be run any time you add a new expert and modelfile, or\nalter a modelfile template.\n\nNote that all queries are examples of receiving the same output.\n\n```\n% lmoe refresh\n% lmoe update your models\n% lmoe refresh the models\n% lmoe update models\n\nDeleting existing lmoe_classifier...\nUpdating lmoe_classifier...\nDeleting existing lmoe_code...\nUpdating lmoe_code...\nDeleting existing lmoe_project_initialization...\nUpdating lmoe_project_initialization...\nDeleting existing lmoe_general...\nUpdating lmoe_general...\n```\n\n## Status\n\nVersion 0.1.2\n\nThis is currently a very basic implementation which primarily supports a general expert, offers no\nconfiguration, has limited automation for environment setup, and does not have persistence.\n\nThis is not yet ready for others\' use.\n\n### Upcoming features\n\n* error handling\n* self-setup of models and ollama context after installation\n* persisted context (i.e. memory, chat-like experience without a formal chat interface)\n* configurability\n* tests\n* programmable interface\n',
    'author': 'Ryan Eiger',
    'author_email': 'ryebosome@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
