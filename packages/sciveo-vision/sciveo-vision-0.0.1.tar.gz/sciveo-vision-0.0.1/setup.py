from setuptools import setup, find_packages
from sciveo_vision.version import __version__

setup(
    name='sciveo-vision',
    version=__version__,
    packages=find_packages(),
    install_requires=[
      'pandas>=0.0.0',
      'numpy>=0.0.0',
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
