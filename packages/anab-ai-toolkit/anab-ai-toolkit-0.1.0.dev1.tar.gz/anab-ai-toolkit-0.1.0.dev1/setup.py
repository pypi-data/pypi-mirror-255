from setuptools import setup, find_packages
from pkg_resources import parse_requirements

# Read the requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [str(req) for req in parse_requirements(f)]

setup(
    name='anab-ai-toolkit',
    version='0.1.0.dev1',
    description='Useful functions for AI-related research.',
    author='Ana Brassard',
    author_email='brassard.ana@gmail.com',
    packages=find_packages(),
    install_requires=requirements,
)
