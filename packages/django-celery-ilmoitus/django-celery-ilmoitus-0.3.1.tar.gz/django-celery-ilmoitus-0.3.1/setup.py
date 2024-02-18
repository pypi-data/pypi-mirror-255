# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
  setup_requires='git-versiointi',
  name='django-celery-ilmoitus',
  description='Ajax/Websocket-pohjainen Django-ilmoitusnäkymätoteutus',
  url='https://github.com/an7oine/django-celery-ilmoitus.git',
  author='Antti Hautaniemi',
  author_email='antti.hautaniemi@me.com',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=['celery', 'Django>=3.2'],
  extras_require={
    'websocket': ['celery-viestikanava', 'django-pistoke'],
  },
  entry_points={
    'django.sovellus': [
      'ilmoitus = ilmoitus.sovellus:Ilmoitus',
    ],
  },
)
