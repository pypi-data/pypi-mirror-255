from setuptools import setup, find_packages

setup(
    name="nccommons",
    version="0.0.4",
    author="Abhishek Maurya",
    author_email="testmartech1@netcorecloud.com",
    description="This package provides common functions that can be used in API or UI Automation",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/abhishek.maurya/Abhishekkapackage",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
