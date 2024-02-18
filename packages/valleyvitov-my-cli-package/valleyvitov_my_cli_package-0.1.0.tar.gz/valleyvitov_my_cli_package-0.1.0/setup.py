from setuptools import setup, find_packages

setup(
    name='valleyvitov_my_cli_package',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'my_command=my_package.myscript:main'
        ]
    },
    # Additional metadata such as author, description, dependencies, etc.
)