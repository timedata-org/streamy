#!/usr/bin/env python

import os
import sys
from setuptools import setup


def setup_package():
    setup(name='streamy',
          version='1.0',
          py_modules=['streamy'])


if __name__ == '__main__':
    setup_package()
