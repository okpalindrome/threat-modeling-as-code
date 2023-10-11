from setuptools import setup, find_packages

setup(
    name="threatmac",
    version="0.1",
    packages=find_packages(), # treating this project iteself as package by searching __init__.py to indicate the sign of package
    install_requires=[
        "argparse",
        "pyyaml",
        "json"
    ],
    entry_points={"console_scripts": ["threatmac = threatmac.main:main"]},
    author="okpalindrome",
    description="Threat Modeling as Code",
)
