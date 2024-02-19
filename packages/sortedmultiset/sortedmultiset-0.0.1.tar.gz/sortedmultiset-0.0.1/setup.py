from setuptools import setup, find_packages
import codecs
import os

# here = os.path.abspath(os.path.dirname(__file__))
#
# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'A sorted multiset can store multiple values in sorted order unlike a normal set'
LONG_DESCRIPTION = 'A sorted multiset can store multiple values in sorted order unlike a normal set'

# Setting up
setup(
    name="multiset",
    version=VERSION,
    author="Rushikesh Sunil Kotkar",
    author_email="<rshksh019@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'multiset'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        # "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)