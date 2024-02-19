from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Randomized Encryption System'
LONG_DESCRIPTION = 'Randomized Encryption System'

# Setting up
setup(
    name="REScrypt",
    version=VERSION,
    author="HarbingerOfFire",
    author_email="harbingeroffire@proton.me",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'random', 'SXH', 'RES', 'Encryption', 'cryptography']
)
