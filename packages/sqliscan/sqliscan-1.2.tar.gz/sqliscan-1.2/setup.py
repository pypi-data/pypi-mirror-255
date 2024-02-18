from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='sqliscan',
    version='1.2',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdaseem03/",
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'sqliscan=sqliscan.main:main',
        ],
    },
)
