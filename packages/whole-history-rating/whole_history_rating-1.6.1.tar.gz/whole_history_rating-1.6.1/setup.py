from setuptools import setup, find_packages
from codecs import open
from os import path

setup(
    name="whole_history_rating",  # This is the name of your PyPI-package.
    version="1.6.1",  # Update the version number for new releases
    description="a python convertion from the ruby implementation of Rémi Coulom's Whole-History Rating (WHR) algorithm.",
    url="https://github.com/pfmonville/whole_history_rating",
    author="Pierre-François Monville",
    # packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages=["whr"],
    install_requires=["numpy"],
    classifiers=["License :: OSI Approved :: MIT License"],
)
