import codecs
from setuptools import setup, find_packages
import os
import re


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'src', 'walutomatpy', '__init__.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = [
    'pyOpenSSL >=20.0.1, <21',
    'requests >=2.25.1, <3',
    'python-dateutil >=2.8.2, <3'
]


setup(name='walutomatpy',
      version=version,
      description="Python wrapper Walutomat REST API 2.0",
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Topic :: Internet :: WWW/HTTP',
      ],
      author='Lukasz Jachym',
      author_email='lukasz.jachym@gmail.com',
      url='https://github.com/b1r3k/walutomatpy/',
      license='MIT',
      package_dir={"": "src"},
      packages=find_packages(where="src"),
      test_suite='nose.collector',
      tests_require=['nose', 'flake8', 'coverage'],
      python_requires='>=3.6',
      install_requires=install_requires,
      include_package_data=True)
