from setuptools import setup, find_packages

setup(
    name="inspectify",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "colored"
    ],
    author="Dimitri Rusin",
    author_email="dimitri@habimm.com",
    description="Print a lot of info about the content of variables",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Habimm/create_trace",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
