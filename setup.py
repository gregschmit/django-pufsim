import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-pufsim',
    version='dev',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Front-end app for puflib',
    long_description=README,
    url='https://github.com/gregschmit/django-pufsim',
    author='Gregory N. Schmit',
    author_email='schmitgreg@gmail.com',
    install_requires=['numpy', 'matplotlib', 'puflib',],
    dependency_links=['https://github.com/gregschmit/puflib/tarball/master#egg=puflib-0.1'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
