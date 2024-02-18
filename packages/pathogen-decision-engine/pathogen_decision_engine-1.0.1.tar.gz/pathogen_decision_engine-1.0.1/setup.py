from setuptools import setup, find_packages
import os


def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as file:
        return file.read()


setup(
    name='pathogen_decision_engine',
    version='1.0.1',
    long_description=read_file('readme.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.0.3',
        'rule_engine'
    ],
    entry_points={
        'console_scripts': [
            'decision_engine_cli = pathogen_decision_engine.decision_engine_cli:main'
        ]
    }
)
