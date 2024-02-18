from setuptools import setup, find_packages

setup(
    name='yooncloud-core',
    version='0.0.1',
    install_requires=['boto3', 'pydantic'],
    packages=find_packages(exclude=[]),
    python_requires='>=3.8',
)