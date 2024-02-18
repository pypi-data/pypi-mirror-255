# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['osconfiglib', 'osconfiglib.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['osconfiglib = osconfiglib.cli.main:cli']}

setup_kwargs = {
    'name': 'osconfiglib',
    'version': '0.2.1',
    'description': 'Library for image configuration',
    'long_description': '[![Lint](https://github.com/brandonrc/osconfiglib/actions/workflows/lint.yml/badge.svg)](https://github.com/brandonrc/osconfiglib/actions/workflows/lint.yml)\n\n# osconfiglib\n\nosconfiglib is a Python library designed to ease the process of layer-based configuration for virtual machines (QCOW2). The library provides utilities to manage layers, apply configurations, and includes a CLI tool for easy management.\n\n## Installation\n\nTo install osconfiglib, add the following to the dependencies section of your project\'s `pyproject.toml`:\n\n```toml\nosconfiglib = "^1.0.0"\n```\n\nThen run:\n\n```bash\n$ pip install -r requirements.txt\n```\n\n## Usage\n\nHere\'s a basic example of how you can use osconfiglib:\n\n```python\nfrom osconfiglib.layers import squash_layers, export_squashed_layer\nfrom osconfiglib.virt_customize import apply_squashed_layer\n\n# Use osconfiglib to squash layers\nsquashed_layer = squash_layers(base_image_path, os_recipe_toml_path)\n\n# Export the squashed layer\nexport_squashed_layer(squashed_layer, output_image_path)\n\n# Apply the squashed layer to a base image\napply_squashed_layer(base_image_path, squashed_layer, output_image_path, python_version="python3")\n```\n\n### CLI Usage\n\nosconfiglib also includes a CLI tool to manage your layers. Here are some examples of how to use it:\n\n```bash\n# List all layers\n$ osconfiglib list layers\n\n# Check version\n$ osconfiglib --version\n\n# Add RPM to a layer\n$ osconfiglib add rpm mylayer tmux\n\n# Add a file to a layer\n$ osconfiglib add file mylayer ~/.tmux.conf /home/user\n\n# Create a new layer\n$ osconfiglib create layer newLayer\n\n# Delete a layer\n$ osconfiglib delete layer <layer>\n```\n\n## Repository Structure\n\nWhen using osconfiglib to manage layers, your repository should follow this structure:\n\n```\nmy-build/\n├── configs/\n│   ├── bin/\n│   │   └── custom-executable\n│   ├── etc/\n│   │   └── custom-executable.conf\n│   └── usr/local/bin\n│       └── symlink-to-something\n├── package-lists/\n│   ├── rpm-requirements.txt\n│   ├── dep-requirements.txt\n│   └── pip-requirements.txt\n└── scripts/\n    ├── 01-first-script-to-run.sh\n    └── 02-second-script-to-run.sh\n```\n\n- `configs/`: This directory is where you put custom config files that go in the root filesystem. Examples can include custom dns, dhcpd, tftp, and other services required for this "layer".\n- `package-lists/`: This directory contains lists for RedHat and Debian packages based on the flavor of Linux. A separate file is included for pip requirements for the system Python.\n- `scripts/`: Scripts are run in alphabetical order. If you number them you can control the order of the scripts.\n\nYou can refer to this [os-layer-template](https://github.com/brandonrc/os-layer-template) for a complete template of the repository structure.\n\n\n\n## TOML File Usage\n\nYou can define your layers in a TOML file for easy import, squash, and application. Here\'s an example of a TOML file:\n\n```toml\nname = "Ubuntu-Python-Dev"\nversion = "1.0.0"\n\n[layers]\n[[layer]]\ntype = "git"\nurl = "https://github.com/user/os-ubuntu.git"\nbranch_or_tag = "main"\n\n[[layer]]\ntype = "git"\nurl = "https://github.com/user/os-python.git"\nbranch_or_tag = "main"\n\n[[layer]]\ntype = "local"\npath = "/path/to/your/local/os-custom-configs"\n```\n\nThis TOML file defines three layers. The `os-ubuntu` and `os-python` layers are git layers. The `os-custom-configs` layer is a local layer, stored in your filesystem.\n\nTo use these layers:\n\n1. Import the layers using the `import_layers` function:\n\n   ```python\n   import_layers(\'path/to/your/layers.toml\')\n   ```\n\n   This function will import all the layers defined in your TOML file into your local cache. For git layers, the repositories will be cloned. For local layers, they are already in your filesystem, so they won\'t be imported.\n\n2. Squash the layers using the `squash_layers` function:\n\n   ```python\n   squashed_layer = squash_layers(layers)\n   ```\n\n   This function will combine all the layers into a single squashed layer.\n\n3. You can either export the squashed layer into a tarball using the `export_squashed_layer` function:\n\n   ```python\n   export_squashed_layer(squashed_layer, \'path/to/your/output.tar.gz\')\n   ```\n\n   Or apply the squashed layer to a base image using the `apply_squashed_layer` function:\n\n   ```python\n   apply_squashed_layer(\'path/to/your/base.qcow2\', squashed_layer, \'path/to/your/output.qcow2\')\n   ```\n\n4. If you want to export or apply layers based on a TOML file directly, you can use the `toml_export` or `toml_apply` functions:\n\n   ```python\n   toml_export(\'path/to/your/layers.toml\', \'path/to/your/output.tar.gz\')\n   ```\n\n   ```python\n   toml_apply(\'path/to/your/layers.toml\', \'path/to/your/base.qcow2\', \'path/to/your/output.qcow2\')\n   ```\n\n   The `toml_export` function will export a squashed layer based on the layers defined in the TOML file. The `toml_apply` function will apply a squashed layer based on the layers defined in the TOML file to a base image.\n\n\n\n## Developing\n\nTo run the test suite, install the dev dependencies and run pytest:\n\n```bash\n$ pip install -r dev-requirements.txt\n$ pytest\n```\n\n## Contact\n\nIf you have any issues or questions, feel free to\n\n contact me at brandon.geraci@gmail.com.\n',
    'author': 'Brandon Geraci',
    'author_email': 'brandon.geraci@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
