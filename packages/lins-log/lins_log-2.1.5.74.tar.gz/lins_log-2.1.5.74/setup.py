from distutils.core import setup
from setuptools import find_packages


def get_version():
    return open('version.txt', 'r').read().strip()


setup(
    author='Nicollas Borges',
    author_email='nicollasborges@lojaspompeia.com.br',
    description='Para utilizar Graylog',
    license='MIT',
    name='lins_log',
    packages=find_packages(),
    url='https://bitbucket.org/grupolinsferrao/pypck-logs/',
    version=get_version(),
    install_requires=['graypy==1.1.2']
)
