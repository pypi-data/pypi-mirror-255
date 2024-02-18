import setuptools

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aliceCSV",
    version="0.1.3",
    author="AliceDrop",
    author_email="alicedrop@126.com",
    description="operating csv files as two-dimensional table",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alicedrop/aliceCSV",
    packages=setuptools.find_packages(),
    install_requires=[],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
