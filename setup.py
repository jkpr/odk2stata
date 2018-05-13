from setuptools import setup, find_packages

from odk2stata import __version__


packages = find_packages()


setup(
    name='odk2stata',
    version=__version__,
    author='James K. Pringle',
    author_email='jpringle@jhu.edu',
    url='http://www.pma2020.org',
    packages=packages,
    license='LICENSE.txt',
    description='Generate a Stata do file for ODK analysis',
    long_description=open('README.md').read(),
    install_requires=[
        'xlrd>=1.1.0',
        'Jinja2>=2.10'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
