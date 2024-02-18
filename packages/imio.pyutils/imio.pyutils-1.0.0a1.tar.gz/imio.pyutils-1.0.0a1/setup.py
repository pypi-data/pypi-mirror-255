from setuptools import setup, find_packages

version = '1.0.0a1'

setup(name='imio.pyutils',
      version=version,
      description="Some python useful methods",
      long_description=open("README.rst").read() + "\n" + open('CHANGES.rst').read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.10",
      ],
      keywords='Python IMIO',
      author='IMIO',
      author_email='support@imio.be',
      url="https://github.com/imio/imio.pyutils/",
      project_urls={
          "PyPI": "https://pypi.python.org/pypi/imio.pyutils",
          "Source": "https://github.com/imio/imio.pyutils",
          # "Tracker": (
          #     "https://github.com/collective/dexterity.localroles/issues"
          # ),
      },
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['imio'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'future',
          'six',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
