from setuptools import setup, find_packages
import os

VERSION = '2.0.5'

setup(name='emrt.necd.theme',
      version=VERSION,
      description="Installable theme: emrt.necd.theme",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Mikel Santamaria',
      author_email='msantamaria@bilbomatica.es',
      url='https://github.com/eea/emrt.necd.theme/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['emrt', 'emrt.necd'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'z3c.jbot',
          'eea.icons',
          'emrt.necd.content',
          'Products.Collage',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
