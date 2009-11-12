from setuptools import setup, find_packages
from xml.dom.minidom import parse
from os import path

pom = parse('pom.xml')
# Get version from common file
pom = parse('pom.xml')
for t in pom.getElementsByTagName('project')[0].childNodes:
    if t.nodeName == 'version':
        version = t.childNodes[0].nodeValue.rstrip('-SNAPSHOT')
        break


setup(name='arcs.shibboleth.client',
      version=version,
      description="Shibboleth authentication handler",
      long_description=open(path.join("docs", "intro.rst")).read() + "\n" +
                       open(path.join("docs", "history.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        ],
      keywords='jython',
      author='Russell Sim',
      author_email='russell.sim@arcs.org.au',
      url='',
      license='GPL',
      packages=find_packages('src/main/python', exclude=['ez_setup']),
      package_dir = {'': 'src/main/python'},
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
