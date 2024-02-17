from setuptools import setup, find_packages
import pathlib


setup(
    name="whitehouse",
    version="0.2.0",
    description="An html templating library for Python",
    author="Minh-Quan Do",
    author_email="mdo9@gmu.edu",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={
        '': ['__pycache__', '*.pyc', '*.pyo']
    },
    install_requires=[
        'beautifulsoup4'
    ]
)