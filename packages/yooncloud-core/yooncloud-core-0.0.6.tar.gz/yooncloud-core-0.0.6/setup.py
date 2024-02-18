from setuptools import setup, find_packages

setup(
    name='yooncloud-core',
    version='0.0.6',
    install_requires=['boto3', 'pydantic', 'urllib3<2,>=1.26.2'],
    packages=find_packages(exclude=[]),
    python_requires='>=3.8',
)