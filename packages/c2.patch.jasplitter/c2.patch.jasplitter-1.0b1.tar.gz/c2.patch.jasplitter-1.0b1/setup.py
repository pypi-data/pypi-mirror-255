# -*- coding: utf-8 -*-
"""Installer for the c2.patch.jasplitter package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('docs/CONTRIBUTORS.rst').read(),
    open('docs/CHANGES.rst').read(),
])


setup(
    name='c2.patch.jasplitter',
    version='1.0b1',
    description="This product is bugfix splitter of Plone for Japanese.",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Manabu TERADA',
    author_email='terada@cmscom.jp',
    url='https://pypi.python.org/pypi/c2.patch.jasplitter',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['c2', 'c2.patch'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'collective.monkeypatcher',
        'six',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            # 'plone.testing>=5.0.0',
            'plone.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'plone.api',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
