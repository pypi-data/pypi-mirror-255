from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


# Setting up
setup(
    name='Amino.fixed',
    version='1.0.1',
    description="An API about lib Fix Amino.py",
    author= 'Codex and Arjun',
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires = [
        'schedule',
        'reportlab',
        'argparse'

    ],
    keywords=['python', 'bot','aminobot','theamino'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)