# Tb_wrapper
## _Description_
This wrapper allows us to use the Python API client of Thingsboard.
## Installation

- TB wrapper requirements [tb_rest_client](https://pypi.org/project/tb-rest-client/)
- Thingsboard [Thingsboard](https://thingsboard.io/docs/reference/python-rest-client/)
```sh
pip install tb_wrapper
```
### Features
- Manage Entities such as Devices and Assets
- Access to thingsboard account using credentials stored into files
- Create Alarms 


## Build
- Requirements [twine](https://twine.readthedocs.io/en/stable/)
- Requirements [python](https://www.python.org/)
- Requirements [setuptools](https://pypi.org/project/setuptools/)


### Steps

First of all, change the version of the release to the latest version at the pyproject.toml file
```
[project]
name = "<my project name>"
version = "<my-version"
```
Create the dist directory used to upload the package into Pypi
```sh
python3 -m build
```
Upload the new version of the package using twine
```sh
twine upload dist/*
```
and use Username and Password based on API Token