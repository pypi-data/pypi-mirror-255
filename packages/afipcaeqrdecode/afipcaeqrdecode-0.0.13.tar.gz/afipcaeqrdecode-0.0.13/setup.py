from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='afipcaeqrdecode',
    version='0.0.13',
    packages=find_packages(),
    install_requires=requirements,
    description='Package to decode and extract invoice metadata from an AFIP CAE qr code link',
    author='Emiliano Mesquita',
    license='LGPLv3',
    url='https://github.com/mezka/afipcaeqrdecode',
    long_description=long_description,
    long_description_content_type='text/markdown'
)