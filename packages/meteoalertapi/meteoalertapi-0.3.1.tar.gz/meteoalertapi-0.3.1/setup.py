import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="meteoalertapi",
    version="0.3.1",
    author="Rolf Berkenbosch",
    author_email="rolf@berkenbosch.nl",
    description="A small api to get alerting messages from extreme weather in Europe from https://www.meteoalarm.org.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rolfberkenbosch/meteoalert-api",
    install_requires=[
        'xmltodict',
        'requests',
    ],
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
