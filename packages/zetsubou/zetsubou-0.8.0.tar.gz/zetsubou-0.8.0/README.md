# Zetsubou

[![CI (ubuntu-latest)](https://github.com/BentouDev/Zetsubou/actions/workflows/python-ci.yml/badge.svg)](https://github.com/BentouDev/Zetsubou/actions/workflows/python-ci.yml) [![PyPI version](https://badge.fury.io/py/zetsubou.svg)](https://badge.fury.io/py/zetsubou)

### FASTbuild project generator for the helpless

High level wrapper around FASTbuild build system, written in python. Generates Visual Studio solution from simple yaml description. Supports Conan package manager. Provides commands for common operations, like setting up dev environment, building or clean (and many more in future).

_Currently only Windows and msvc are supported, but clang and Linux are planned._


---

## Install
```
pip install zetsubou
```

### Development
Local install in editable mode
```
python -m pip install -e .
```
Deploy conan generator
```
deploy_generator.bat
```
or
```
conan export zetsubou/zetsubou_conan_toolchain.py --user=bentou --channel=stable
```

## Usage
```cmd
zetsubou [COMMAND] [PROJECT] [OPTIONS...]
```

```cmd
zetsubou regen project.yml --verbose
```

## Commands
- clean - removes all generated build folder and sln
- install - setups virtual environment based on your build_tools.ini
- gen - generates bff files, creates visual studio project and solution
- regen - clean, install and gen in one command
- build - build generated project
- create - (WiP) emit new project from template

---

## Example Project
### project.yml
```yml
project: MyTest

config:
  verbose_build: false
  platforms:
    - 'platform/windows.yml'
  rules:
    - 'configurations/MsvcRules.yml'
  configurations:
    - 'configurations/Debug.yml'
    - 'configurations/Release.yml'
  config_string: '{platform}-{configuration}-{toolchain}'

conan:
  build_tools: build_tools.ini
  dependencies: dependencies.ini

targets:
  - 'my_app/my_app.yml'
```

### my_app.yml
```yml
target: 'MyApp'

config:
  kind: EXECUTABLE

source:
  paths: 'src'
  patterns:
    - '*.cpp'
```

### Directory structure
```ini
my_project/
├── build/              # generated
│   ├── conan/          # conan dependencies install output
│   ├── fbuild/         # generated fastbuild files (bff)
│   ├── projects/       # generated vcxproj files
│   ├── scripts/        # command scripts
│   └── venv/           # virtual environment, with activate and deactivate scripts
│
├── my_app/
│   ├── src/
│   │   └── main.cpp
│   └── my_app.yml
│
├── my_project.sln      # generated
├── build_tools.ini
├── dependencies.ini
└── project.yml
```
