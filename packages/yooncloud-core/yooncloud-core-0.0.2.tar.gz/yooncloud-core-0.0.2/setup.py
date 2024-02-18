from setuptools import setup, find_packages

setup(
    name='yooncloud-core',
    version='0.0.2',
    install_requires=['boto3', 'pydantic', 'urllib3==1.12.1'],
    packages=find_packages(exclude=[]),
    python_requires='>=3.8',
)