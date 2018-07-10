from os.path import join, dirname
from setuptools import setup


with open(join(dirname(__file__), 'README.rst')) as file:
    long_description = file.read()

setup(
    name='activerest',
    version='0.0.5',
    description='Python REST resource client, modeled on Ruby on Rails\' ActiveResource.',
    long_description=long_description,
    author='Marlin Forbes',
    author_email='marlinf@datashaman.com',
    url='https://github.com/datashaman/activerest/',
    packages=['activerest'],
    license='MIT License',
    install_requires=[
        'furl',
        'future',
        'inflection',
        'requests',
        'six',
    ],
    tests_require=[
        'coverage',
        'coveralls',
        'pyyaml',
        'requests-mock',
    ],
    test_suite='tests',
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
