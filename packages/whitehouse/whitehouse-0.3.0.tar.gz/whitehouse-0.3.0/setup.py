from setuptools import setup, find_packages
import pathlib
import shutil

# removing dist/ and whitehouse.egg-info/ directories
shutil.rmtree("dist", ignore_errors=True)
shutil.rmtree("whitehouse.egg-info", ignore_errors=True)

setup(
    name="whitehouse",
    version="0.3.0",
    description="An html templating library for Python",
    author="Minh-Quan Do",
    author_email="mdo9@gmu.edu",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=["__pycache__", "*.pyc", "*.pyo"]),
    exclude_package_data={
        '': ['__pycache__', '*.pyc', '*.pyo']
    },
    install_requires=[
        'beautifulsoup4'
    ]
)