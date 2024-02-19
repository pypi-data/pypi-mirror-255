import setuptools
from setuptools import setup

import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


setup(
    name='Peliqan',
    version=get_version("peliqan/__init__.py"),
    description='This package is an sdk that allows any python client to connect with a Peliqan environment.',
    url='https://peliqan.io/',
    author='Peliqan.io',
    author_email='dev@peliqan.io',
    license='MIT',
    packages=setuptools.find_packages('.'),
    install_requires=['pandas',
                      'requests',
                      ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
