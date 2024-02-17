import setuptools
import os

with open('README.md') as readme_f:
  long_description = readme_f.read()

packages = setuptools.find_packages()
for root, _, files in os.walk("tecton_proto"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_swagger"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_openapiv2"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))

setuptools.setup(
    classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'License :: Other/Proprietary License'],
    python_requires='>=3.7',
    author='Tecton, Inc.',
    author_email='support@tecton.ai',
    url='https://tecton.ai',
    license='Tecton Proprietary',
    include_package_data=True,
    description='Tecton Python SDK',
    entry_points={'console_scripts': ['tecton=tecton.cli.cli:main'], 'pytest11': ['pytest_tecton=tecton.pytest_tecton']},
    name='tecton',
    version='0.9.0b12',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['attrs>=21.3.0', 'boto3', 'googleapis-common-protos~=1.52', 'jinja2~=3.0', 'numpy~=1.16', 'pathspec', 'pendulum~=2.1', 'pex~=2.1', 'protobuf>=3.20.0', 'pypika~=0.48.9', 'pytimeparse', 'pandas>=1.0', 'texttable', 'requests', 'colorama~=0.4', 'tqdm~=4.41', 'yaspin<3,>=0.16', 'typing-extensions~=4.1', 'pygments>=2.7.4', 'pytest', 'click~=8.0', 'typeguard~=2.0', 'sqlparse', 'semantic_version', 'pyarrow<15,>=8', 'pydantic<3,>=1.10.13', 'pyyaml'],
    extras_require={'databricks-connect': ['databricks-connect[sql]~=10.4.12'], 'databricks-connect9': ['databricks-connect[sql]~=9.1.23'], 'databricks-connect10': ['databricks-connect[sql]~=10.4.12'], 'databricks-connect11': ['databricks-connect[sql]~=11.3.12'], 'pyspark': ['pyspark[sql]~=3.2.1'], 'pyspark3': ['pyspark[sql]~=3.2.1'], 'pyspark3.1': ['pyspark[sql]~=3.1.2'], 'pyspark3.2': ['pyspark[sql]~=3.2.1'], 'pyspark3.3': ['pyspark[sql]~=3.3.2'], 'rift': ['duckdb==0.9.2', 'deltalake~=0.12', 'pyarrow>=11.0.0'], 'snowflake': ['snowflake-snowpark-python[pandas]~=1.0'], 'athena': ['awswrangler~=3.0'], 'materialization': ['statsd==3.3.0', 'urllib3<2.0.0']},
    packages=packages,
)
