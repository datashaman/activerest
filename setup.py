from setuptools import setup
import sys

version = '0.0.1'

setup(name='activerest',
      version=version,
      description='Basic ActiveResource for Python',
      author='Marlin Forbes',
      author_email='marlinf@datashaman.com',
      url='https://github.com/datashaman/activerest/',
      packages=['activerest'],
      license='MIT License',
      install_requires=[
          'requests',
      ],
      tests_require=[
          'requests-mock',
      ],
      test_suite='tests',
      platforms=['any'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.6',
                   'Topic :: Software Development',
                   'Topic :: Software Development :: Libraries',
                   'Topic :: Software Development :: Libraries :: Python Modules']
)
