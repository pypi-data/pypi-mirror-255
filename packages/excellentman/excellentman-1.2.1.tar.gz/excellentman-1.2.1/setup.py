import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="excellentman",                     # This is the name of the package
    version="1.2.1",                        
    author="Alec and Lindsay",                     # Full name of the author
    description="A tool for running Newman with parameters from an Excel file",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.8',                # Minimum version requirement of the package
    py_modules=["excellentman"],             # Name of the python package
    package_dir={'':'src'},     # Directory of the source code of the package
    install_requires=['openpyxl'],                     # Install other dependencies if any
    entry_points={
        "console_scripts": [
            "excellentman=excellentman:main",
        ]
    },
)
