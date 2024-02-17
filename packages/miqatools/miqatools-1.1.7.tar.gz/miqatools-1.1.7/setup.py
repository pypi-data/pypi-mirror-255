from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='miqatools',
    version='1.1.7',
    license='GPLv3',
    author="Gwenn Berry",
    author_email='gwenn@magnalabs.co',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://www.magnalabs.co',
    keywords='miqa',
    install_requires=[
          'asyncio', 'aiohttp',
      ],
    long_description=long_description,
    long_description_content_type='text/x-rst'
)