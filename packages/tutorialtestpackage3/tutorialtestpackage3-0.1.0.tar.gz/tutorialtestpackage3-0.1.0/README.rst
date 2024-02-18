The purpose of this project is to show how to upload a python package to the PYPI server.

Main commands:

- Build the package distribution
`python setup.py sdist bdist_wheel`

- Install twine on local env
`pip install twine`

- Upload to TestPyPi
`twine upload --repository-url https://test.pypi.org/legacy/ dist/*`

- Upload to Pypi
`twine upload dist/*`

- Create a venv
`python -m venv venv`

- Activate a venv
`venv\\Scripts\\activate`

- Install package
`pip install --index-url https://test.pypi.org/simple/ your_package_name`

- Show installed packages
`pip list`