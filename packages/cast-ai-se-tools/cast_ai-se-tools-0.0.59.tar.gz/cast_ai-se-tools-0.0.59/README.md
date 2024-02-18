# cast-ai-se-tools package

[![PyPI version](https://img.shields.io/pypi/v/my-awesome-package.svg)](https://pypi.org/project/cast-ai-se-tools/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Style](https://img.shields.io/badge/code%20style-flake8-000000.svg)](https://flake8.pycqa.org/)

[![GitHub Issues](https://img.shields.io/github/issues/castai/solutions-engineering-lab)](https://github.com/castai/solutions-engineering-lab/issues)
[![GitHub release](https://img.shields.io/github/release/castai/solutions-engineering-lab)](https://github.com/castai/solutions-engineering-lab/releases)

## Overview

Cast AI SE Package: is a python package intended to serve tools required by Cast AI`s customer success team.
Purpose: not to have to invent the wheel creating functions that can created once and leveraged via a package.

## Installation

You can install `cast-ai-se-tools` using pip:

```bash
pip install cast-ai-se-tools
```

### Caveats
To leverage Azure automations make sure you:
Create an App and provide it Read/Write permissions to: \
*AKS \
*Log Analytics \
*Resource Group