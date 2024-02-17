from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pysqlitecrypto-rsa',
    version='0.1.2',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'rsa'
    ],
    entry_points={
        'console_scripts': [
            'pysqlitecrypto-rsa = pysqlitecrypto_rsa.__main__:main'
        ]
    },
    license='GPL-3.0',
    author='hecdelatorre',
    author_email='hector982015@gmail.com',
    description='A package for RSA encryption and decryption using SQLite storage.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='RSA encryption decryption SQLite cryptography',
    url='https://github.com/hecdelatorre/Pysqlitecrypto-RSA.git',
)
