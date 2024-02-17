from setuptools import find_packages
from setuptools import setup

with open('./ks_session_manager/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'")
            break


def read_requirements():
    with open('./requirements.txt') as f:
        req = f.read().splitlines()

    return req


with open('README.md', "r") as f:
    long_description = f.read()

setup(
    name='ks_session_manager',
    author="pylakey",
    version=version,
    packages=find_packages(),
    # license='MIT',
    # license_file='LICENSE',
    description='KS session manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=read_requirements(),
    python_requires='>=3.10',
)
