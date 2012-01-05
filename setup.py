from setuptools import setup

setup(
    name='ulint',
    version='0.1',
    packages=['ulint'],
    entry_points={
        'console_scripts': [ 'ulint = ulint.ulint:main' ],
        }
    )
