from setuptools import setup, find_packages
import os

with open("./facelandmarks/README.md", "r") as f:
    long_description = f.read()

VERSION = '0.1.0'
DESCRIPTION = 'Human face landmarking via machine learning model'
LONG_DESCRIPTION = long_description
REQUIREMENTS_PATH = './facelandmarks/requirements.txt'

def get_requirements(req_path: str):
    with open(req_path, 'r') as f:
        requirements = [req.strip() for req in f.readlines()]
    return requirements

# Setting up
setup(
    name="facelandmarks",
    version=VERSION,
    author="JaroslavTrnka",
    author_email="<jaroslav_trnka@centrum.cz>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=get_requirements(REQUIREMENTS_PATH),
    keywords=['python', 'pytorch', 'face', 'landmarks', 'machine learning'],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)