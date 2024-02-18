import setuptools
from setuptools import setup

# pylint: disable-next=exec-used,consider-using-with
exec(open('databricks_genai/version.py', 'r', encoding='utf-8').read())

install_requires = [
    'databricks-sdk>=0.14.0',
    'typing_extensions>=4.7.1',
    'mosaicml-cli==0.6.5',
    'datasets>=2.16.1',
    'mlflow>=2.9.2'
]

extra_deps = {}

extra_deps['dev'] = [
    # 'build>=0.10.0',
    'isort>=5.9.3',
    'packaging>=21,<23',
    'pylint>=3.0.0',
    'pyright==1.1.256',
    'pytest>=7.4.0',
    'yapf>=0.40.0',
    # 'twine>=4.0.2',
]

extra_deps['all'] = set(dep for deps in extra_deps.values() for dep in deps)

setup(
    name='databricks-genai',
    version=__version__,  # type: ignore pylint: disable=undefined-variable
    author='Databricks',
    author_email='genai-eng-team@databricks.com',
    description='Interact with the Databricks Generative AI APIs in python',
    url='https://docs.mosaicml.com/projects/mcli/en/latest/finetuning/finetuning.html',  # TODO: update with DBX docs
    include_package_data=True,
    package_data={},
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=install_requires,
    extras_require=extra_deps,
    python_requires='>=3.8',
    ext_package='databricks_genai',
)
