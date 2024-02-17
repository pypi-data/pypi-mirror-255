from setuptools import setup, find_packages

setup(
    author='David María Arribas',
    description='Functions used in CAPO projects',
    name='capo_libs',
    version='0.0.1_alpha',
    packages=find_packages(include=['src.*']),
    python_requires='>=3.10',
)