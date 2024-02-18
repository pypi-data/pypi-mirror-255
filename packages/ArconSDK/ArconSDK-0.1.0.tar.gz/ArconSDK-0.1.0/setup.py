from setuptools import setup, find_packages

setup(
    name='ArconSDK',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'base64',
        'ipaddress',
        'psutil',
        'requests',
        'pycryptodome',
    ],
    entry_points={
        'console_scripts': [
            'arconsdk-cli=ArconSDK.arcon_sdk:main',
        ],
    },
    author='Anand Vishwakarma',
    author_email='anand.v@arconnet.com',
    description='ArconSDK: A Python package to get PWD ',
    license='MIT',
)
