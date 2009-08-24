from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='arcs.shibboleth.client',
      version=version,
      description="Shibboleth authentication handler",
      long_description=open(os.path.join("docs", "intro.rst")).read() + "\n" +
                       open(os.path.join("docs", "history.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Russell Sim',
      author_email='russell.sim@arcs.org.au',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['arcs', 'arcs.shibboleth'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      shib-login = arcs.shibboleth.client.shiblogin:main
      shib-logout = arcs.shibboleth.client.shiblogout:main
      """,
      )
