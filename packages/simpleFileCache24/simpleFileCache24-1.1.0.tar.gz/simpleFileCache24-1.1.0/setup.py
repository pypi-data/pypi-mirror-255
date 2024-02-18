from setuptools import setup

setup(
    name='simpleFileCache24',
    version='1.1.0',
    author='zackaryW',
    install_requires=['cryptography', 'keyring', 'requests', 'sioDict>=0.3.2'],
    packages=[
        'simpleFileCache',
        'simpleFileCache.utils',
    ],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown"
)