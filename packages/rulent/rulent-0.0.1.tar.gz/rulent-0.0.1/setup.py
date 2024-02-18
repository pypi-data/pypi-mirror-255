from setuptools import setup, find_packages
from pathlib import Path
with open('requirements.txt') as f:
    required = f.read().splitlines()

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='rulent',
    version='0.0.1',
    author='Raza Balbale',
    packages=find_packages(),
    description='A declarative rules engine.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email='ribalbale@gmail.com',
    url='https://github.com/razaibi/pyrulent',
    project_urls={
        'Documentation': 'https://github.com/razaibi/pyrulent/README.md',
        'Source': 'https://github.com/razaibi/pyrulent',
        'Tracker': 'https://github.com/razaibi/pyrulent/',
    },
    install_requires=required,
    license='Apache 2.0',
    include_package_data=True,
    test_suite='tests',
)
