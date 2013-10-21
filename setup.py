from setuptools import setup

VERSION = 0.1


setup(
    name='cerberus',
    version=VERSION,
    description='Sync Gateway workload generator',
    author='Pavel Paulau',
    author_email='pavel.paulau@gmail.com',
    packages=['cerberus'],
    entry_points={
        'console_scripts': ['cerberus = cerberus.main:main']
    },
    install_requires=[
        'logger',
        'requests==2.0.0',
    ]
)
