from setuptools import setup, find_packages

setup(
    name="rimc_engine",
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'numpy'
    ],
)