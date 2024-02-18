import io
import sys
from glob import glob

from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


requirements = ["pyperclip", "tabulate", "click"]  # TODO: add requirements (do I want to leverage gitpython?)

# TODO: add test requirements

# upload to pypi:
#   python setup.py sdist bdist_wheel
#   python -m twine upload dist/*

setup(
    name="aeratable",
    version="0.1.0",    
    author="Timo Lesterhuis",
    author_email="timolesterhuis@gmail.com",
    description="Nicely format Aera interface-output to a table in ASCII or CSV format.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/timolesterhuis/jrnlsync/",
    project_urls={
        # 'Documentation': 'https://jrnlsync.readthedocs.io/',
        #'Changelog': 'https://python-nameless.readthedocs.io/en/latest/changelog.html',
        "Source": "https://github.com/timolesterhuis/aeratable",
        'Issue Tracker': 'https://github.com/timolesterhuis/aeratable/issues',
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aeratable = aeratable.cli:main",
        ]
    },
    tests_require=["pytest", "pytest-cov"],
    cmdclass={"pytest": PyTest},
    license="MIT License",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)