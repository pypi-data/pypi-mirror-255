#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

# https://github.com/pypa/setuptools_scm
# use_scm = {"write_to": "empanada_napari/_version.py"}


def _clean_version():
    """
    This function was required because scm was generating developer versions on
    GitHub Action.
    """

    def get_version(version):
        return '0.0.6'

    def empty(version):
        return ''

    return {'local_scheme': get_version, 'version_scheme': empty, "write_to": "empanada_napari/_version.py"}


setup(use_scm_version=_clean_version)
