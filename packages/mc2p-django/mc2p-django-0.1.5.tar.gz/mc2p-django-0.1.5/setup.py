from setuptools import setup, find_packages

import os
import re


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('django_mc2p')

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


setup(
    name='mc2p-django',
    version=version,
    url='https://github.com/mc2p/mc2p-django',
    license='BSD',
    description='MyChoice2Pay Django Bindings',
    long_description=README,
    long_description_content_type='text/markdown',
    author='MyChoice2Pay',
    author_email='support@mychoice2pay.com',
    download_url='https://github.com/mc2p/mc2p-django/archive/v0.1.5.tar.gz',
    packages=find_packages(),
    install_requires=[
        'django',
        'mc2p-python'
    ],
    keywords=['mychoice2pay', 'payments'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
