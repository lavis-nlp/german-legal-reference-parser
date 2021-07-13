from setuptools import setup

setup(name='olparse',
      version='0.1',
      description='Parser for OpenLegal Documents',
      author='Kevin Pech, Marco Wrzalik',
      author_email='m.wrzalik@web.de',
      license='MIT',
      packages=['olparse'],
      install_requires=[
          'beautifulsoup4'
      ],
)