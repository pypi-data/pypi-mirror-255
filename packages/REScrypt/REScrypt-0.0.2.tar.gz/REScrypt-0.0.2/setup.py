from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Randomized Encryption System'

# Setting up
setup(
    name="REScrypt",
    version=VERSION,
    author="HarbingerOfFire",
    author_email="harbingeroffire@proton.me",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=open("README.MD", "r").read(),
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'random', 'SXH', 'RES', 'Encryption', 'cryptography']
)
