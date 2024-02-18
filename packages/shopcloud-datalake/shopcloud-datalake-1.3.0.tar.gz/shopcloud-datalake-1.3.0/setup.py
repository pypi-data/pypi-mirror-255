from setuptools import find_packages, setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = {
    "name": 'shopcloud-datalake',
    "version": '1.3.0',
    "description": 'CLI tool for datalake operation',
    "long_description_content_type": "text/markdown",
    "long_description": README,
    "license": 'MIT',
    "packages": find_packages(),
    "author": 'Konstantin Stoldt',
    "author_email": 'konstantin.stoldt@talk-point.de',
    "keywords": ['CLI'],
    "url": 'https://github.com/Talk-Point/shopcloud-datalake-cli',
    "scripts": ['./scripts/datalake'],
}

install_requires = [
    'pyyaml',
    'requests',
    'pytest',
    'shopcloud-secrethub>=2.12.0',
    'pre-commit',
    'google-cloud-storage',
    'google-cloud-bigquery',
    'pandas',
    'tqdm',
    'pyarrow',
    'fastparquet',
    'prompt_toolkit',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
