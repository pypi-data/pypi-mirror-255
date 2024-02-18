import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pginter",
    version="0.2.16",
    author="Nilusink",
    author_email="nilusink@protonmail.com",
    description="A python GUI interface, based on pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nilusink/PgInter",
    # project_urls={
    #     "Official Website": "http://info.fridrich.xyz",
    # },
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.11",
    include_package_data=True,
    install_requires=[
        "setuptools>=60.2.0",
        "pygame>=2.1.2"
    ],
)
