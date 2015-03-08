from setuptools import setup

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(name='striplog',
      version='0.4',
      description='Tools for making and managing well data.',
      url='http://github.com/agile-geoscience/striplog',
      author='Agile Geoscience',
      author_email='hello@agilegeoscience.com',
      license='Apache 2',
      packages=['striplog'],
      install_requires=REQUIREMENTS,
      zip_safe=False)
