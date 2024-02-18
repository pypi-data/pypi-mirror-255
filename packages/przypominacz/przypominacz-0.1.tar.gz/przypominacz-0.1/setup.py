from setuptools import setup, find_packages

setup(
    name='przypominacz',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
           
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt'],
        'przypominacz.reminder': ['*.py'],
        'przypominacz.config': ['*.ini'],
        'przypominacz.logs': ['*.log'],
    },
)