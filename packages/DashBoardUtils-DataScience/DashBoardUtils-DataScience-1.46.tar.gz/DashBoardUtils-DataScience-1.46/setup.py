from setuptools import setup, find_packages

long_description = open("README.md", "rb").read().decode()

setup(
    name="DashBoardUtils-DataScience",
    version="1.46",
    author="Rajat Mishra",
    author_email="rajatsmishra@aol.com",
    description="AutoMated visualization Features Extraction For Data Scientists and data format calculater for application developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["pandas", "bokeh"],
)
