# -*- coding: utf-8 -*-

from setuptools import setup

setup(
  setup_requires='git-versiointi>=1.6rc4',
  name='celery-viestikanava',
  description='Asynkroninen toteutus Celeryn käyttämiseksi viestinvälitykseen',
  url='https://github.com/an7oine/celery-viestikanava.git',
  author='Antti Hautaniemi',
  author_email='antti.hautaniemi@pispalanit.fi',
  licence='MIT',
  py_modules=['viestikanava'],
  python_requires='>=3.8',
  install_requires=['celery'],
)
