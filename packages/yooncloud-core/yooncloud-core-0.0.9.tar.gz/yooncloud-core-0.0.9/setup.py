from setuptools import setup, find_packages

setup(
    name='yooncloud-core',
    version='0.0.9',
    install_requires=['boto3', 'pydantic', 'urllib3<2,>=1.26.2'],
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    package_dir={'': 'src'},
    zip_safe = False
)