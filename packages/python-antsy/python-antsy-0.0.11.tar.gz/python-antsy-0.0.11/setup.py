from setuptools import setup, find_packages

__version__ = "0.0.11"

setup(
    name="python-antsy",
    packages=find_packages(exclude=["tests", "tests.*"]),
    version=__version__,
    description="Antsy API Client",
    long_description=open("README.md").read().strip(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="Juan F. Duque",
    author_email="jfelipe@grupodyd.com",
    include_package_data=True,
    url="https://www.grupodyd.com",
    project_urls={
        "Source": "https://github.com/grupodyd/python-antsy",
        "Tracker": "https://github.com/grupodyd/python-antsy/issues",
    },
    keywords="antsy",
    python_requires=">=3.9.0",
    install_requires=[
        "httpx[http2] >= 0.26.0, < 1",
        "pydantic >= 2, < 3",
        "python-dateutil >= 2.8.2, < 3",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
