from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='pro-video-toolsda',
    version=1.0,
    description='Este pacote fornece tools video processing',
    long_description=Path('README.md').read_text(),
    author='Daniel Ramos',
    author_email='danielramos@gmail.com',
    keywords=['camera','video', 'tools'],
    packages= find_packages()
)