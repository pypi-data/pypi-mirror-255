#! /usr/bin/env python
import setuptools

setuptools.setup(
    entry_points={'console_scripts':
                  ['pypi-downloader=pypi_downloader.pypi_downloader_mt:main',
                   'pypi-packages=pypi_downloader.pypi_packages:main']},
    python_requires='>=3.6'
)
