from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A Tool for Scrambling and Unscrambling '
LONG_DESCRIPTION = 'A package that allows to Scramble and Unscramble the Images with different techniques.'

# Setting up
setup(
    name="img_paradox",
    version=VERSION,
    author="1uCif3R",
    author_email="<ctfmail049@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy', 'pillow'],
    keywords=['python', 'Image', 'Encryption', 'Scrambling'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)