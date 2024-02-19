from setuptools import setup, find_packages

setup(
    name='sqli-scanner',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'sqli-scanner=sqli_scanner:main',
        ],
    },
     
)
