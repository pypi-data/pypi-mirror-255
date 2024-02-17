import os.path
import re

from setuptools import find_packages, setup


def read(*parts):
    with open(os.path.join(*parts)) as f:
        return f.read().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*\"([\d.abrc]+)\"")
    init_py = os.path.join(os.path.dirname(__file__), "dayu", "__init__.py")
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError(f"Cannot find version in {init_py}")


classifiers = [
    "License :: OSI Approved :: MIT License",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3 :: Only",
    "Operating System :: POSIX",
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries",
    "Framework :: AsyncIO",
]

setup(
    name="dayu_ratelimit",
    version=read_version(),
    description="ratelimit",
    long_description="\n\n".join((read("README.rst"), read("CHANGELOG.md"))),
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    keywords="aio ratelimit api",
    platforms=["POSIX"],
    url="https://github.com/daleeg/ratelimit",
    license="MIT",
    packages=find_packages(exclude=["docs"]),
    python_requires=">=3.9",
    include_package_data=True,
)
